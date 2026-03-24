from __future__ import annotations

from audit.audit_logger import AuditLogger
from models.guard import GuardFailure
from models.review import ReviewRecord
from models.task import Task
from storage.db import DatabaseManager
from core.guard_exceptions import GuardValidationError


class GuardManager:
    """
    First version of guard layer:
    - contract validation
    - state validation
    - dependency existence validation
    """

    VALID_REVIEW_GATE_TYPES = {"script", "clip", "rough_cut", "final"}
    VALID_REVIEW_MODES = {"ai", "human", "hybrid"}
    VALID_REVIEW_STATUSES = {"approved", "rejected"}

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self.audit_logger = AuditLogger(db)

    def _record_failure(
        self,
        task_id: str,
        guard_type: str,
        severity: str,
        reason: str,
        details: str,
        action_taken: str,
    ) -> GuardFailure:
        failure = GuardFailure(
            task_id=task_id,
            guard_type=guard_type,
            severity=severity,
            reason=reason,
            details=details,
            action_taken=action_taken,
        )
        self.db.save_guard_failure(failure)
        self.audit_logger.log_event(
            task_id=task_id,
            event_type="guard_failure",
            event_data={
                "rule": guard_type,
                "severity": severity,
                "task_id": task_id,
            },
        )
        return failure

    def validate_state_transition(
        self,
        task: Task,
        from_state: str,
        to_state: str,
        allowed: bool,
    ) -> None:
        if allowed:
            return

        self._record_failure(
            task_id=task.task_id,
            guard_type="state",
            severity="L3",
            reason="illegal state transition",
            details=f"{from_state} -> {to_state}",
            action_taken="block",
        )
        raise GuardValidationError(f"Illegal state transition: {from_state} -> {to_state}")

    def validate_review_contract(
        self,
        task: Task,
        review: ReviewRecord,
    ) -> None:
        if review.gate_type not in self.VALID_REVIEW_GATE_TYPES:
            self._record_failure(
                task_id=task.task_id,
                guard_type="contract",
                severity="L2",
                reason="invalid review gate_type",
                details=review.gate_type,
                action_taken="block",
            )
            raise GuardValidationError(f"Invalid review gate_type: {review.gate_type}")

        if review.review_mode not in self.VALID_REVIEW_MODES:
            self._record_failure(
                task_id=task.task_id,
                guard_type="contract",
                severity="L2",
                reason="invalid review mode",
                details=review.review_mode,
                action_taken="block",
            )
            raise GuardValidationError(f"Invalid review mode: {review.review_mode}")

        if review.review_status not in self.VALID_REVIEW_STATUSES:
            self._record_failure(
                task_id=task.task_id,
                guard_type="contract",
                severity="L2",
                reason="invalid review status",
                details=review.review_status,
                action_taken="block",
            )
            raise GuardValidationError(f"Invalid review status: {review.review_status}")

        if not review.asset_id:
            self._record_failure(
                task_id=task.task_id,
                guard_type="contract",
                severity="L2",
                reason="missing review asset_id",
                details="asset_id is empty",
                action_taken="block",
            )
            raise GuardValidationError("Review asset_id is required")

    def validate_asset_exists(
        self,
        task_id: str,
        asset_id: str,
    ) -> None:
        row = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,),
        )
        if row is not None:
            return

        self._record_failure(
            task_id=task_id,
            guard_type="write",
            severity="L2",
            reason="asset not found",
            details=asset_id,
            action_taken="block",
        )
        raise GuardValidationError(f"Asset not found: {asset_id}")
