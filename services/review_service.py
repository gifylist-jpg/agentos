from __future__ import annotations

from models.review import ReviewRecord
from models.task import Task
from services.state_manager import StateManager
from storage.db import DatabaseManager


class ReviewService:
    """
    Review-driven state transition service.
    All review results should be submitted through this service.
    """

    def __init__(self, db: DatabaseManager, state_manager: StateManager) -> None:
        self.db = db
        self.state_manager = state_manager

    def submit_review(self, task: Task, review: ReviewRecord) -> Task:
        """
        Save review first, then drive state transition by gate_type + review_status.
        """
        self.db.save_review(review)

        gate_type = review.gate_type
        review_status = review.review_status

        if gate_type == "script":
            return self._handle_script_review(task, review_status, review)

        if gate_type == "clip":
            return self._handle_clip_review(task, review_status, review)

        if gate_type == "rough_cut":
            return self._handle_rough_cut_review(task, review_status, review)

        if gate_type == "final":
            return self._handle_final_review(task, review_status, review)

        raise ValueError(f"Unsupported gate_type: {gate_type}")

    def _handle_script_review(
        self,
        task: Task,
        review_status: str,
        review: ReviewRecord,
    ) -> Task:
        if review_status == "approved":
            return self.state_manager.transition_task(
                task=task,
                new_state="approved",
                trigger="review",
                reason=f"script review approved: {review.reason}",
                new_substate="",
            )

        if review_status == "rejected":
            return self.state_manager.rollback_task(
                task=task,
                rollback_to="planning",
                reason=f"script review rejected: {review.reason}",
                triggered_by="review",
            )

        raise ValueError(f"Unsupported review_status for script: {review_status}")

    def _handle_clip_review(
        self,
        task: Task,
        review_status: str,
        review: ReviewRecord,
    ) -> Task:
        if review_status == "approved":
            # clip 审核通过，不改变 approved 主状态
            return task

        if review_status == "rejected":
            return self.state_manager.rollback_task(
                task=task,
                rollback_to="approved",
                reason=f"clip review rejected: {review.reason}",
                triggered_by="review",
            )

        raise ValueError(f"Unsupported review_status for clip: {review_status}")

    def _handle_rough_cut_review(
        self,
        task: Task,
        review_status: str,
        review: ReviewRecord,
    ) -> Task:
        if review_status == "approved":
            return task

        if review_status == "rejected":
            return self.state_manager.rollback_task(
                task=task,
                rollback_to="approved",
                reason=f"rough cut review rejected: {review.reason}",
                triggered_by="review",
            )

        raise ValueError(f"Unsupported review_status for rough_cut: {review_status}")

    def _handle_final_review(
        self,
        task: Task,
        review_status: str,
        review: ReviewRecord,
    ) -> Task:
        if review_status == "approved":
            return self.state_manager.transition_task(
                task=task,
                new_state="completed",
                trigger="review",
                reason=f"final review approved: {review.reason}",
                new_substate="",
            )

        if review_status == "rejected":
            return self.state_manager.rollback_task(
                task=task,
                rollback_to="approved",
                reason=f"final review rejected: {review.reason}",
                triggered_by="review",
            )

        raise ValueError(f"Unsupported review_status for final: {review_status}")
