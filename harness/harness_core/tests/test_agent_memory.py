"""Phase-1 TDD: agent_memory.py — namespaced lessons + self-evolution hooks.

top_k(query, k) returns lesson IDs ranked by relevance x confidence (keyword/recency
for Phase 1). attribute(ids, outcome) credits/blames after an outcome; confidence =
helped/(helped+misled); a lesson with confidence < 0.3 after >= 5 uses auto-retires
(archived, not deleted). count() feeds Phase-2 seed verification.
"""
from harness_core.agent_memory import AgentMemory, Lesson


def _mem(tmp_path, domain="engineering", step="ideate", now=None):
    return AgentMemory(domain, step, db_path=str(tmp_path / "mem.db"),
                       now=now or (lambda: 1000.0))


def test_add_and_count(tmp_path):
    m = _mem(tmp_path)
    m.add("risk_blocked errors are TypeScript, start at risk-calculations.ts")
    m.add("never write python tests for a typescript bug")
    assert m.count() == 2


def test_namespaces_are_isolated(tmp_path):
    db = str(tmp_path / "mem.db")
    a = AgentMemory("engineering", "ideate", db_path=db)
    b = AgentMemory("engineering", "judge", db_path=db)
    a.add("layer lesson")
    assert a.count() == 1
    assert b.count() == 0


def test_top_k_returns_most_relevant_ids(tmp_path):
    m = _mem(tmp_path)
    l1 = m.add("typescript risk layer lesson", tags="typescript risk")
    m.add("python pandas dataframe lesson", tags="python pandas")
    assert m.top_k("typescript risk bug", k=1) == [l1.id]


def test_confidence_is_helped_over_total(tmp_path):
    m = _mem(tmp_path)
    l = m.add("x")
    m.attribute([l.id], "helped")
    m.attribute([l.id], "helped")
    m.attribute([l.id], "misled")
    assert m.get(l.id).confidence == 2 / 3


def test_credited_lesson_outranks_blamed_one(tmp_path):
    m = _mem(tmp_path)
    a = m.add("lesson A about foo", tags="foo")
    b = m.add("lesson B about foo", tags="foo")
    for _ in range(3):
        m.attribute([a.id], "helped")
    m.attribute([b.id], "misled")
    assert m.top_k("foo", k=2)[0] == a.id


def test_low_confidence_lesson_auto_retired_after_5_uses(tmp_path):
    m = _mem(tmp_path)
    l = m.add("bad lesson", tags="foo")
    m.attribute([l.id], "helped")            # 1 helped
    for _ in range(4):
        m.attribute([l.id], "misled")        # 4 misled -> conf 0.2, uses 5
    assert m.get(l.id).retired == 1
    assert m.count() == 0                     # retired excluded from count
    assert m.count(include_retired=True) == 1
    assert l.id not in m.top_k("foo", k=10)   # retired not retrieved


def test_day0_seed_starts_neutral_and_is_retrievable(tmp_path):
    m = _mem(tmp_path)
    s = m.add("seed lesson foo", tags="foo")
    assert m.count() == 1
    assert 0.4 < m.get(s.id).confidence < 0.6  # neutral prior, unproven
    assert s.id in m.top_k("foo", k=10)
