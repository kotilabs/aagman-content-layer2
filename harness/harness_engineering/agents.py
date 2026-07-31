"""harness_engineering/agents.py — the ENGINEERING (bug-fix) domain agents.

Wraps the aagman-v2 fix pipeline into the six ABCs. External effects are
injected (fetch_fn for gh issues, runner_fn for the Claude Code subprocess,
pr_fn for PR creation) so the agents are testable offline and so the ACTUAL
side-effecting commands live in one visible place. The four engineering laws
(from RISK_RULES.md) and the distilled layer/file/objection knowledge are loaded
into the RCA and review prompts — this is where Day-0 distillation pays off.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from harness_core.agent_base import (
    Artifact, Idea, Receipt, Signal, Verdict,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.judgment_panel import JudgmentPanel

REPO = "kotilabs/aagman-v2"
ASSIGNEE = "ajitk2003"
PR_ASSIGNEE = "amit-kotidev"
BRANCH_PREFIX = "ajit/fix-"

# Recurrence -> architectural-review escalation. An area fixed this many times
# (total), or bounced/reopened this many times (adverse — stronger signal), stops
# earning silent patch N+1 and instead flags the plan for a design review.
RECURRENCE_THRESHOLD = 3
RECURRENCE_ADVERSE_THRESHOLD = 2
_ADVERSE_OUTCOMES = ("failed", "rejected")

# Retrieval pre-route neighbours. On the deduped 96-issue 4-fold CV, k in {1,2,3,5}
# are all within ~2pp (noise); k=1 is simplest and marginally best — 36.5% CV vs 26%
# majority-class, 0% keyword (leakage-free). Re-tune when the index grows.
ROUTE_K = 1


def _area_of(entry_file: str, layer: str = "") -> str:
    """A stable, coarse recurrence key. The first two path segments match the
    curated file_relationships area naming (e.g. 'backtester/packages'); with no
    file, fall back to the layer, then 'unknown'."""
    if entry_file:
        return "/".join(entry_file.split("/")[:2])
    return layer or "unknown"


def _layer_of(entry_file: str) -> str:
    """Infer the layer from a routed file's extension (retrieval gives a file, not
    a layer label)."""
    f = (entry_file or "").lower()
    if f.endswith((".ts", ".tsx")):
        return "typescript"
    if f.endswith(".py"):
        return "python"
    return ""


def _recurrence_stats(memory_factory, area: str) -> dict:
    """Count prior fix outcomes logged for `area` in the engineering/fixlog store."""
    if not memory_factory or not area or area == "unknown":
        return {"total": 0, "adverse": 0, "area": area}
    total = adverse = 0
    for les in memory_factory("engineering", "fixlog").all():
        if les.tags != area:
            continue
        total += 1
        if any(f"outcome={o}" in les.text for o in _ADVERSE_OUTCOMES):
            adverse += 1
    return {"total": total, "adverse": adverse, "area": area}


def _load_json(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError, TypeError):
        return default


def _read(path):
    try:
        return Path(path).read_text()
    except (OSError, TypeError):
        return ""


def _lesson_texts(mem, query, k=5):
    out = []
    for lid in mem.top_k(query, k=k):
        les = mem.get(lid)
        if les and les.text:
            out.append(les.text)
    return out


def _recall(memory_factory, domain, step, query, k=5):
    """Recall top-k lesson TEXTS and their PROVENANCE. relied = [[domain, step, id], ...]
    is stamped onto idea/artifact meta so the harness can credit/blame exactly the
    lessons a cycle relied on (self-evolution scoring)."""
    if not memory_factory:
        return [], []
    mem = memory_factory(domain, step)
    texts, relied = [], []
    for lid in mem.top_k(query, k=k):
        les = mem.get(lid)
        if les and les.text:
            texts.append(les.text)
            relied.append([domain, step, lid])
    return texts, relied


# --------------------------------------------------------------------------- #
# SENSE — poll GitHub issues assigned to ajitk2003
# --------------------------------------------------------------------------- #
class IssueListener(SenseAgent):
    def __init__(self, repo=REPO, assignee=ASSIGNEE, fetch_fn=None):
        self.repo = repo
        self.assignee = assignee
        self.fetch_fn = fetch_fn or self._gh_fetch

    def sense(self, sources=None) -> list:
        signals = []
        for i in self.fetch_fn(self.repo, self.assignee) or []:
            labels = [l["name"] if isinstance(l, dict) else l
                      for l in i.get("labels", [])]
            signals.append(Signal(
                id=f"eng:{i['number']}", domain="engineering", source="github",
                payload={"number": i["number"], "title": i.get("title", ""),
                         "body": i.get("body", ""), "labels": labels}))
        return signals

    @staticmethod
    def _gh_fetch(repo, assignee):
        out = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--assignee", assignee,
             "--state", "open", "--json", "number,title,body,labels", "--limit", "50"],
            capture_output=True, text=True, check=True)
        return json.loads(out.stdout or "[]")


# --------------------------------------------------------------------------- #
# IDEATE — RCA: four laws + layer routing + file relationships + second pass
# --------------------------------------------------------------------------- #
class RCAAgent(IdeateAgent):
    def __init__(self, router, memory_factory, layer_gt_path, file_rel_path,
                 risk_rules_path, panel=None, route_index_path=None):
        self.router = router
        self.memory_factory = memory_factory
        self.layer_gt = _load_json(layer_gt_path, [])
        self.file_rel = _load_json(file_rel_path, {})
        self.risk_rules = _read(risk_rules_path)
        self.panel = panel or JudgmentPanel(router, "rca_panel")
        # retrieval router (issue -> area/file); measured ~15x the keyword route.
        from harness_engineering.route_index import RouteIndex
        self.route_index = RouteIndex.load(route_index_path) if route_index_path else None

    def ideate(self, signal) -> Idea:
        title = signal.payload.get("title", "")
        body = signal.payload.get("body", "")
        # Pre-route prior: retrieval (nn over past issues) first — it routes ~15x
        # more issues than the 4 keyword symptoms — then keyword as fallback. The
        # model is still asked to STATE the real layer/entry file, trusted when given.
        ri_area, ri_entry = (self.route_index.predict(f"{title} {body}", k=ROUTE_K)
                             if self.route_index else ("", ""))
        kw_layer, kw_entry = self._route_layer(f"{title}\n{body}")
        pre_entry = ri_entry or kw_entry
        pre_layer = _layer_of(pre_entry) or kw_layer
        pre_area = _area_of(pre_entry, pre_layer)
        if pre_area == "unknown" and ri_area:
            pre_area = ri_area
        pre_rec = _recurrence_stats(self.memory_factory, pre_area)
        pre_arch = (pre_rec["total"] >= RECURRENCE_THRESHOLD
                    or pre_rec["adverse"] >= RECURRENCE_ADVERSE_THRESHOLD)
        similar, r_sense = _recall(self.memory_factory, "engineering", "sense",
                                   f"{title} {body}")
        lessons, r_ideate = _recall(self.memory_factory, "engineering", "ideate",
                                    f"{title} {body}")
        prompt = self._prompt(title, body, pre_layer, pre_entry, lessons,
                              pre_rec if pre_arch else None, similar)
        res = self.router.complete("complex_planning", prompt,
                                   domain="engineering", step="ideate")
        text = res["text"].strip()
        confidence = self._confidence(text)
        if confidence < 0.7:  # law-c rigor: a shaky RCA gets a second, harder pass
            res = self.router.complete(
                "complex_planning",
                "Your first RCA was low-confidence. Redo it MORE rigorously: every "
                "conclusion DATA/CODE/TEST-backed (no 'probably'). \n\n" + prompt,
                domain="engineering", step="ideate")
            text = res["text"].strip()
            confidence = max(confidence, self._confidence(text))
        # Final route preference: model-STATED > retrieval/keyword pre-route. Derive
        # layer from the RESOLVED entry file first so it can't disagree with it (a live
        # run showed '**bold**' markdown defeating the layer parse -> stale layer).
        p_layer, p_entry = self._parse_route(text)
        entry_file = p_entry or pre_entry
        layer = _layer_of(entry_file) or p_layer or pre_layer
        area = _area_of(entry_file, layer)
        rec = _recurrence_stats(self.memory_factory, area)
        arch_review = (rec["total"] >= RECURRENCE_THRESHOLD
                       or rec["adverse"] >= RECURRENCE_ADVERSE_THRESHOLD)
        if arch_review:
            text = (f"⚠️ ARCHITECTURAL REVIEW RECOMMENDED — area '{area}' has "
                    f"{rec['total']} prior fixes ({rec['adverse']} reopened/bounced). "
                    f"This issue is likely a variation of a recurring problem; weigh a "
                    f"design review over another patch.\n\n" + text)
        return Idea(summary=text,
                    plan={"layer": layer, "entry_file": entry_file, "area": area,
                          "recurrence": rec, "architectural_review": arch_review,
                          "issue": signal.payload},
                    confidence=confidence,
                    meta={"model": res.get("model", ""), "relied": r_sense + r_ideate})

    def _prompt(self, title, body, layer, entry_file, lessons, recurrence=None,
                similar=None):
        laws = self.risk_rules or "(risk rules unavailable)"
        gt = "\n".join(f"- {e.get('symptom','')[:80]} -> {e.get('layer','')} @ "
                       f"{e.get('entry_file','')}" for e in self.layer_gt[:12])
        recur = ""
        if recurrence:
            recur = (f"RECURRENCE: area '{recurrence['area']}' has {recurrence['total']} "
                     f"prior fixes ({recurrence['adverse']} reopened/bounced). This is "
                     f"likely a recurring problem — evaluate whether a ROOT architectural "
                     f"change is warranted over another patch, and say so explicitly.\n\n")
        sim = ("SIMILAR PAST ISSUES (real, from this repo — use to classify & route):\n"
               + "\n".join(f"- {t}" for t in similar) + "\n\n") if similar else ""
        return (
            "Root-cause this aagman-v2 issue. Obey these laws verbatim:\n"
            f"{laws}\n\n"
            "LAYER GROUND TRUTH (symptom -> layer -> entry file):\n" + gt + "\n\n"
            + recur + sim
            + ("PAST LESSONS:\n" + "\n".join(f"- {t}" for t in lessons) + "\n\n"
               if lessons else "")
            + f"ROUTE HINT (retrieval/keyword prior): {layer} (entry: {entry_file})\n\n"
            f"ISSUE TITLE: {title}\nISSUE BODY: {body}\n\n"
            "Output a PLAN. State the route as two exact lines — 'LAYER: <layer>' and "
            "'ENTRY_FILE: <path>' — then the root cause with EVIDENCE (data/code/test), "
            "atomic fix tasks, and 'confidence: <0-1>'."
        )

    def _route_layer(self, text):
        low = text.lower()
        for e in self.layer_gt:
            symptom = str(e.get("symptom", "")).lower()
            keys = [t for t in ("risk_blocked", "strategy_blocked", "rule 6",
                                "rule 6.x") if t in symptom]
            if any(k in low for k in keys):
                return e.get("layer", ""), e.get("entry_file", "")
        return "", ""

    @staticmethod
    def _parse_route(text):
        """Extract an LLM-stated LAYER/ENTRY_FILE from the RCA output. Returns
        ('', '') where absent or implausible (so the keyword route wins)."""
        import re
        layer = entry = ""
        m = re.search(r"entry[_ ]?file\s*[:=][ \t]*([^\n]+)", text, re.I)
        if m:
            cand = m.group(1).strip().strip("`*'\" ")
            cand = cand.split()[0].strip("`*'\"") if cand else ""
            if "/" in cand and not cand.startswith("(") and len(cand) > 3:
                entry = cand
        m = re.search(r"\blayer\s*[:=][ \t]*`?([A-Za-z][\w\- ]*?)`?\s*(?:\n|$)", text, re.I)
        if m:
            layer = m.group(1).strip().strip("`*'\"")
        return layer, entry

    @staticmethod
    def _confidence(text):
        low = text.lower()
        import re
        m = re.search(r"confidence[:=\s]+([01](?:\.\d+)?)", low)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return 0.8  # no explicit signal -> assume workable


# --------------------------------------------------------------------------- #
# CREATE — Claude Code subprocess (test-first); serial; injectable runner
# --------------------------------------------------------------------------- #
def _parse_claude_json(out):
    """Parse `claude -p --output-format json` -> (result_text, usage|None), where
    usage = {tokens, cost_usd}. Non-JSON output passes through as (text, None)."""
    out = (out or "").strip()
    if not out:
        return "", None
    try:
        obj = json.loads(out)
    except Exception:
        return out, None
    if isinstance(obj, list):                       # stream-json: last result object
        results = [o for o in obj if isinstance(o, dict) and o.get("type") == "result"]
        obj = results[-1] if results else (obj[-1] if obj else {})
    if not isinstance(obj, dict):
        return out, None
    text = obj.get("result") or obj.get("text") or ""
    usage = obj.get("usage") or {}
    tokens = sum(v for k, v in usage.items()
                 if k.endswith("tokens") and isinstance(v, (int, float)))
    cost = obj.get("total_cost_usd", obj.get("cost_usd", 0.0)) or 0.0
    text = text if isinstance(text, str) else str(text)
    return text.strip(), {"tokens": int(tokens), "cost_usd": float(cost)}


class CodeFixAgent(CreateAgent):
    def __init__(self, runner_fn=None, workdir=".", router=None,
                 memory_factory=None, file_rel=None):
        self.runner_fn = runner_fn or self._claude_code
        self.workdir = str(workdir)
        self.router = router
        self.memory_factory = memory_factory
        self.file_rel = _load_json(file_rel, {}) if file_rel else {}
        self._area = ""

    def create(self, idea) -> Artifact:
        issue = idea.plan.get("issue", {}) if isinstance(idea.plan, dict) else {}
        num = issue.get("number", "x")
        entry_file = idea.plan.get("entry_file", "") if isinstance(idea.plan, dict) else ""
        # Day-0 distillation pays off HERE: recall how similar bugs actually landed
        # (fix_success_patterns) and the files that historically change with the
        # entry file (co-change) so the fixer weighs sibling breakage up front.
        patterns, r_create = _recall(self.memory_factory, "engineering", "create",
                                     f"{issue.get('title','')} {idea.summary}")
        siblings = self._cochange(entry_file)
        task = (
            "Fix this aagman-v2 issue with STRICT TDD (law d): FIRST write a "
            "regression test that reproduces the bug and MUST FAIL before the fix; "
            "if it passes pre-fix, STOP — the layer is wrong. Then make the minimal "
            "fix so it passes. Add the test under regression-testing/{area}/ and "
            "update that area's README table.\n\n"
            f"LAYER: {idea.plan.get('layer','')}  ENTRY: {entry_file}\n"
            f"RCA / PLAN:\n{idea.summary}\n"
            + (("\nSIMILAR FIXES THAT LANDED (approach | merged_first_try — mirror what "
                "held up, avoid what bounced):\n" + "\n".join(f"- {t}" for t in patterns))
               if patterns else "")
            + (("\nCO-CHANGE — files that historically change WITH the entry file; check "
                "each for sibling breakage and update tests if touched:\n"
                + "\n".join(f"- {s}" for s in siblings)) if siblings else "")
        )
        self._area = "/".join(entry_file.split("/")[:2]) if entry_file else ""
        summary = self.runner_fn(task, self.workdir)
        prior = (idea.meta.get("relied", []) if isinstance(getattr(idea, "meta", None), dict)
                 else [])
        return Artifact(body=summary, kind="patch",
                        meta={"issue_number": num, "layer": idea.plan.get("layer", ""),
                              "relied": prior + r_create})

    def _cochange(self, entry_file, k=8):
        if not entry_file or not isinstance(self.file_rel, dict):
            return []
        sib = set()
        for pair in self.file_rel.get("co_change", []):
            if isinstance(pair, list) and entry_file in pair:
                sib.update(x for x in pair if x != entry_file)
        return sorted(sib)[:k]

    def revise(self, artifact, issues) -> Artifact:
        task = (
            "Revise the fix to address the reviewer's objections, keeping the "
            "test-first discipline (the regression test must still fail before / "
            "pass after).\n\nOBJECTIONS:\n" + "\n".join(f"- {i}" for i in issues)
            + f"\n\nCURRENT FIX:\n{artifact.body}\n"
        )
        summary = self.runner_fn(task, self.workdir)
        return Artifact(body=summary, kind="patch",
                        meta={**artifact.meta, "revised": True})

    def _claude_code(self, task, workdir):
        """Default runner: nested Claude Code with JSON output so we can capture and log
        the REAL fix-token cost (code_execution) — CREATE is billed outside the router,
        which is why est_tokens couldn't be calibrated before. Returns the result text."""
        proc = subprocess.run(
            ["claude", "-p", task, "--output-format", "json",
             "--dangerously-skip-permissions"],
            capture_output=True, text=True, cwd=workdir)
        text, usage = _parse_claude_json(proc.stdout or "")
        if self.router is not None and usage:
            self.router.log_external_cost("claude-code", "code_execution",
                                          usage["tokens"], usage["cost_usd"],
                                          area=self._area)
        return text or (proc.stderr or "").strip() or "no runner output"


