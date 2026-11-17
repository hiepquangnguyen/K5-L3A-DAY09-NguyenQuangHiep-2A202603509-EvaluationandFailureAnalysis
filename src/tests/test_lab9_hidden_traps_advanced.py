"""M7 extra checks for hidden integrity traps (duplicate rows, evaluator_failures on green run, slice relabeling)."""

from __future__ import annotations

import copy

import pytest

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["denial"] if i < 2 else []}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}],
    "slices": [{"name": "denial", "metric": "pass_rate", "min": 0.9, "blocking": True}],
}


def _report(rows, metrics, failures=()):
    return {
        "manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]},
        "rows": rows,
        "metrics": metrics,
        "evaluator_failures": list(failures),
    }


def test_advanced_flags_duplicate_rows_and_green_failures_and_slice_relabel():
    from lab9 import gate

    base = _report(copy.deepcopy(ROWS), {"pass_rate": 1.0})
    assert gate.integrity_check(base, base, SPEC, SPEC) == []

    dup_rows = copy.deepcopy(ROWS[:-1]) + [copy.deepcopy(ROWS[0])]
    assert gate.integrity_check(_report(dup_rows, {"pass_rate": 1.0}), base, SPEC)

    green_fail = _report(copy.deepcopy(ROWS), {"pass_rate": 1.0}, failures=["E-001@1:TrialPass:timeout"])
    assert gate.integrity_check(green_fail, base, SPEC)

    relabelled = copy.deepcopy(ROWS)
    relabelled[0]["slices"] = []
    assert gate.integrity_check(_report(relabelled, {"pass_rate": 1.0}), base, SPEC)
