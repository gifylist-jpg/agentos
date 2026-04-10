from __future__ import annotations

from typing import Any, Mapping


REQUIRED_FEEDBACK_FIELDS = (
    "analysis_result",
    "decision_record",
    "review_result",
    "freeze_result",
    "control_outcome",
)


def assert_valid_control_outcome(control_outcome: Mapping[str, Any] | None) -> None:
    if not isinstance(control_outcome, Mapping):
        raise ValueError("control_outcome must be a mapping")

    required = ("status", "next_step", "reason")
    missing = [field for field in required if field not in control_outcome]
    if missing:
        raise ValueError(f"control_outcome missing required fields: {missing}")


def assert_has_required_feedback_fields(feedback_result: Mapping[str, Any] | None) -> None:
    if not isinstance(feedback_result, Mapping):
        raise ValueError("feedback_result must be a mapping")

    missing = [field for field in REQUIRED_FEEDBACK_FIELDS if field not in feedback_result]
    if missing:
        raise ValueError(f"feedback_result missing required fields: {missing}")

    assert_valid_control_outcome(feedback_result.get("control_outcome"))