# --------------------------------------------------------------------------- #
# JUDGE — adversarial review loaded with Anshuman's objection vocabulary
# --------------------------------------------------------------------------- #
class AdversarialReview(JudgeAgent):
    def __init__(self, router, adversarial_vocab_path, threshold=0.66):
        self.objections = _load_json(adversarial_vocab_path, [])
        self.panel = JudgmentPanel(router, "rca_panel", threshold=threshold)

    def judge(self, artifact, memory_factory=None) -> Verdict:
        vocab = "\n".join(f"- {o.get('objection','')[:140]}"
                          for o in self.objections[:15] if isinstance(o, dict))
        texts, relied = _recall(memory_factory, "engineering", "judge", artifact.body)
        lessons = "\n".join(f"- {t}" for t in texts)
        criteria = (
            "Adversarially review this fix (Sonnet challenged by GPT-4o). Reply "
            "'pass' only if it survives. Check: is it a patch masking a symptom or "
            "a ROOT-CAUSE fix; downstream/sibling breakage; scope creep; does it "
            "carry the fail-before/pass-after regression test.\n\n"
            "REVIEWER OBJECTIONS TO APPLY:\n" + vocab
            + (f"\n\nLESSONS:\n{lessons}" if lessons else "")
        )
        v = self.panel.decide(criteria, artifact.body)
        v.meta = {**(v.meta or {}), "relied": relied}
        return v


