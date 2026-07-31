"""LLMRouter.log_external_cost records a subprocess/external cost (the nested claude -p
CREATE) into the same cost_log + budget as router calls, so est_tokens can eventually
calibrate on real fix-token cost."""
import json


class _Budget:
    def __init__(self):
        self.spent = 0.0

    def record(self, c):
        self.spent += c


def test_log_external_cost_writes_code_execution_record(tmp_path):
    from harness_core.llm_router import LLMRouter
    log = tmp_path / "cost.jsonl"
    b = _Budget()
    r = LLMRouter(completion_fn=lambda *a, **k: {"text": "", "tokens": 0},
                  cost_log_path=str(log), budget=b)
    r.log_external_cost("claude-code", "code_execution", 63000, 0.42, area="backend/src")

    recs = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
    assert len(recs) == 1
    rec = recs[0]
    assert rec["task_type"] == "code_execution"
    assert rec["tokens"] == 63000
    assert rec["cost_usd"] == 0.42
    assert rec["area"] == "backend/src"
    assert b.spent == 0.42                      # counted against budget too
