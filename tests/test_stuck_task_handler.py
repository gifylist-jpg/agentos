from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from models.task import Task
from services.alert_service import AlertService
from services.recovery_policy import RecoveryPolicy
from services.stuck_task_detector import StuckTaskDetector
from services.stuck_task_handler import StuckTaskHandler


def _make_task(task_id: str, state: str, updated_at: datetime) -> Task:
    task = Task(
        task_id=task_id,
        task_type="test_task",
        workflow_type="video_production",
    )
    task.current_state = state
    task.updated_at = updated_at
    return task


def test_normal_task_returns_empty_results() -> None:
    now = datetime.now(timezone.utc)
    audit_logger_for_detector = Mock()
    audit_logger_for_alert = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger_for_detector,
        now_provider=lambda: now,
    )
    alert_service = AlertService(audit_logger=audit_logger_for_alert)
    recovery_policy = RecoveryPolicy()

    handler = StuckTaskHandler(
        detector=detector,
        alert_service=alert_service,
        recovery_policy=recovery_policy,
    )

    task = _make_task(
        "task_001",
        "waiting_review",
        now - timedelta(seconds=120),
    )

    results = handler.handle([task])

    assert results == []
    audit_logger_for_detector.log_event.assert_not_called()
    audit_logger_for_alert.log_event.assert_not_called()


def test_waiting_review_stuck_triggers_alert_and_retry_policy() -> None:
    now = datetime.now(timezone.utc)
    audit_logger_for_detector = Mock()
    audit_logger_for_alert = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger_for_detector,
        now_provider=lambda: now,
    )
    alert_service = AlertService(audit_logger=audit_logger_for_alert)
    recovery_policy = RecoveryPolicy()

    handler = StuckTaskHandler(
        detector=detector,
        alert_service=alert_service,
        recovery_policy=recovery_policy,
    )

    task = _make_task(
        "task_002",
        "waiting_review",
        now - timedelta(seconds=301),
    )

    results = handler.handle([task])

    assert len(results) == 1
    assert results[0]["task_id"] == "task_002"
    assert results[0]["state"] == "waiting_review"
    assert results[0]["severity"] == "L2"
    assert results[0]["action"] == "rollback"

    audit_logger_for_detector.log_event.assert_called_once()
    audit_logger_for_alert.log_event.assert_called_once()


def test_executing_stuck_triggers_alert_and_human_intervention_policy() -> None:
    now = datetime.now(timezone.utc)
    audit_logger_for_detector = Mock()
    audit_logger_for_alert = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger_for_detector,
        now_provider=lambda: now,
    )
    alert_service = AlertService(audit_logger=audit_logger_for_alert)
    recovery_policy = RecoveryPolicy()

    handler = StuckTaskHandler(
        detector=detector,
        alert_service=alert_service,
        recovery_policy=recovery_policy,
    )

    task = _make_task(
        "task_003",
        "executing",
        now - timedelta(seconds=601),
    )

    results = handler.handle([task])

    assert len(results) == 1
    assert results[0]["task_id"] == "task_003"
    assert results[0]["state"] == "executing"
    assert results[0]["severity"] == "L3"
    assert results[0]["action"] == "human_intervention"

    audit_logger_for_detector.log_event.assert_called_once()
    audit_logger_for_alert.log_event.assert_called_once()


if __name__ == "__main__":
    test_normal_task_returns_empty_results()
    test_waiting_review_stuck_triggers_alert_and_retry_policy()
    test_executing_stuck_triggers_alert_and_human_intervention_policy()
    print("\nAll stuck task handler tests passed.")
