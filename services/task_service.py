from __future__ import annotations

from typing import Any, Dict, List, Optional

from audit.audit_logger import AuditLogger
from guards.guard_manager import GuardManager
from models.asset import Asset, AssetDependency, AssetVersion
from models.review import ReviewRecord
from models.task import Task
from services.alert_service import AlertService
from services.asset_service import AssetService
from services.recovery_policy import RecoveryPolicy
from services.review_service import ReviewService
from services.state_manager import StateManager
from services.stuck_task_detector import StuckTaskDetector
from services.stuck_task_handler import StuckTaskHandler
from storage.db import DatabaseManager


class TaskService:
    """
    Unified legal entrypoint for task operations.

    All higher-level executors (workers / OpenClaw / tools) should go through this service
    instead of directly touching db / state / review / asset internals.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.state_manager = StateManager(db)
        self.review_service = ReviewService(db, self.state_manager)
        self.asset_service = AssetService(db)
        self.guard_manager = GuardManager(db)

        self.audit_logger = AuditLogger(db)
        self.alert_service = AlertService(audit_logger=self.audit_logger)
        self.recovery_policy = RecoveryPolicy()
        self.stuck_task_detector = StuckTaskDetector(audit_logger=self.audit_logger)
        self.stuck_task_handler = StuckTaskHandler(
            detector=self.stuck_task_detector,
            alert_service=self.alert_service,
            recovery_policy=self.recovery_policy,
        )

    def create_task(
        self,
        task_id: str,
        task_type: str,
        workflow_type: str = "video_production",
        priority: int = 0,
        context: Optional[Dict[str, Any]] = None,
        assigned_worker: str = "",
    ) -> Task:
        task = Task(
            task_id=task_id,
            task_type=task_type,
            workflow_type=workflow_type,
            priority=priority,
            context=context or {},
            assigned_worker=assigned_worker,
        )
        self.db.save_task(task)
        return task

    def get_task(self, task_id: str) -> Optional[dict]:
        row = self.db.fetch_one(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        )
        return dict(row) if row else None

    def transition_task(
        self,
        task: Task,
        new_state: str,
        trigger: str,
        reason: str = "",
        new_substate: str = "",
    ) -> Task:
        allowed = self.state_manager.can_transition(task.current_state, new_state)
        self.guard_manager.validate_state_transition(
            task=task,
            from_state=task.current_state,
            to_state=new_state,
            allowed=allowed,
        )

        return self.state_manager.transition_task(
            task=task,
            new_state=new_state,
            trigger=trigger,
            reason=reason,
            new_substate=new_substate,
        )

    def submit_review(
        self,
        task: Task,
        review: ReviewRecord,
    ) -> Task:
        self.guard_manager.validate_review_contract(task, review)
        self.guard_manager.validate_asset_exists(task.task_id, review.asset_id)

        return self.review_service.submit_review(task, review)

    def create_asset(
        self,
        task_id: str,
        asset_type: str,
        status: str = "draft",
    ) -> Asset:
        return self.asset_service.create_asset(
            task_id=task_id,
            asset_type=asset_type,
            status=status,
        )

    def create_asset_version(
        self,
        asset_id: str,
        version: int,
        data: Dict[str, Any],
        created_by: str,
    ) -> AssetVersion:
        return self.asset_service.create_asset_version(
            asset_id=asset_id,
            version=version,
            data=data,
            created_by=created_by,
        )

    def add_asset_dependency(
        self,
        task_id: str,
        asset_id: str,
        depends_on: str,
        relation_type: str = "derived_from",
    ) -> AssetDependency:
        self.guard_manager.validate_asset_exists(task_id, asset_id)
        self.guard_manager.validate_asset_exists(task_id, depends_on)

        return self.asset_service.add_dependency(
            asset_id=asset_id,
            depends_on=depends_on,
            relation_type=relation_type,
        )

    def update_asset_status(
        self,
        asset_id: str,
        new_status: str,
    ) -> None:
        self.asset_service.update_asset_status(asset_id, new_status)

    def check_and_handle_stuck_tasks(
        self,
        tasks: List[Task],
    ) -> List[Dict[str, Any]]:
        """
        Explicit legal entrypoint for stuck task handling.

        This method:
        - does NOT modify task state
        - does NOT auto-recover
        - only returns structured handling suggestions
        """
        return self.stuck_task_handler.handle(tasks)
