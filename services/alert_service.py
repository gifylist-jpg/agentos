from __future__ import annotations

from typing import Any

from audit.audit_logger import AuditLogger


class AlertService:
    def __init__(self, audit_logger: AuditLogger) -> None:
        self.audit_logger = audit_logger

    def record_alert(
        self,
        *,
        task_id: str,
        alert_type: str,
        severity: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.audit_logger.log_event(
            task_id=task_id,
            event_type="alert",
            event_data={
                "task_id": task_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "details": details,
            },
        )
