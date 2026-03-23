from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Task:
    task_id: str
    task_type: str
    workflow_type: str = "video_production"
    current_state: str = "planning"
    current_substate: str = ""
    status: str = "running"  # running | paused | completed | failed
    priority: int = 0
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    context: Dict[str, Any] = field(default_factory=dict)
    assigned_worker: str = ""

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaskStateHistory:
    task_id: str
    from_state: str
    to_state: str
    trigger: str  # review | worker | guard | system
    reason: str = ""
    created_at: datetime = field(default_factory=utc_now)
    record_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
