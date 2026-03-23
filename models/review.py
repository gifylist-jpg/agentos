from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ReviewRecord:
    task_id: str
    asset_id: str
    gate_type: str  # script | clip | rough_cut | final
    review_mode: str  # ai | human | hybrid
    review_status: str  # approved | rejected
    score: float = 0.0
    reason: str = ""
    suggestions: str = ""
    reviewer: str = ""
    state_before: str = ""
    state_after: str = ""
    rollback_target: str = ""
    created_at: datetime = field(default_factory=utc_now)
    review_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)
