from __future__ import annotations

from typing import Any, Dict, List

from models.task import Task
from services.alert_service import AlertService
from services.recovery_policy import RecoveryPolicy
from services.stuck_task_detector import StuckTaskDetector


class StuckTaskHandler:
    """
    Minimal integration handler:
    StuckTaskDetector -> AlertService -> RecoveryPolicy

    This version only:
    - detects stuck tasks
    - records alert
    - returns suggested recovery action

    It does NOT:
    - modify task state
    - call TaskService
    - auto-recover
    """

    SEVERITY_BY_STATE = {
        "waiting_review": "L2",
        "executing": "L3",
    }

    def __init__(
        self,
        *,
        detector: StuckTaskDetector,
        alert_service: AlertService,
        recovery_policy: RecoveryPolicy,
    ) -> None:
        self.detector = detector
        self.alert_service = alert_service
        self.recovery_policy = recovery_policy

    def handle(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        stuck_tasks = self.detector.detect_stuck_tasks(tasks)
        results: List[Dict[str, Any]] = []

        for task in stuck_tasks:
            severity = self.SEVERITY_BY_STATE.get(task.current_state, "L2")
            action = self.recovery_policy.get_action(
                severity=severity,
                error_type="task_stuck",
            )

            self.alert_service.record_alert(
                task_id=task.task_id,
                alert_type="task_stuck",
                severity=severity,
                message=f"Task stuck in state: {task.current_state}",
                details={
                    "state": task.current_state,
                    "suggested_action": action,
                },
            )

            results.append(
                {
                    "task_id": task.task_id,
                    "state": task.current_state,
                    "severity": severity,
                    "action": action,
                }
            )

        return results
