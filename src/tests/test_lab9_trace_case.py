"""M1 regression test from docs/trace_case.md (C-002@11: FM-03 ticket_trust)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.student


def _ctx(case: dict):
    from pydantic_evals.evaluators import EvaluatorContext

    return EvaluatorContext(
        name="C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_seeded_regression_triggers_override_and_fails():
    from lab9.graders import DbFactKept
    from lab9.trace_case import investigate

    case = investigate("seeded_regression", "C-002", 11)
    trial = case["trial"]
    assert trial["lab8_pass"] is False
    assert trial["snapshot"]["refund_vnd"] == 20000
    assert any(e.get("kind") == "model_override" for e in trial["events"])
    assert DbFactKept().evaluate(_ctx(case)).value is False


def test_c002_fixed_keeps_db_fact_and_passes():
    from lab9.graders import DbFactKept
    from lab9.trace_case import investigate

    case = investigate("fixed", "C-002", 11)
    trial = case["trial"]
    assert trial["lab8_pass"] is True
    assert trial["snapshot"]["refund_vnd"] == 0
    assert not any(e.get("kind") == "model_override" for e in trial["events"])
    assert DbFactKept().evaluate(_ctx(case)).value is True
