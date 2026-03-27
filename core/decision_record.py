from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class DecisionRecord:
    decision_id: str
    task_id: str
    decision_type: str
    decider: str
    input_refs: List[str]
    decision_result: Dict[str, Any]
    reason: str
    created_at: str = field(default_factory=now_iso)

    # 预留字段
    confidence: float = 0.0
    known_factors: List[str] = field(default_factory=list)
    unknown_factors: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    decision_status: str = "confident"

    @classmethod
    def create(
        cls,
        task_id: str,
        decision_type: str,
        decider: str,
        input_refs: List[str],
        decision_result: Dict[str, Any],
        reason: str,
        confidence: float = 0.0,
    ) -> "DecisionRecord":
        return cls(
            decision_id=new_id("decision"),
            task_id=task_id,
            decision_type=decision_type,
            decider=decider,
            input_refs=input_refs,
            decision_result=decision_result,
            reason=reason,
            confidence=confidence,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
