"""Phase-1 TDD: generic_harness.py — the domain-agnostic loop.

Fakes implement the ABCs; the tests assert ORCHESTRATION, not any domain: full
loop to published, dedup at sense, fixable-retry via revise, escalate-parks,
loop-limit exhaustion parks (never infinite), non-fixable block rejects, kill
switch stops, dry-run skips publish, and parallel fan-out calls create per item.
"""
import threading

from harness_core.agent_base import (
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
    Signal, Idea, Artifact, Verdict, Receipt,
)
from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.gates import GateResult
from harness_core.state import WorkItemStore
from harness_core.kill_switch import KillSwitch
from harness_core.generic_harness import GenericHarness


# ----------------------------- fake agents -------------------------------- #
class FakeSense(SenseAgent):
    def __init__(self, signals):
        self._signals = signals

    def sense(self, sources):
        return list(self._signals)


class FakeIdeate(IdeateAgent):
    def __init__(self):
        self.calls = 0

    def ideate(self, signal):
        self.calls += 1
        return Idea(summary=f"idea:{signal.id}")


class FakeCreate(CreateAgent):
    def __init__(self):
        self.create_calls = 0
        self.revise_calls = 0
        self._lock = threading.Lock()

    def create(self, idea):
        with self._lock:
            self.create_calls += 1
        return Artifact(body="draft", kind=(idea.meta.get("fan_out") or "text"))

    def revise(self, artifact, issues):
        with self._lock:
            self.revise_calls += 1
        return Artifact(body="revised", kind=artifact.kind)


class FakeJudge(JudgeAgent):
    def __init__(self, block_times=0):
        self.calls = 0
        self.block_times = block_times

    def judge(self, artifact, panel):
        self.calls += 1
        if self.calls <= self.block_times:
            return Verdict(verdict="block", issues=["weak"])
        return Verdict(verdict="pass")


class FakePublish(PublishAgent):
    def __init__(self):
        self.calls = 0

    def publish(self, artifact, channels):
        self.calls += 1
        return Receipt(channel="outbox", ref="r1")


class FakeLearn(LearnAgent):
    def __init__(self):
        self.records = []

    def record(self, signal, idea, artifact, outcome):
        self.records.append(outcome)


# ------------------------------- fake gates ------------------------------- #
class PassGate:
    def check(self, payload, ctx=None):
        return GateResult(verdict="pass")


class BlockOnceGate:
    def __init__(self):
        self.n = 0

    def check(self, payload, ctx=None):
        self.n += 1
        if self.n > 1:
            return GateResult(verdict="pass")
        return GateResult(verdict="block", issues=["fix me"], fixable=True)


class AlwaysBlockGate:
    def check(self, payload, ctx=None):
        return GateResult(verdict="block", issues=["nope"], fixable=True)


class NonFixableBlockGate:
    def check(self, payload, ctx=None):
        return GateResult(verdict="block", issues=["hard no"], fixable=False)


class EscalateGate:
    gate_name = "review"

    def check(self, payload, ctx=None):
        return GateResult(verdict="escalate", issues=["human needed"])


# ------------------------------- helpers ---------------------------------- #
def _cfg(sense, ideate, create, judge, publish, learn,
         create_gates=None, create_mode="serial", create_fan_out=None):
    return DomainConfig(name="test", steps=[
        StepConfig(step="sense", agent=sense),
        StepConfig(step="ideate", agent=ideate),
        StepConfig(step="create", agent=create, mode=create_mode,
                   fan_out=create_fan_out or [], gates=create_gates or [],
                   loop_limit=2),
        StepConfig(step="judge", agent=judge, loop_limit=2),
        StepConfig(step="publish", agent=publish),
        StepConfig(step="learn", agent=learn),
    ])


def _agents():
    return (FakeIdeate(), FakeCreate(), FakeJudge(), FakePublish(), FakeLearn())


def _harness(tmp_path, cfg, **kw):
    store = WorkItemStore(str(tmp_path / "s.db"))
    return GenericHarness(cfg, store, workdir=str(tmp_path), **kw), store


def _sig(sid="c-1", payload=None):
    return Signal(id=sid, domain="test", source="inbox", payload=payload or {})


# -------------------------------- tests ----------------------------------- #
def test_happy_path_runs_full_loop_to_published(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea)
    h, store = _harness(tmp_path, cfg)
    h.run_once(sources=["inbox"])
    wi = store.get("c-1")
    assert wi.status == "published"
    assert (ide.calls, cre.create_calls, jud.calls, pub.calls) == (1, 1, 1, 1)
    assert lea.records == ["published"]


