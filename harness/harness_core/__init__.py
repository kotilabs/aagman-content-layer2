"""harness_core — the generic, domain-agnostic engine.

No domain logic may leak into this package; the Phase-1 genericity grep enforces
that. Domains live in their own packages and plug in only via harness_configs/*.
"""
