# agentos/schemas/control_invariant_checker.py

from agentos.schemas.control import ControlStatus

def check_control_invariants(control_outcome, decision_record):
    """
    Control 层不变量
    """

    status = control_outcome.get("status")

    # 🔴 FSM 限制
    assert status in {
        ControlStatus.ALLOWED,
        ControlStatus.BLOCKED,
        ControlStatus.FROZEN,
    }, f"[INV] Invalid FSM status: {status}"

    # 🔴 Review Gate
    if decision_record.review_required:
        assert status == ControlStatus.BLOCKED, \
            "[INV] review_required must result in BLOCKED"

    # 🔴 Freeze Gate
    if decision_record.freeze_candidate:
        assert status == ControlStatus.FROZEN, \
            "[INV] freeze_candidate must result in FROZEN"
