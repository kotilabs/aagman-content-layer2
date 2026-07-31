"""generic_harness.py — the domain-agnostic loop.

SENSE -> IDEATE -> CREATE -> JUDGE -> PUBLISH, with LEARN always. Per step: run the
agent, run the step's gates, and on a fixable block retry (revise) up to the step's
loop_limit; on escalate / exhaustion park the item (awaiting_gate:<name>); on a
non-fixable block reject. Dedup at sense; kill switch + budget pause checked between
every unit of work; parallel CREATE fans out via threads. Nothing domain-specific
lives here — domains supply agents + gates through a DomainConfig.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness_core.agent_base import Artifact, Idea, Signal
from harness_core.loop_controller import LoopController

_PIPELINE = ["ideate", "create", "judge", "publish"]
_STATUS = {"ideate": "ideating", "create": "creating",
           "judge": "judging", "publish": "publishing"}
# Outcomes that carry a real quality signal for self-evolution scoring. Parked
# (escalate), unfinished (incomplete) and infra-failed (failed) cycles are NOT the
# relied lessons' fault, so they never credit or blame.
_ATTRIBUTABLE = frozenset({"published", "rejected"})


class GenericHarness:
    def __init__(self, config, store, kill_switch=None, budget=None,
                 memory_factory=None, workdir=None, dry_run=False, prioritizer=None):
        self.config = config
        self.store = store
        self.kill_switch = kill_switch
        self.budget = budget
        self.memory_factory = memory_factory
        self.workdir = Path(workdir) if workdir else Path(".")
        self.dry_run = dry_run
        # Optional domain-supplied callable(list[work_item]) -> list[work_item] that
        # reorders and may subset the open queue before the pipeline runs (budget-fitted
        # prioritization). Domain-free here: dropped items simply stay open for next run.
        self.prioritizer = prioritizer
        self.loop = LoopController()

    # -- top level -------------------------------------------------------- #
    def run_once(self, sources):
        if self._stopped():
            return
        sense = self.config.step("sense")
        signals = sense.agent.sense(sources) if sense else []
        for sig in signals:
            if self._stopped():
                return
            if not self.store.is_duplicate(sig.fingerprint):
                self.store.create(sig)
        items = self.store.open_items()
        if self.prioritizer is not None:
            items = self.prioritizer(items)
        for wi in items:
            if self._stopped():
                return
            self.run_item(wi)

    def _stopped(self) -> bool:
        if self.kill_switch is not None and self.kill_switch.is_killed():
            return True
        if self.budget is not None and self.budget.is_paused():
            return True
        return False

    # -- per item --------------------------------------------------------- #
    def run_item(self, wi):
        signal = self._signal_of(wi)
        ctx = {"signal": signal, "idea": None, "artifact": None,
               "outcome": "incomplete"}
        try:
            for step in _PIPELINE:
                if self._stopped():
                    return
                cfg = self.config.step(step)
                if cfg is None:
                    continue
                self.store.update(wi.id, current_step=step, status=_STATUS[step])
                verdict = getattr(self, f"_step_{step}")(wi, cfg, ctx)
                if verdict != "advance":
                    ctx["outcome"] = verdict
                    return
            self.store.update(wi.id, status="published")
            ctx["outcome"] = "published"
        except Exception as e:
            # Fault containment: an unexpected agent failure (e.g. every model in
            # a chain errors) must not crash the loop or the other items. Mark THIS
            # item failed, audit the reason (never silent), and move on. KILL/budget
            # use _stopped() (bool), not exceptions, so they still halt the loop.
            ctx["outcome"] = "failed"
            self.store.update(wi.id, status="failed")
            self.store.audit(wi.id, "error", "failed", issues=[str(e)[:300]])
        finally:
            self._learn(signal, ctx)

    # -- steps ------------------------------------------------------------ #
    def _step_ideate(self, wi, cfg, ctx):
        ctx["idea"] = cfg.agent.ideate(ctx["signal"])
        return self._gate_loop(wi, cfg, revise=None, payload=lambda: ctx["idea"].summary)

    def _step_create(self, wi, cfg, ctx):
        if cfg.mode == "parallel" and cfg.fan_out:
            parts = self._fan_out_create(cfg, ctx["idea"])
            ctx["artifact"] = Artifact(
                body="\n".join(a.body for a in parts),
                kind="multi", meta={"parts": [a.kind for a in parts]})
        else:
            ctx["artifact"] = cfg.agent.create(ctx["idea"])

        def revise(issues):
            ctx["artifact"] = cfg.agent.revise(ctx["artifact"], issues)

        return self._gate_loop(wi, cfg, revise=revise,
                               payload=lambda: ctx["artifact"].body)

    def _step_judge(self, wi, cfg, ctx):
        counts = self._counts(wi)
        create_cfg = self.config.step("create")
        while True:
            if self._stopped():
                return "parked"
            v = cfg.agent.judge(ctx["artifact"], self.memory_factory)
            self.store.audit(wi.id, "judge", v.verdict, issues=v.issues)
            if v.verdict == "pass":
                ctx["verdict"] = v          # carry judge provenance to _learn scoring
                return self._gate_loop(wi, cfg, revise=None,
                                       payload=lambda: ctx["artifact"].body)
            if v.verdict == "escalate":
                self._park(wi, "judge")
                return "parked"
            # block -> adversarial bounce back to create.revise
            if not self.loop.should_retry(counts, "judge", cfg.loop_limit):
                self._park(wi, "judge")
                return "parked"
            counts = self.loop.record(counts, "judge")
            self.store.update(wi.id, loop_counts_json=json.dumps(counts))
            if create_cfg is not None:
                ctx["artifact"] = create_cfg.agent.revise(ctx["artifact"], v.issues)

    def _step_publish(self, wi, cfg, ctx):
        if self.dry_run:
            self.store.update(wi.id, status="awaiting_publish")
            return "dry_run"
        gate_verdict = self._gate_loop(wi, cfg, revise=None,
                                       payload=lambda: ctx["artifact"].body)
        if gate_verdict != "advance":
            return gate_verdict
        cfg.agent.publish(ctx["artifact"], ctx.get("channels", []))
        return "advance"

    # -- gate engine ------------------------------------------------------ #
    def _gate_loop(self, wi, cfg, revise, payload):
        counts = self._counts(wi)
        while True:
            if self._stopped():
                return "parked"
            gres, gate = self._check_gates(cfg, payload(), wi)
            if gres is None or gres.verdict == "pass":
                return "advance"
            gname = getattr(gate, "gate_name", cfg.step)
            self.store.audit(wi.id, gname, gres.verdict,
                             rules_version=getattr(gate, "rules_version", ""),
                             issues=gres.issues)
            if gres.verdict == "escalate":
                self._park(wi, gname)
                return "parked"
            if not gres.fixable:
                self.store.update(wi.id, status="rejected")
                return "rejected"
            if revise is None:  # no repair path -> park for a human
                self._park(wi, gname)
                return "parked"
            if not self.loop.should_retry(counts, cfg.step, cfg.loop_limit):
                self._park(wi, gname)
                return "parked"
            counts = self.loop.record(counts, cfg.step)
            self.store.update(wi.id, loop_counts_json=json.dumps(counts))
            revise(gres.issues)

    def _check_gates(self, cfg, payload_text, wi):
        for i, gate in enumerate(cfg.gates):
            gname = getattr(gate, "gate_name", f"{cfg.step}_{i}")
            gate_dir = str(self.workdir / "gates" / wi.id / gname)
            res = gate.check(payload_text, {"work_item": wi, "gate_dir": gate_dir})
            if res.verdict != "pass":
                return res, gate
        return None, None

    def _fan_out_create(self, cfg, idea):
        def one(item):
            sub = Idea(summary=idea.summary, plan=dict(idea.plan),
                       confidence=idea.confidence,
                       meta={**idea.meta, "fan_out": item})
            return cfg.agent.create(sub)

        with ThreadPoolExecutor(max_workers=min(4, len(cfg.fan_out))) as ex:
            return list(ex.map(one, cfg.fan_out))

    # -- helpers ---------------------------------------------------------- #
    def _park(self, wi, gate_name):
        self.store.update(wi.id, status=f"awaiting_gate:{gate_name}")

    def _counts(self, wi):
        return json.loads(self.store.get(wi.id).loop_counts_json or "{}")

    def _signal_of(self, wi):
        return Signal(id=wi.id, domain=wi.domain, source="",
                      payload=json.loads(wi.signal_json or "{}"),
                      fingerprint=wi.fingerprint)

    def _learn(self, signal, ctx):
        lc = self.config.step("learn")
        if lc is not None:
            lc.agent.record(signal, ctx["idea"], ctx["artifact"], ctx["outcome"])
        self._attribute(ctx)

    def _attribute(self, ctx):
        """Self-evolution: credit/blame the lessons this cycle relied on, by terminal
        outcome, so proven lessons surface in top_k and misleading ones sink. Generic —
        domains stamp idea/artifact meta['relied']=[[domain,step,id], ...]; here we just
        honour that provenance. No domain logic."""
        if self.memory_factory is None or ctx.get("outcome") not in _ATTRIBUTABLE:
            return
        by_ns = {}
        for obj in (ctx.get("idea"), ctx.get("artifact"), ctx.get("verdict")):
            for entry in (getattr(obj, "meta", {}) or {}).get("relied", []) or []:
                if isinstance(entry, (list, tuple)) and len(entry) == 3:
                    by_ns.setdefault((entry[0], entry[1]), set()).add(entry[2])
        for (domain, step), ids in by_ns.items():
            self.memory_factory(domain, step).attribute(list(ids), ctx["outcome"])