# --------------------------------------------------------------------------- #
# PUBLISH — open PR on branch ajit/fix-{n}, assign amit-kotidev (gh injected)
# --------------------------------------------------------------------------- #
class PRAgent(PublishAgent):
    def __init__(self, repo=REPO, branch_prefix=BRANCH_PREFIX, assignee=PR_ASSIGNEE,
                 pr_fn=None):
        self.repo = repo
        self.branch_prefix = branch_prefix
        self.assignee = assignee
        self.pr_fn = pr_fn or self._gh_pr

    def publish(self, artifact, channels) -> Receipt:
        num = artifact.meta.get("issue_number", "x")
        branch = f"{self.branch_prefix}{num}"
        title = f"fix: #{num}"
        body = (f"## RCA\n{artifact.meta.get('rca','(see plan)')}\n\n"
                f"## Fix\n{artifact.body}\n\n_assigned {self.assignee}_")
        ref = self.pr_fn(branch, title, body, self.assignee)
        return Receipt(channel="github", ref=ref,
                       meta={"branch": branch, "issue_number": num})

    def _gh_pr(self, branch, title, body, assignee):
        out = subprocess.run(
            ["gh", "pr", "create", "--repo", self.repo, "--head", branch,
             "--title", title, "--body", body, "--assignee", assignee],
            capture_output=True, text=True, check=True)
        return (out.stdout or "").strip()


