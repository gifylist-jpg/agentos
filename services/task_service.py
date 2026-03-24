from __future__ import annotations

from typing import Any, Dict, Optional

from audit.audit_logger import AuditLogger
from guards.guard_manager import GuardManager
from models.asset import Asset, AssetDependency, AssetVersion
from models.review import ReviewRecord
from models.task import Task
from services.asset_service import AssetService
from services.review_service import ReviewService
from services.state_manager import StateManager
from storage.db import DatabaseManager


class TaskService:
    """
    Unified legal entrypoint for task operations.

    All higher-level executors (workers / OpenClaw / tools) should go through this service
    instead of directly touching db / state / review / asset internals.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.audit_logger = AuditLogger(db)
        self.state_manager = StateManager(db)
        self.review_service = ReviewService(db, self.state_manager)
        self.asset_service = AssetService(db)
        self.guard_manager = GuardManager(db)

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
        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="task_created",
            event_data={
                "task_id": task.task_id,
                "task_type": task.task_type,
            },
        )
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

        old_state = task.current_state
        transitioned_task = self.state_manager.transition_task(
            task=task,
            new_state=new_state,
            trigger=trigger,
            reason=reason,
            new_substate=new_substate,
        )
        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="task_transition",
            event_data={
                "task_id": task.task_id,
                "from_state": old_state,
                "to_state": new_state,
                "trigger": trigger,
                "reason": reason,
            },
        )
        return transitioned_task

    def submit_review(
        self,
        task: Task,
        review: ReviewRecord,
    ) -> Task:
        self.guard_manager.validate_review_contract(task, review)
        self.guard_manager.validate_asset_exists(task.task_id, review.asset_id)
        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="review_submission_requested",
            event_data={
                "task_id": task.task_id,
                "asset_id": review.asset_id,
                "trigger": review.gate_type,
                "reason": review.reason,
            },
        )
        result_task = self.review_service.submit_review(task, review)
        self.audit_logger.log_event(
            task_id=task.task_id,
            event_type="review_submission",
            event_data={
                "task_id": task.task_id,
                "asset_id": review.asset_id,
                "trigger": review.gate_type,
                "reason": review.reason,
            },
        )
        return result_task

    def create_asset(
        self,
        task_id: str,
        asset_type: str,
        status: str = "draft",
    ) -> Asset:
        asset = self.asset_service.create_asset(
            task_id=task_id,
            asset_type=asset_type,
            status=status,
        )
        self.audit_logger.log_event(
            task_id=task_id,
            event_type="asset_created",
            event_data={
                "task_id": task_id,
                "asset_id": asset.asset_id,
            },
        )
        return asset

    def create_asset_version(
        self,
        asset_id: str,
        version: int,
        data: Dict[str, Any],
        created_by: str,
    ) -> AssetVersion:
        asset_version = self.asset_service.create_asset_version(
            asset_id=asset_id,
            version=version,
            data=data,
            created_by=created_by,
        )
        self.audit_logger.log_event(
            task_id="",
            event_type="asset_version_created",
            event_data={
                "asset_id": asset_id,
            },
        )
        return asset_version

    def add_asset_dependency(
        self,
        task_id: str,
        asset_id: str,
        depends_on: str,
        relation_type: str = "derived_from",
    ) -> AssetDependency:
        self.guard_manager.validate_asset_exists(task_id, asset_id)
        self.guard_manager.validate_asset_exists(task_id, depends_on)

        dependency = self.asset_service.add_dependency(
            asset_id=asset_id,
            depends_on=depends_on,
            relation_type=relation_type,
        )
        self.audit_logger.log_event(
            task_id=task_id,
            event_type="asset_dependency_added",
            event_data={
                "asset_id": asset_id,
                "depends_on": depends_on,
            },
        )
        return dependency

    def update_asset_status(
        self,
        asset_id: str,
        new_status: str,
    ) -> None:
        self.asset_service.update_asset_status(asset_id, new_status)
        self.audit_logger.log_event(
            task_id="",
            event_type="asset_status_updated",
            event_data={
                "asset_id": asset_id,
                "new_status": new_status,
            },
        )
