from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class GuardFailure:
    task_id: str
    guard_type: str  # contract | state | write
    severity: str  # L1 | L2 | L3 | L4
    reason: str
    details: str = ""
    action_taken: str = ""  # retry | rollback | block | alert
    created_at: datetime = field(default_factory=utc_now)
    guard_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)
