from __future__ import annotations

from typing import Any, Dict

from agentos.schemas.analysis import AssetAnalysisResult
from agentos.schemas.control import DecisionRecord
from agentos.schemas.enums import Suggestion
import uuid


def map_suggestion_to_decision_type(suggestion: Suggestion) -> str:
    if suggestion == Suggestion.WAIT_MORE_DATA:
        return "observation_only"
    if suggestion == Suggestion.KEEP_OBSERVING:
        return "observation_only"
    if suggestion == Suggestion.KEEP:
        return "observation_only"
    if suggestion == Suggestion.AMPLIFY_CANDIDATE:
        return "scale_candidate"
    if suggestion == Suggestion.FREEZE:
        return "freeze"
    return "review_gate"


def build_decision_record(
    task_id: str,
    asset_result: AssetAnalysisResult,
) -> DecisionRecord:
    return DecisionRecord(
        decision_id=str(uuid.uuid4()),
        task_id=task_id,
        variant_id=asset_result.variant_id,
        action=asset_result.suggestion,
        decision_type=map_suggestion_to_decision_type(asset_result.suggestion),
        confidence=asset_result.causal_confidence.value,
        review_required=asset_result.needs_human_review,
        freeze_candidate=asset_result.should_freeze_task,
        memory_admission_candidate=asset_result.memory_admission_ready,
        diagnostics={
            "stage": asset_result.stage.value,
            "signal_status": asset_result.signal_status.value,
            "distribution_status": asset_result.distribution_status.value,
            "creative_status": asset_result.creative_status.value,
            "commercial_status": asset_result.commercial_status.value,
            "environment_noise": asset_result.environment_noise.value,
            "reason": asset_result.reason,
        },
        metadata={},
    )
