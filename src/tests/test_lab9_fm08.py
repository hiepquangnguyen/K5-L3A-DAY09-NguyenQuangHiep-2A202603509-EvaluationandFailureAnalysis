"""M3 unit tests for ReplyMatchesLedger (FM-08) and NoPreDeduction (FM-05)."""

from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9.graders import NoPreDeduction, ReplyMatchesLedger

pytestmark = pytest.mark.student


def _ctx(refund_vnd: int, events: list[dict]) -> EvaluatorContext:
    trial = {
        "snapshot": {"refund_vnd": refund_vnd, "refund_count": 1 if refund_vnd > 0 else 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": events,
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output={"refund_vnd": refund_vnd, "approval_ok": True},
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_reply_matches_ledger_accepts_matching_and_no_reply():
    assert ReplyMatchesLedger().evaluate(_ctx(35000, [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-107."}}])).value is True
    assert ReplyMatchesLedger().evaluate(_ctx(0, [{"kind": "reply", "payload": {"text": "Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."}}])).value is True
    assert ReplyMatchesLedger().evaluate(_ctx(35000, [])).value is True


def test_reply_matches_ledger_flags_misreport():
    res = ReplyMatchesLedger().evaluate(_ctx(20000, [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}]))
    assert res.value is False


def test_no_pre_deduction_flags_lowered_proposal_and_allows_extra_lookup():
    pre_events = [
        {"kind": "quote", "payload": {"amount_vnd": 150000}},
        {"kind": "refund_history", "payload": {"refund_count": 1, "refunded_vnd": 30000}},
        {"kind": "proposal", "payload": {"amount_vnd": 120000}},
    ]
    assert NoPreDeduction().evaluate(_ctx(90000, pre_events)).value is False
    ok_events = [
        {"kind": "quote", "payload": {"amount_vnd": 150000}},
        {"kind": "refund_history", "payload": {"refund_count": 1, "refunded_vnd": 30000}},
    ]
    assert NoPreDeduction().evaluate(_ctx(120000, ok_events)).value is True
