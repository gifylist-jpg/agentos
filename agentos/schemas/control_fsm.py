from agentos.schemas.control import ControlStatus, ControlOutcome


def map_to_control_outcome(review_required: bool, freeze_candidate: bool) -> ControlOutcome:
    if freeze_candidate:
        return ControlOutcome(
            status=ControlStatus.FROZEN,
            next_step="FREEZE",
            reason="freeze_candidate=True",
        )

    if review_required:
        return ControlOutcome(
            status=ControlStatus.BLOCKED,
            next_step="REVIEW",
            reason="review_required=True",
        )

    return ControlOutcome(
        status=ControlStatus.ALLOWED,
        next_step="PROCEED",
        reason=None,
    )
