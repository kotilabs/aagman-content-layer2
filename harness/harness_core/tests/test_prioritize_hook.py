"""run_once applies an optional, injected prioritizer to reorder/subset the open work
items before the pipeline loop. The hook is domain-free — harness_core knows only that
a callable(list)->list may reorder and drop items (deferred stay open for next run)."""
from types import SimpleNamespace

from harness_core.generic_harness import GenericHarness


class _Store:
    def __init__(self, items):
        self._items = items

    def open_items(self):
        return list(self._items)


class _Config:
    def step(self, name):
        return None                      # no sense agent -> no signals this run


def _harness(items, prioritizer):
    h = GenericHarness(_Config(), _Store(items), prioritizer=prioritizer)
    calls = []
    h.run_item = lambda wi: calls.append(wi.id)
    return h, calls


def test_run_once_applies_prioritizer_reorder_and_subset():
    items = [SimpleNamespace(id="a"), SimpleNamespace(id="b"), SimpleNamespace(id="c")]
    h, calls = _harness(items, prioritizer=lambda xs: [xs[2], xs[0]])   # reorder + drop b
    h.run_once(sources=None)
    assert calls == ["c", "a"]


def test_run_once_without_prioritizer_is_fifo():
    items = [SimpleNamespace(id="a"), SimpleNamespace(id="b")]
    h, calls = _harness(items, prioritizer=None)
    h.run_once(sources=None)
    assert calls == ["a", "b"]
