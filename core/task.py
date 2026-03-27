from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class BusinessState:
    PLANNING = "planning"
    SCRIPT_READY = "script_ready"
    WAITING_REVIEW = "waiting_review"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    task_type: str
    goal: str
    input_payload: Dict[str, Any]
    business_state: str = BusinessState.PLANNING
    priority: str = "normal"
    source: str = "user"
    parent_task_id: Optional[str] = None
    run_id: str = field(default_factory=lambda: new_id("run"))
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    # 预留字段：后面接完整系统时直接补，不用返工
    current_substate: Optional[str] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    review_required: bool = False
    review_status: Optional[str] = None
    is_frozen: bool = False
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        task_type: str,
        goal: str,
        input_payload: Dict[str, Any],
        source: str = "user",
        parent_task_id: Optional[str] = None,
    ) -> "Task":
        return cls(
            task_id=new_id("task"),
            task_type=task_type,
            goal=goal,
            input_payload=input_payload,
            source=source,
            parent_task_id=parent_task_id,
        )

    def set_state(self, business_state: str, substate: Optional[str] = None) -> None:
        self.business_state = business_state
        if substate is not None:
            self.current_substate = substate
        self.updated_at = now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