# --------------------------------------------------------------------------- #
# LEARN — outcomes into engineering learn namespaces + knowledge base
# --------------------------------------------------------------------------- #
class FixMemory(LearnAgent):
    def __init__(self, memory_factory, knowledge_base_path=None):
        self.memory_factory = memory_factory
        self.kb_path = knowledge_base_path

    def record(self, signal, idea, artifact, outcome) -> None:
        if not self.memory_factory:
            return
        num = signal.payload.get("number", "") if signal else ""
        plan = idea.plan if idea and isinstance(idea.plan, dict) else {}
        layer = plan.get("layer", "")
        self.memory_factory("engineering", "ideate").add(
            f"outcome={outcome} | issue={num} | layer={layer} | "
            f"rca={(idea.summary[:80] if idea else '')}", tags=str(outcome))
        if outcome in ("rejected", "failed"):
            self.memory_factory("engineering", "judge").add(
                f"outcome={outcome} | issue={num}: review/fix did not land", tags=str(outcome))
        # recurrence ledger: one event per fix, tagged by area, so RCAAgent can
        # detect an area that keeps needing fixes and flag it for design review.
        area = plan.get("area") or _area_of(plan.get("entry_file", ""), layer)
        if area and area != "unknown":
            self.memory_factory("engineering", "fixlog").add(
                f"area={area} | outcome={outcome} | issue={num}", tags=area)
