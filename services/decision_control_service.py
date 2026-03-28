from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from agentos.schemas.control_invariant_checker import check_control_invariants
from agentos.schemas.analysis import AssetAnalysisResult
from agentos.schemas.control import (
    DecisionRecord,
    ReviewResult,
    FreezeResult,
    ControlOutcome,
)
from agentos.schemas.control_fsm import map_to_control_outcome
from services.analysis_control_adapter import build_decision_record


class DecisionControlService:
    def process(self, task_id: str, asset_result: AssetAnalysisResult) -> Dict[str, Any]:
        decision_record: DecisionRecord = build_decision_record(
            task_id=task_id,
            asset_result=asset_result,
        )

        review_result = ReviewResult(
            blocked=decision_record.review_required,
            reason="review_required=True" if decision_record.review_required else None,
        )

        freeze_result = FreezeResult(
            frozen=decision_record.freeze_candidate,
            reason="freeze_candidate=True" if decision_record.freeze_candidate else None,
        )

        control_outcome: ControlOutcome = map_to_control_outcome(
            review_required=decision_record.review_required,
            freeze_candidate=decision_record.freeze_candidate,
        )

        check_control_invariants(asdict(control_outcome), decision_record)

        return {
            "decision_record": asdict(decision_record),
            "review_result": asdict(review_result),
            "freeze_result": asdict(freeze_result),
            "control_outcome": asdict(control_outcome),
        }
