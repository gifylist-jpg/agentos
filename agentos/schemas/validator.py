from __future__ import annotations

from typing import Iterable

from agentos.schemas.analysis import AssetAnalysisResult, PerformanceAnalysisOutput
from agentos.schemas.enums import (
    Stage,
    SignalStatus,
    Strength,
    Confidence,
    NoiseLevel,
    Suggestion,
)


def validate_asset_analysis_result(result: AssetAnalysisResult) -> None:
    if not isinstance(result, AssetAnalysisResult):
        raise TypeError("result must be AssetAnalysisResult")

    if not result.asset_id:
        raise ValueError("asset_id is required")

    if not result.variant_id:
        raise ValueError("variant_id is required")

    if not isinstance(result.stage, Stage):
        raise TypeError(f"stage must be Stage, got {type(result.stage).__name__}")

    if not isinstance(result.signal_status, SignalStatus):
        raise TypeError(
            f"signal_status must be SignalStatus, got {type(result.signal_status).__name__}"
        )

    if not isinstance(result.distribution_status, Strength):
        raise TypeError(
            f"distribution_status must be Strength, got {type(result.distribution_status).__name__}"
        )

    if not isinstance(result.creative_status, Strength):
        raise TypeError(
            f"creative_status must be Strength, got {type(result.creative_status).__name__}"
        )

    if not isinstance(result.commercial_status, Strength):
        raise TypeError(
            f"commercial_status must be Strength, got {type(result.commercial_status).__name__}"
        )

    if not isinstance(result.causal_confidence, Confidence):
        raise TypeError(
            f"causal_confidence must be Confidence, got {type(result.causal_confidence).__name__}"
        )

    if not isinstance(result.environment_noise, NoiseLevel):
        raise TypeError(
            f"environment_noise must be NoiseLevel, got {type(result.environment_noise).__name__}"
        )

    if not isinstance(result.suggestion, Suggestion):
        raise TypeError(
            f"suggestion must be Suggestion, got {type(result.suggestion).__name__}"
        )

    if not result.reason:
        raise ValueError("reason is required")

    if result.needs_human_review and not result.review_reason:
        raise ValueError("review_reason required when needs_human_review=True")

    if result.should_freeze_task and not result.freeze_reason:
        raise ValueError("freeze_reason required when should_freeze_task=True")


def validate_analysis_output(output: PerformanceAnalysisOutput) -> None:
    if not isinstance(output, PerformanceAnalysisOutput):
        raise TypeError("output must be PerformanceAnalysisOutput")

    if not output.analysis_id:
        raise ValueError("analysis_id is required")

    if not output.strategy_id:
        raise ValueError("strategy_id is required")

    if not output.product_id:
        raise ValueError("product_id is required")

    if not isinstance(output.asset_results, list):
        raise TypeError("asset_results must be a list")

    if not output.asset_results:
        raise ValueError("asset_results must be non-empty")

    for result in output.asset_results:
        validate_asset_analysis_result(result)

    if not output.recommended_next_action:
        raise ValueError("recommended_next_action is required")

    if not output.summary:
        raise ValueError("summary is required")


def validate_analysis_results(results: Iterable[AssetAnalysisResult]) -> None:
    for result in results:
        validate_asset_analysis_result(result)
