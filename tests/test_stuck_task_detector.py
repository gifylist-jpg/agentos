from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from services.stuck_task_detector import StuckTaskDetector
from models.task import Task


def _make_task(task_id: str, state: str, updated_at: datetime) -> Task:
    task = Task(
        task_id=task_id,
        task_type="test_task",
        workflow_type="video_production",
    )
    task.current_state = state
    task.updated_at = updated_at
    return task


def test_normal_task_not_stuck() -> None:
    now = datetime.now(timezone.utc)
    task = _make_task(
        "task_001",
        "waiting_review",
        now - timedelta(seconds=120),
    )
    audit_logger = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger,
        now_provider=lambda: now,
    )

    stuck = detector.detect_stuck_tasks([task])

    assert stuck == []
    audit_logger.log_event.assert_not_called()


def test_waiting_review_timeout_detected() -> None:
    now = datetime.now(timezone.utc)
    task = _make_task(
        "task_002",
        "waiting_review",
        now - timedelta(seconds=301),
    )
    audit_logger = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger,
        now_provider=lambda: now,
    )

    stuck = detector.detect_stuck_tasks([task])

    assert len(stuck) == 1
    assert stuck[0].task_id == "task_002"
    audit_logger.log_event.assert_called_once()


def test_executing_timeout_detected() -> None:
    now = datetime.now(timezone.utc)
    task = _make_task(
        "task_003",
        "executing",
        now - timedelta(seconds=601),
    )
    audit_logger = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger,
        now_provider=lambda: now,
    )

    stuck = detector.detect_stuck_tasks([task])

    assert len(stuck) == 1
    assert stuck[0].task_id == "task_003"
    audit_logger.log_event.assert_called_once()


def test_audit_logger_log_event_called_when_stuck_detected() -> None:
    now = datetime.now(timezone.utc)
    task = _make_task(
        "task_004",
        "executing",
        now - timedelta(seconds=900),
    )
    audit_logger = Mock()

    detector = StuckTaskDetector(
        audit_logger=audit_logger,
        now_provider=lambda: now,
    )

    detector.detect_stuck_tasks([task])

    audit_logger.log_event.assert_called_once()
    _, kwargs = audit_logger.log_event.call_args
    assert kwargs["task_id"] == "task_004"
    assert kwargs["event_type"] == "task_stuck"
    assert kwargs["event_data"]["state"] == "executing"


if __name__ == "__main__":
    test_normal_task_not_stuck()
    test_waiting_review_timeout_detected()
    test_executing_timeout_detected()
    test_audit_logger_log_event_called_when_stuck_detected()
    print("\nAll stuck task detector tests passed.")
