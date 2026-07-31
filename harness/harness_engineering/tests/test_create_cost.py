"""CREATE cost instrumentation: parse `claude -p --output-format json` into
(result_text, usage) so the runner can log real fix-token cost to the cost_log."""
import json

from harness_engineering.agents import _parse_claude_json


def test_parse_claude_json_extracts_text_and_summed_usage():
    out = json.dumps({
        "type": "result", "result": "done fixing", "total_cost_usd": 0.42,
        "usage": {"input_tokens": 50000, "output_tokens": 3000,
                  "cache_read_input_tokens": 10000},
    })
    text, usage = _parse_claude_json(out)
    assert text == "done fixing"
    assert usage["tokens"] == 63000            # all *_tokens fields summed
    assert usage["cost_usd"] == 0.42


def test_parse_claude_json_stream_array_takes_result():
    out = json.dumps([
        {"type": "assistant", "text": "working"},
        {"type": "result", "result": "final", "usage": {"input_tokens": 100}},
    ])
    text, usage = _parse_claude_json(out)
    assert text == "final"
    assert usage["tokens"] == 100


def test_parse_claude_json_plaintext_fallback():
    text, usage = _parse_claude_json("just some text")
    assert text == "just some text"
    assert usage is None


def test_parse_claude_json_empty():
    assert _parse_claude_json("") == ("", None)
