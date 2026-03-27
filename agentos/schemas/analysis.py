from dataclasses import dataclass
from typing import Optional, List

from agentos.schemas.enums import (
    Stage,
    SignalStatus,
    Strength,
    Confidence,
    NoiseLevel,
    Suggestion,
)


@dataclass(frozen=True, slots=True)
class AssetAnalysisResult:
    asset_id: str
    variant_id: str

    stage: Stage
    signal_status: SignalStatus

    distribution_status: Strength
    creative_status: Strength
    commercial_status: Strength

    causal_confidence: Confidence
    environment_noise: NoiseLevel

    data_trust: str
    data_status: str
    freshness_level: str

    suggestion: Suggestion
    reason: str

    needs_human_review: bool
    review_reason: Optional[str]

    should_freeze_task: bool
    freeze_reason: Optional[str]

    memory_candidate: bool
    memory_admission_ready: bool

    def __post_init__(self):
        object.__setattr__(self, "stage", Stage.validate(self.stage))
        object.__setattr__(self, "signal_status", SignalStatus.validate(self.signal_status))

        object.__setattr__(self, "distribution_status", Strength.validate(self.distribution_status))
        object.__setattr__(self, "creative_status", Strength.validate(self.creative_status))
        object.__setattr__(self, "commercial_status", Strength.validate(self.commercial_status))

        object.__setattr__(self, "causal_confidence", Confidence.validate(self.causal_confidence))
        object.__setattr__(self, "environment_noise", NoiseLevel.validate(self.environment_noise))

        object.__setattr__(self, "suggestion", Suggestion.validate(self.suggestion))

        if not self.asset_id:
            raise ValueError("asset_id is required")

        if not self.variant_id:
            raise ValueError("variant_id is required")

        if self.needs_human_review and not self.review_reason:
            raise ValueError("review_reason required when needs_human_review=True")

        if self.should_freeze_task and not self.freeze_reason:
            raise ValueError("freeze_reason required when should_freeze_task=True")


@dataclass(frozen=True, slots=True)
class PerformanceAnalysisOutput:
    analysis_id: str
    strategy_id: str
    product_id: str

    asset_results: List[AssetAnalysisResult]

    recommended_next_action: str
    summary: str

    def __post_init__(self):
        if not self.analysis_id:
            raise ValueError("analysis_id required")

        if not isinstance(self.asset_results, list) or not self.asset_results:
            raise ValueError("asset_results must be non-empty list")

        for r in self.asset_results:
            if not isinstance(r, AssetAnalysisResult):
                raise TypeError("asset_results must contain AssetAnalysisResult")
