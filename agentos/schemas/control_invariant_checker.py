from agentos.schemas.control import ControlStatus


def check_control_invariants(control_outcome, decision_record):
    """
    Control 层不变量
    """

    status = control_outcome.get("status")

    assert status in {
        ControlStatus.ALLOWED,
        ControlStatus.BLOCKED,
        ControlStatus.FROZEN,
    }, f"[INV] Invalid FSM status: {status}"

    review_required = decision_record.review_required
    freeze_candidate = decision_record.freeze_candidate

    # Freeze 优先级高于 Review
    if freeze_candidate:
        assert status == ControlStatus.FROZEN, \
            "[INV] freeze_candidate must result in FROZEN"
        return

    if review_required:
        assert status == ControlStatus.BLOCKED, \
            "[INV] review_required must result in BLOCKED"
