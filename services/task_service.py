from __future__ import annotations

from typing import Any, Dict, List, Optional

from audit.audit_logger import AuditLogger
from guards.guard_manager import GuardManager
from models.asset import Asset, AssetDependency, AssetVersion
from models.review import ReviewRecord
from models.task import Task
from core.publish_record import PublishRecord
from core.performance_snapshot import PerformanceSnapshot
from services.feedback_builder import FeedbackBuilder, BaselineReference
from services.alert_service import AlertService
from services.asset_service import AssetService
from services.recovery_policy import RecoveryPolicy
from services.review_service import ReviewService
from services.state_manager import StateManager
from services.decision_control_service import DecisionControlService
from services.stuck_task_detector import StuckTaskDetector
from services.stuck_task_handler import StuckTaskHandler
from storage.db import DatabaseManager
from core.system_guard import assert_valid_control_outcome, assert_has_required_feedback_fields
from agentos.schemas.feedback_validator import validate_feedback_result
from agents.performance_analysis_agent import PerformanceAnalysisInput, AssetPerformanceSnapshot
from agents.performance_analysis_agent import PerformanceAnalysisAgent
from typing import Any, Dict, List, Optional


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
        self.decision_control_service = DecisionControlService()
        self.feedback_builder = FeedbackBuilder()

        self.audit_logger = AuditLogger(db)
        self.alert_service = AlertService(audit_logger=self.audit_logger)
        self.recovery_policy = RecoveryPolicy()
        self.stuck_task_detector = StuckTaskDetector(audit_logger=self.audit_logger)
        self.stuck_task_handler = StuckTaskHandler(
            detector=self.stuck_task_detector,
            alert_service=self.alert_service,
            recovery_policy=self.recovery_policy,
        )

    def _select_primary_asset_result(self, asset_results, publish_record):
        for r in asset_results:
            if r.variant_id == publish_record.variant_id:
                return r
        return asset_results[0] if asset_results else None

    def _adapt_asset_result_for_control(
        self,
        asset_result,
        publish_record,
    ):
        """
        临时桥接：
        把 PerformanceAnalysisAgent v3.2 的 AssetAnalysisResult
        适配成 DecisionControlService 需要的结构。
        """

        # suggestion -> action / decision_type / next_step
        if asset_result.suggestion == "WAIT_MORE_DATA":
            action = "WAIT_MORE_DATA"
            decision_type = "observation_only"
            recommended_next_step = "collect more snapshots before judging"
        elif asset_result.suggestion in ("AMPLIFY_CANDIDATE",):
            action = "SCALE_CANDIDATE"
            decision_type = "scale_candidate"
            recommended_next_step = "prepare controlled scale validation"
        elif asset_result.needs_human_review:
            action = "HUMAN_REVIEW"
            decision_type = "review_gate"
            recommended_next_step = "send to human review before any scale decision"
        elif asset_result.suggestion in (
            "RETEST_SAME_ANGLE_NEW_HOOK",
            "RETEST_SAME_HOOK_NEW_CTA",
        ):
            action = "RETEST"
            decision_type = "retest_candidate"
            recommended_next_step = "retest with adjusted variant or context"
        elif asset_result.suggestion in ("KEEP_OBSERVING", "KEEP"):
            action = "KEEP_OBSERVING"
            decision_type = "observation_only"
            recommended_next_step = "keep observing without strong intervention"
        else:
            action = "RETEST"
            decision_type = "analysis_output"
            recommended_next_step = "retest with adjusted variant or context"


    def run_feedback_loop(
        self,
        task: Task,
        publish_record: PublishRecord,
        snapshots: List[PerformanceSnapshot],
        baseline: BaselineReference,
        analysis_agent: PerformanceAnalysisAgent,
    ) -> Dict[str, Any]:
        """
        Minimal structured feedback loop:

        PublishRecord + Snapshots + Baseline
        -> FeedbackBuilder
        -> PerformanceAnalysisInput
        -> Analysis
        -> Decision Control
        -> feedback_result
        """

        feedback_bundle = self.feedback_builder.build_feedback_bundle(
            publish_record=publish_record,
            snapshots=snapshots,
            baseline=baseline,
        )

        aggregate = feedback_bundle.aggregate

        analysis_snapshots: List[AssetPerformanceSnapshot] = []

        for snap in snapshots:
            analysis_snapshots.append(
                AssetPerformanceSnapshot(
                    asset_id=publish_record.publish_id,
                    variant_id=publish_record.variant_id,
                    metrics={
                        "ctr": snap.ctr,
                        "watch_rate": snap.completion_rate,
                        "avg_watch_time": snap.watch_time,
                        "views": snap.impressions,
                        "cvr": snap.cvr,
                    },
                    timestamp=snap.captured_at.timestamp(),
                    publish_mode=publish_record.publish_mode,
                    account_id=publish_record.account_id,
                )
            )

        scoped_baseline = {
            baseline.baseline_scope: {
                "product": (
                    baseline.ads_baseline
                    if baseline.baseline_scope == "ads"
                    else baseline.organic_baseline
                )
            }
        }

        analysis_input = PerformanceAnalysisInput(
            product_id=publish_record.product_id,
            strategy_id=task.task_id,
            snapshots=analysis_snapshots,
            baseline=scoped_baseline,
        )

        analysis_output = analysis_agent.analyze(analysis_input)

        if not analysis_output.asset_results:
            feedback_result = {
                "analysis_result": analysis_output,
                "decision_record": None,
                "review_result": None,
                "freeze_result": None,
                "control_outcome": {
                    "status": "NO_RESULT",
                    "next_step": "no analysis result available",
                    "reason": "EMPTY_ASSET_RESULTS",
                },
            }

            assert_has_required_feedback_fields(feedback_result)
            validate_feedback_result(feedback_result)

            return feedback_result

        primary_asset_result = self._select_primary_asset_result(
            analysis_output.asset_results,
            publish_record,
        )

        control_bundle = self.decision_control_service.process(
            task_id=task.task_id,
            asset_result=primary_asset_result,
        )

        feedback_result = {
            "analysis_result": analysis_output,
            "primary_asset_result": primary_asset_result,
            "decision_record": control_bundle["decision_record"],
            "review_result": control_bundle["review_result"],
            "freeze_result": control_bundle["freeze_result"],
            "control_outcome": control_bundle["control_outcome"],
        }

        validate_feedback_result(feedback_result)
        return feedback_result

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
