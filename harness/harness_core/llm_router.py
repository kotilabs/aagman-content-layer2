"""llm_router.py — the ONLY place model choices resolve.

Loads harness_configs/models.yaml (defaults + panels + overrides + pricing) and
is the single source of truth: no concrete model string appears anywhere else.

- Startup pricing check: every model in every chain must have a pricing entry, or
  the router refuses to start (fail fast — a mispriced model would break the
  budget guard silently).
- Resolution order: overrides["{domain}.{step}"] -> panels[task] -> defaults[task].
- Resolver stub (Phase 1): primary() = chain[0]; the Phase-2 dynamic resolver
  plugs into _choose() without touching models.yaml.
- complete(): tries the chain in order, falls back on transient errors, logs cost
  to logs/cost_log.jsonl and records spend against the budget guard if wired.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import yaml

_DEFAULT_YAML = Path(__file__).resolve().parent.parent / "harness_configs" / "models.yaml"


class LLMRouter:
    def __init__(self, models_yaml_path=None, completion_fn=None,
                 cost_log_path=None, budget=None):
        path = Path(models_yaml_path) if models_yaml_path else _DEFAULT_YAML
        cfg = yaml.safe_load(path.read_text()) or {}
        self.defaults = cfg.get("defaults", {}) or {}
        self.panels = cfg.get("panels", {}) or {}
        self.overrides = cfg.get("overrides", {}) or {}
        self.pricing = cfg.get("pricing_per_1k", {}) or {}
        self._check_pricing()
        self.completion_fn = completion_fn or _litellm_completion
        self.cost_log_path = (Path(cost_log_path) if cost_log_path
                              else path.resolve().parent.parent / "logs" / "cost_log.jsonl")
        self.budget = budget

    # -- resolution ------------------------------------------------------- #
    def resolve(self, task_type, domain=None, step=None) -> list:
        if domain and step:
            key = f"{domain}.{step}"
            if key in self.overrides:
                return list(self.overrides[key])
        if task_type in self.panels:
            return list(self.panels[task_type])
        if task_type in self.defaults:
            return list(self.defaults[task_type])
        raise KeyError(
            f"no model chain for task_type '{task_type}' (domain={domain} step={step})")

    def primary(self, task_type, domain=None, step=None) -> str:
        return self._choose(self.resolve(task_type, domain, step))[0]

    def _choose(self, chain) -> list:
        # Phase-1 resolver stub: pass-through (chain[0] first).
        # Phase-2 dynamic resolver (artifact_type + priority) plugs in HERE only.
        return list(chain)

    def price(self, model) -> float:
        return float(self.pricing.get(model, 0.0))

    # -- execution -------------------------------------------------------- #
    def call_model(self, model, task_type, prompt, **kw) -> dict:
        """Call one specific model; log cost + record spend. May raise (the caller
        decides fallback). Panels call this per member; complete() loops it."""
        res = self.completion_fn(model, prompt, **kw)
        tokens = int(res.get("tokens", 0))
        cost = self.price(model) * tokens / 1000.0
        self._log_cost(model, task_type, tokens, cost)
        if self.budget is not None:
            self.budget.record(cost)
        return {"text": res.get("text", ""), "model": model,
                "tokens": tokens, "cost_usd": cost}

    def complete(self, task_type, prompt, domain=None, step=None, **kw) -> dict:
        chain = self._choose(self.resolve(task_type, domain, step))
        last_err = None
        for model in chain:
            try:
                return self.call_model(model, task_type, prompt, **kw)
            except Exception as e:  # transient (429/500/timeout) -> next in chain
                last_err = e
        raise last_err if last_err else RuntimeError(f"empty chain for '{task_type}'")

    # -- internals -------------------------------------------------------- #
    def _all_chain_models(self) -> set:
        models: set = set()
        for table in (self.defaults, self.panels, self.overrides):
            for chain in table.values():
                models.update(chain)
        return models

    def _check_pricing(self):
        missing = sorted(m for m in self._all_chain_models() if m not in self.pricing)
        if missing:
            raise ValueError(
                f"models.yaml: missing pricing_per_1k for {missing} — router refuses "
                f"to start (every model in every chain must be priced)")

    def _log_cost(self, model, task_type, tokens, cost, area=""):
        self.cost_log_path.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.time(), "model": model, "task_type": task_type,
               "tokens": tokens, "cost_usd": cost}
        if area:
            rec["area"] = area
        with self.cost_log_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def log_external_cost(self, model, task_type, tokens, cost, area=""):
        """Record a subprocess/external cost (e.g. the nested `claude -p` CREATE, billed
        outside the router) into the same cost_log + budget as router calls, so est_tokens
        can calibrate on real fix-token cost."""
        self._log_cost(model, task_type, tokens, cost, area=area)
        if self.budget is not None:
            self.budget.record(cost)


def _litellm_completion(model, prompt, **kw):
    """Default adapter over litellm. Not exercised in Phase-1 tests (no API keys)."""
    import litellm
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kw,
    )
    text = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage") or {}
    tokens = usage.get("total_tokens", 0)
    return {"text": text, "tokens": tokens}
