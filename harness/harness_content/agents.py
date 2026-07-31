"""harness_content/agents.py — the CONTENT domain agents.

Six agents implementing the six ABCs. They hold a router (model choices resolve
through models.yaml, never hard-coded here) and a memory_factory (namespaced
lessons for self-evolution). Compliance is layered: every text artifact begins
with the mandatory RIA disclosure (so the ComplianceGate's REQUIRED_STRINGS pass
deterministically), and the ContentJudge runs a multi-model quality panel whose
`block` drives the create->revise loop.
"""
from __future__ import annotations

import json
from pathlib import Path

from harness_core.agent_base import (
    Artifact, Idea, Receipt, Signal, Verdict, _fingerprint,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.judgment_panel import JudgmentPanel

# Public identifiers (also in .env.example); overridable via env at wiring time.
RIA_NAME = "Koti Labs"
RIA_REG = "INA000021951"

_BRIEF_SUFFIXES = (".md", ".txt", ".json")


def disclosure(ria_name: str = RIA_NAME, reg: str = RIA_REG) -> str:
    """The mandatory not-investment-advice line that opens every text post. Must
    contain the RIA name + reg number verbatim (SEBI_RULES REQUIRED_STRINGS)."""
    return (f"Educational content from {ria_name} (SEBI RIA {reg}). "
            f"Not investment advice — no buy/sell recommendation.")


def _read(path: str) -> str:
    try:
        return Path(path).read_text()
    except (OSError, TypeError):
        return ""


def _lesson_texts(mem, query: str, k: int = 5) -> list:
    """top_k returns lesson IDs; resolve them to their text via get()."""
    out = []
    for lid in mem.top_k(query, k=k):
        les = mem.get(lid)
        if les and les.text:
            out.append(les.text)
    return out


def _recall(memory_factory, domain, step, query, k=5):
    """Recall lesson TEXTS + PROVENANCE. relied=[[domain, step, id], ...] is stamped on
    the Idea so the harness credits/blames exactly the lessons a cycle relied on
    (self-evolution scoring — identical contract to the engineering domain)."""
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
# SENSE — briefs inbox folder
# --------------------------------------------------------------------------- #
class ContentSensor(SenseAgent):
    def __init__(self, inbox_dir: str):
        self.inbox_dir = Path(inbox_dir)

    def sense(self, sources=None) -> list:
        dirs = [Path(s) for s in sources] if sources else [self.inbox_dir]
        signals = []
        for d in dirs:
            if not d.exists():
                continue
            for f in sorted(d.iterdir()):
                if not (f.is_file() and f.suffix.lower() in _BRIEF_SUFFIXES):
                    continue
                payload = self._payload(f)
                signals.append(Signal(id=f"content:{f.name}", domain="content",
                                      source="inbox", payload=payload))
        return signals

    @staticmethod
    def _payload(f: Path) -> dict:
        raw = f.read_text()
        if f.suffix.lower() == ".json":
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    obj.setdefault("brief", obj.get("brief", ""))
                    obj["file"] = f.name
                    return obj
            except ValueError:
                pass
        return {"brief": raw.strip(), "file": f.name}


# --------------------------------------------------------------------------- #
# IDEATE — educational-only framing from brand voice + examples + memory
# --------------------------------------------------------------------------- #
class ContentStrategist(IdeateAgent):
    def __init__(self, router, memory_factory, brand_voice_path, examples_path):
        self.router = router
        self.memory_factory = memory_factory
        self.brand_voice_path = brand_voice_path
        self.examples_path = examples_path

    def ideate(self, signal) -> Idea:
        brief = signal.payload.get("brief", "")
        channel = signal.payload.get("channel", "linkedin")
        lesson_texts, relied = _recall(self.memory_factory, "content", "ideate", brief)
        lessons = "\n".join(f"- {t}" for t in lesson_texts)
        prompt = (
            "You are an educational-only content strategist for a SEBI RIA. "
            "Produce an ANGLE and key points that inform and explain — never a "
            "buy/sell call, price target, or return promise.\n\n"
            f"BRAND VOICE:\n{_read(self.brand_voice_path)[:2000]}\n\n"
            + (f"LESSONS:\n{lessons}\n\n" if lessons else "")
            + f"CHANNEL: {channel}\nBRIEF: {brief}\n"
        )
        res = self.router.complete("complex_planning", prompt,
                                   domain="content", step="ideate")
        return Idea(summary=res["text"].strip(),
                    plan={"channel": channel, "brief": brief},
                    confidence=0.9,
                    meta={"model": res.get("model", ""), "relied": relied})


# --------------------------------------------------------------------------- #
# CREATE — parallel fan_out (text/image); text opens with the RIA disclosure
# --------------------------------------------------------------------------- #
class ContentCreator(CreateAgent):
    def __init__(self, router, memory_factory, brand_voice_path, channel_rules_path,
                 ria_name: str = RIA_NAME, reg_number: str = RIA_REG):
        self.router = router
        self.memory_factory = memory_factory
        self.brand_voice_path = brand_voice_path
        self.channel_rules = self._load_rules(channel_rules_path)
        self.ria_name = ria_name
        self.reg_number = reg_number

    def create(self, idea) -> Artifact:
        channel = idea.plan.get("channel", "linkedin")
        modality = idea.meta.get("fan_out", "text")
        if modality == "image":
            prompt = (f"Write an image / storyboard PROMPT (no image generated in "
                      f"this phase) for a {channel} visual illustrating: {idea.summary}")
            res = self.router.complete("content_gen", prompt,
                                       domain="content", step="create")
            return Artifact(body=res["text"].strip(), kind="image",
                            meta={"channel": channel, "model": res.get("model", "")})
        prompt = (
            "Write educational content for a SEBI RIA. Inform and explain; no "
            "buy/sell call, price target, urgency, or return promise. End on an "
            "open question, not a CTA.\n\n"
            f"BRAND VOICE:\n{_read(self.brand_voice_path)[:2000]}\n\n"
            f"CHANNEL: {channel}\nANGLE:\n{idea.summary}\n"
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        body = self._finalize(res["text"].strip(), channel)
        return Artifact(body=body, kind="text",
                        meta={"channel": channel, "model": res.get("model", "")})

    def revise(self, artifact, issues) -> Artifact:
        channel = artifact.meta.get("channel", "linkedin")
        prompt = (
            "Revise this content to fix the issues below, preserving the "
            "educational-only, no-advice framing.\n\n"
            f"ISSUES:\n" + "\n".join(f"- {i}" for i in issues) + "\n\n"
            f"CURRENT:\n{artifact.body}\n"
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        text = res["text"].strip()
        if artifact.kind == "text":
            body = self._finalize(text, channel)
        else:
            body = text
        return Artifact(body=body, kind=artifact.kind,
                        meta={**artifact.meta, "revised": True})

    # -- helpers --
    def _finalize(self, text: str, channel: str) -> str:
        body = f"{disclosure(self.ria_name, self.reg_number)}\n\n{text}"
        limit = self._char_limit(channel)
        if limit and len(body) > limit:
            body = body[:limit].rstrip()
        return body

    def _char_limit(self, channel: str):
        rule = self.channel_rules.get(channel) or {}
        for k in ("max_chars", "char_limit", "max_length"):
            if isinstance(rule.get(k), int):
                return rule[k]
        return None

    @staticmethod
    def _load_rules(path: str) -> dict:
        try:
            obj = json.loads(Path(path).read_text())
            return obj if isinstance(obj, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}


# --------------------------------------------------------------------------- #
# JUDGE — multi-model quality panel (brand voice / accuracy / engagement)
# --------------------------------------------------------------------------- #
class ContentJudge(JudgeAgent):
    """The quality decision lives HERE (not as a judge-gate) so a `block` bounces
    back to create.revise via the loop (a gate block would only park). Panel
    models resolve from models.yaml `judge_panel` — the three dimensions are
    criteria in the prompt, not hard-coded model assignments."""

    def __init__(self, router, threshold: float = 0.66):
        # No domain/step: the judge votes with the judge_panel chain, never a
        # per-step generation override (see content_config compliance note).
        self.panel = JudgmentPanel(router, "judge_panel", threshold=threshold)

    def judge(self, artifact, memory_factory=None) -> Verdict:
        texts, relied = _recall(memory_factory, "content", "judge", artifact.body)
        lessons = "\n".join(f"- {t}" for t in texts)
        criteria = (
            "Evaluate this content on THREE dimensions and reply 'pass' only if "
            "all hold: (1) BRAND VOICE — educational, no hype, ends on open "
            "tension not a CTA; (2) ACCURACY — every claim/number sourced, no "
            "fabrication; (3) ENGAGEMENT — clear and compelling without urgency "
            "or a buy/sell call."
            + (f"\n\nLESSONS FROM PAST REJECTIONS:\n{lessons}" if lessons else "")
        )
        v = self.panel.decide(criteria, artifact.body)
        v.meta = {**(v.meta or {}), "relied": relied}
        return v


# --------------------------------------------------------------------------- #
# PUBLISH — write final artifact to outbox/{channel}/ (+ post only if configured)
# --------------------------------------------------------------------------- #
class ContentPublisher(PublishAgent):
    def __init__(self, outbox_dir: str, poster=None):
        self.outbox_dir = Path(outbox_dir)
        self.poster = poster

    def publish(self, artifact, channels) -> Receipt:
        channel = (channels[0] if channels
                   else artifact.meta.get("channel", "outbox"))
        d = self.outbox_dir / channel
        d.mkdir(parents=True, exist_ok=True)
        name = artifact.meta.get("id") or _fingerprint(artifact.body)
        path = d / f"{name}.md"
        meta = {"kind": artifact.kind, "channel": channel, **artifact.meta}
        path.write_text(f"---\n{json.dumps(meta)}\n---\n{artifact.body}\n")
        ref = str(path)
        if self.poster is not None and self.poster.configured(channel):
            ref = self.poster.post(channel, artifact.body)
        return Receipt(channel=channel, ref=ref, meta=meta)


# --------------------------------------------------------------------------- #
# LEARN — outcome-based lessons into content namespaces
# --------------------------------------------------------------------------- #
class ContentMemory(LearnAgent):
    def __init__(self, memory_factory):
        self.memory_factory = memory_factory

    def record(self, signal, idea, artifact, outcome) -> None:
        if not self.memory_factory:
            return
        channel = idea.plan.get("channel", "") if idea else ""
        brief = signal.payload.get("brief", "")[:80] if signal else ""
        self.memory_factory("content", "create").add(
            f"outcome={outcome} | channel={channel} | brief={brief}", tags=str(outcome))
