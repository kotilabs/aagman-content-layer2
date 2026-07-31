"""Phase-2C TDD: seed_memory.py — distilled JSONs -> AgentMemory namespaces.

Guarantees no engineering namespace boots empty. Flexible extractor tolerates the
various distilled JSON shapes (lists of dicts, nested dicts).
"""
import json

import seed_memory
from harness_core.agent_memory import AgentMemory


def _write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))
    return p


def test_seed_all_populates_every_namespace(tmp_path):
    eng = tmp_path / "harness_engineering" / "distilled"
    con = tmp_path / "harness_content" / "distilled"
    mapping = {
        ("engineering", "sense"): [_write(eng / "classifier_examples.json",
                                          [{"title": "crash", "label": "bug"}])],
        ("engineering", "ideate"): [_write(eng / "layer_ground_truth.json",
                                           [{"symptom": "risk_blocked", "layer": "typescript"}])],
        ("engineering", "create"): [_write(eng / "fix_success_patterns.json",
                                           [{"approach": "fix at source", "merged_first_try": True}])],
        ("engineering", "judge"): [_write(eng / "adversarial_vocab.json",
                                          [{"pattern": "patch", "objection": "root cause?"}])],
        ("engineering", "gate"): [_write(eng / "sebi_patterns.json",
                                         [{"flag": "return claim", "rule": "no returns"}])],
        ("content", "create"): [_write(con / "examples.json", [{"text": "educational post"}])],
        ("content", "judge"): [_write(con / "rejected_patterns.json", [{"pattern": "buy call"}])],
    }
    db = str(tmp_path / "m.db")
    counts = seed_memory.seed_all(db_path=db, mapping=mapping)
    for ns in ("engineering/sense", "engineering/ideate", "engineering/create",
               "engineering/judge", "engineering/gate", "content/create", "content/judge"):
        assert counts[ns] > 0, f"{ns} seeded empty"
    # actually retrievable through the real API
    assert AgentMemory("engineering", "judge", db_path=db).count() > 0


def test_nested_dict_json_is_flattened(tmp_path):
    eng = tmp_path / "harness_engineering" / "distilled"
    f = _write(eng / "file_relationships.json",
               {"areas": {"risk": ["risk-calculations.ts", "risk.py"]},
                "co_change": [["a.ts", "b.ts"]]})
    db = str(tmp_path / "m.db")
    counts = seed_memory.seed_all(db_path=db,
                                  mapping={("engineering", "ideate"): [f]})
    assert counts["engineering/ideate"] > 0


def test_missing_file_seeds_zero_without_error(tmp_path):
    counts = seed_memory.seed_all(
        db_path=str(tmp_path / "m.db"),
        mapping={("engineering", "sense"): [tmp_path / "nope.json"]})
    assert counts["engineering/sense"] == 0
