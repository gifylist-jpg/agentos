from dataclasses import dataclass, field
from typing import Any, Dict, List
import time
import uuid


def new_task_id() -> str:
    return f"task_{uuid.uuid4().hex[:8]}"


@dataclass
class Task:
    task_id: str
    project_id: str
    task_type: str
    title: str
    owner_role: str
    target_role: str
    status: str = "created"
    depends_on: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @classmethod
    def create(
        cls,
        project_id: str,
        task_type: str,
        title: str,
        owner_role: str,
        target_role: str,
        payload: Dict[str, Any] | None = None,
        depends_on: List[str] | None = None,
    ) -> "Task":
        return cls(
            task_id=new_task_id(),
            project_id=project_id,
            task_type=task_type,
            title=title,
            owner_role=owner_role,
            target_role=target_role,
            payload=payload or {},
            depends_on=depends_on or [],
        )
