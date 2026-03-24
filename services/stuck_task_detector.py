from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Dict, List

from models.task import Task


class StuckTaskDetector:
    THRESHOLDS_SECONDS: Dict[str, int] = {
        "waiting_review": 300,
        "executing": 600,
    }

    def __init__(
        self,
        audit_logger,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.audit_logger = audit_logger
        self.now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def detect_stuck_tasks(self, tasks: List[Task]) -> List[Task]:
        now = self.now_provider()
        stuck_tasks: List[Task] = []

        for task in tasks:
            threshold = self.THRESHOLDS_SECONDS.get(task.current_state)
            if threshold is None:
                continue

            duration = int((now - task.updated_at).total_seconds())
            if duration <= threshold:
                continue

            self.audit_logger.log_event(
                task_id=task.task_id,
                event_type="task_stuck",
                event_data={
                    "task_id": task.task_id,
                    "state": task.current_state,
                    "duration": duration,
                },
            )
            stuck_tasks.append(task)

        return stuck_tasks
