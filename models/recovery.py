from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class RecoveryRecord:
    task_id: str
    from_state: str
    to_state: str
    reason: str
    triggered_by: str  # review | guard | system
    created_at: datetime = field(default_factory=utc_now)
    recovery_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)
