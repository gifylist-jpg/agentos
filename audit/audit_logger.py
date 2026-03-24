from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from storage.db import DatabaseManager


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuditLogger:
    """
    Unified audit log entrypoint.
    All important system events should be recorded through this logger.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def log_event(
        self,
        task_id: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> str:
        log_id = str(uuid4())
        self.db.save_audit_log(
            log_id=log_id,
            task_id=task_id,
            event_type=event_type,
            event_data=event_data,
            created_at=utc_now_iso(),
        )
        return log_id

    def log_state_change(
        self,
        task_id: str,
        from_state: str,
        to_state: str,
        trigger: str,
        reason: str,
    ) -> str:
        return self.log_event(
            task_id=task_id,
            event_type="state_change",
            event_data={
                "from_state": from_state,
                "to_state": to_state,
                "trigger": trigger,
                "reason": reason,
            },
        )

    def log_review_event(
        self,
        task_id: str,
        review_id: str,
        gate_type: str,
        review_status: str,
        reviewer: str,
    ) -> str:
        return self.log_event(
            task_id=task_id,
            event_type="review",
            event_data={
                "review_id": review_id,
                "gate_type": gate_type,
                "review_status": review_status,
                "reviewer": reviewer,
            },
        )

    def log_guard_failure(
        self,
        task_id: str,
        guard_type: str,
        severity: str,
        reason: str,
        action_taken: str,
    ) -> str:
        return self.log_event(
            task_id=task_id,
            event_type="guard_failure",
            event_data={
                "guard_type": guard_type,
                "severity": severity,
                "reason": reason,
                "action_taken": action_taken,
            },
        )

    def log_recovery(
        self,
        task_id: str,
        from_state: str,
        to_state: str,
        triggered_by: str,
        reason: str,
    ) -> str:
        return self.log_event(
            task_id=task_id,
            event_type="recovery",
            event_data={
                "from_state": from_state,
                "to_state": to_state,
                "triggered_by": triggered_by,
                "reason": reason,
            },
        )