def test_dedup_skips_same_fingerprint(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    a = _sig("c-1", {"a": 1})
    b = _sig("c-2", {"a": 1})  # different id, SAME fingerprint
    cfg = _cfg(FakeSense([a, b]), ide, cre, jud, pub, lea)
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    assert store.get("c-1") is not None
    assert store.get("c-2") is None  # deduped


def test_fixable_block_triggers_revise_then_advances(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea,
               create_gates=[BlockOnceGate()])
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    assert cre.create_calls == 1
    assert cre.revise_calls == 1
    assert store.get("c-1").status == "published"


def test_escalate_gate_parks_item_and_still_learns(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea,
               create_gates=[EscalateGate()])
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    wi = store.get("c-1")
    assert wi.status.startswith("awaiting_gate")
    assert pub.calls == 0
    assert lea.records  # LEARN always


def test_loop_limit_exhaustion_parks_not_infinite(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea,
               create_gates=[AlwaysBlockGate()])
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    wi = store.get("c-1")
    assert wi.status.startswith("awaiting_gate")
    assert cre.revise_calls == 2  # loop_limit, then park
    assert pub.calls == 0


def test_non_fixable_block_rejects(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea,
               create_gates=[NonFixableBlockGate()])
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    assert store.get("c-1").status == "rejected"
    assert pub.calls == 0


def test_judge_block_bounces_to_revise_then_passes(tmp_path):
    ide, cre, pub, lea = FakeIdeate(), FakeCreate(), FakePublish(), FakeLearn()
    jud = FakeJudge(block_times=1)  # blocks once, then passes
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea)
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    assert jud.calls == 2
    assert cre.revise_calls == 1  # judge bounce revised the artifact
    assert store.get("c-1").status == "published"


def test_kill_switch_stops_before_creating_items(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea)
    ks = KillSwitch(str(tmp_path / "KILL"))
    ks.arm()
    h, store = _harness(tmp_path, cfg, kill_switch=ks)
    h.run_once(["inbox"])
    assert store.get("c-1") is None
    assert ide.calls == 0


def test_dry_run_parks_at_awaiting_publish_without_publishing(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea)
    h, store = _harness(tmp_path, cfg, dry_run=True)
    h.run_once(["inbox"])
    wi = store.get("c-1")
    assert wi.status == "awaiting_publish"
    assert pub.calls == 0
    assert lea.records  # learn still runs


def test_parallel_fan_out_creates_per_item(tmp_path):
    ide, cre, jud, pub, lea = _agents()
    cfg = _cfg(FakeSense([_sig()]), ide, cre, jud, pub, lea,
               create_mode="parallel", create_fan_out=["text", "image"])
    h, store = _harness(tmp_path, cfg)
    h.run_once(["inbox"])
    assert cre.create_calls == 2  # one per fan_out item
    assert store.get("c-1").status == "published"


# ---------------- per-item exception isolation (fault containment) --------- #
class RaisingIdeate(IdeateAgent):
    def ideate(self, signal):
        raise RuntimeError("all models failed (auth)")


def test_run_item_isolates_agent_exception_and_marks_failed(tmp_path):
    sig = Signal(id="x1", domain="test", source="s", payload={})
    cfg = _cfg(FakeSense([sig]), RaisingIdeate(), FakeCreate(), FakeJudge(),
              FakePublish(), FakeLearn())
    h, store = _harness(tmp_path, cfg)
    h.run_once([])  # a raising agent must NOT crash the loop
    assert store.get("x1").status == "failed"


def test_failed_item_is_audited_and_learn_still_runs(tmp_path):
    sig = Signal(id="x1", domain="test", source="s", payload={})
    learn = FakeLearn()
    cfg = _cfg(FakeSense([sig]), RaisingIdeate(), FakeCreate(), FakeJudge(),
              FakePublish(), learn)
    h, store = _harness(tmp_path, cfg)
    h.run_once([])
    assert learn.records == ["failed"]  # LEARN records the failed outcome
    assert any(a["gate_name"] == "error" for a in store.audits("x1"))


def test_run_once_continues_after_one_item_fails(tmp_path):
    class SelectiveIdeate(IdeateAgent):
        def ideate(self, signal):
            if signal.id == "bad":
                raise RuntimeError("boom")
            return Idea(summary="ok")
    bad = Signal(id="bad", domain="test", source="s", payload={"k": 2})
    good = Signal(id="ok", domain="test", source="s", payload={"k": 1})
    cfg = _cfg(FakeSense([bad, good]), SelectiveIdeate(), FakeCreate(),
              FakeJudge(), FakePublish(), FakeLearn())
    h, store = _harness(tmp_path, cfg)
    h.run_once([])
    assert store.get("bad").status == "failed"
    assert store.get("ok").status == "published"  # sibling still processed
