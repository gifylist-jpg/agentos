from __future__ import annotations

from unittest.mock import Mock

from services.alert_service import AlertService


def test_record_alert_calls_audit_logger() -> None:
    audit_logger = Mock()
    service = AlertService(audit_logger=audit_logger)

    service.record_alert(
        task_id="task_001",
        alert_type="task_stuck",
        severity="high",
        message="Task has been stuck in waiting_review too long",
        details={"state": "waiting_review", "duration": 360},
    )

    audit_logger.log_event.assert_called_once()


def test_record_alert_uses_alert_event_type() -> None:
    audit_logger = Mock()
    service = AlertService(audit_logger=audit_logger)

    service.record_alert(
        task_id="task_002",
        alert_type="guard_failure",
        severity="medium",
        message="Guard failure detected",
        details={"rule": "state_transition"},
    )

    _, kwargs = audit_logger.log_event.call_args
    assert kwargs["event_type"] == "alert"


def test_record_alert_payload_contains_required_fields() -> None:
    audit_logger = Mock()
    service = AlertService(audit_logger=audit_logger)

    service.record_alert(
        task_id="task_003",
        alert_type="recovery_triggered",
        severity="low",
        message="Recovery was triggered",
        details={"from_state": "executing", "to_state": "approved"},
    )

    _, kwargs = audit_logger.log_event.call_args

    assert kwargs["task_id"] == "task_003"
    assert kwargs["event_type"] == "alert"

    event_data = kwargs["event_data"]
    assert event_data["task_id"] == "task_003"
    assert event_data["alert_type"] == "recovery_triggered"
    assert event_data["severity"] == "low"
    assert event_data["message"] == "Recovery was triggered"
    assert event_data["details"] == {
        "from_state": "executing",
        "to_state": "approved",
    }


if __name__ == "__main__":
    test_record_alert_calls_audit_logger()
    test_record_alert_uses_alert_event_type()
    test_record_alert_payload_contains_required_fields()
    print("\nAll alert service tests passed.")
