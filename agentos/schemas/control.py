from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from agentos.schemas.enums import Suggestion


class ControlStatus:
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    FROZEN = "FROZEN"


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    decision_id: str
    task_id: str
    variant_id: str

    action: Suggestion
    decision_type: str
    confidence: str

    review_required: bool
    freeze_candidate: bool
    memory_admission_candidate: bool

    diagnostics: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass(frozen=True, slots=True)
class ReviewResult:
    blocked: bool
    reason: Optional[str] = None


@dataclass(frozen=True, slots=True)
class FreezeResult:
    frozen: bool
    reason: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ControlOutcome:
    status: str
    next_step: str
    reason: Optional[str] = None

    def __post_init__(self):
        allowed = {
            ControlStatus.ALLOWED,
            ControlStatus.BLOCKED,
            ControlStatus.FROZEN,
        }
        if self.status not in allowed:
            raise ValueError(f"invalid control status: {self.status}")
