from __future__ import annotations

from typing import Dict, Set

from core.exceptions import StateTransitionError
from models.task import Task, TaskStateHistory
from models.recovery import RecoveryRecord
from audit.audit_logger import AuditLogger
from storage.db import DatabaseManager


class StateManager:
    """
    Single entry point for task state transition.
    All task state updates must go through this manager.
    """

    ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
        "planning": {"script_ready"},
        "script_ready": {"waiting_review"},
        "waiting_review": {"approved", "planning"},
        "approved": {"executing"},
        "executing": {"completed", "approved", "failed"},
        "completed": set(),
        "rejected": set(),
        "failed": set(),
    }

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.audit_logger = AuditLogger(db)

    def can_transition(self, from_state: str, to_state: str) -> bool:
        allowed = self.ALLOWED_TRANSITIONS.get(from_state, set())
        return to_state in allowed

    def transition_task(
        self,
        task: Task,
        new_state: str,
        trigger: str,
        reason: str = "",
        new_substate: str = "",
    ) -> Task:
        if not self.can_transition(task.current_state, new_state):
            raise StateTransitionError(
                f"Illegal state transition: {task.current_state} -> {new_state}"
            )

        old_state = task.current_state
        task.current_state = new_state
        task.current_substate = new_substate
        task.touch()

        self.db.save_task(task)

        history = TaskStateHistory(
            task_id=task.task_id,
            from_state=old_state,
            to_state=new_state,
            trigger=trigger,
            reason=reason,
        )
        self.db.save_task_state_history(history)

        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="state_change",
            event_data={
                "task_id": task.task_id,
                "from_state": old_state,
                "to_state": new_state,
                "trigger": trigger,
                "reason": reason,
            },
        )

        return task

    def rollback_task(
        self,
        task: Task,
        rollback_to: str,
        reason: str,
        triggered_by: str = "system",
    ) -> Task:
        if not self.can_transition(task.current_state, rollback_to):
            raise StateTransitionError(
                f"Illegal rollback: {task.current_state} -> {rollback_to}"
            )

        old_state = task.current_state
        task.current_state = rollback_to
        task.current_substate = ""
        task.touch()

        self.db.save_task(task)

        history = TaskStateHistory(
            task_id=task.task_id,
            from_state=old_state,
            to_state=rollback_to,
            trigger="guard" if triggered_by == "guard" else "system",
            reason=reason,
        )
        self.db.save_task_state_history(history)

        recovery = RecoveryRecord(
            task_id=task.task_id,
            from_state=old_state,
            to_state=rollback_to,
            reason=reason,
            triggered_by=triggered_by,
        )
        self.db.save_recovery_record(recovery)

        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="recovery",
            event_data={
                "task_id": task.task_id,
                "from_state": old_state,
                "to_state": rollback_to,
                "trigger": "guard" if triggered_by == "guard" else "system",
                "reason": reason,
                "triggered_by": triggered_by,
            },
        )

        return task
