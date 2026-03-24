from dataclasses import dataclass, field
from typing import Any, Dict, List
import time
import uuid


def new_message_id() -> str:
    return f"msg_{uuid.uuid4().hex[:8]}"


@dataclass
class Message:
    version: str
    message_id: str
    message_type: str
    project_id: str
    task_id: str
    from_role: str
    to_role: str
    priority: str
    summary: str
    required_action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    requires_response: bool = False
    created_at: float = field(default_factory=time.time)
    status: str = "sent"

    @classmethod
    def create(
        cls,
        message_type: str,
        project_id: str,
        task_id: str,
        from_role: str,
        to_role: str,
        summary: str,
        required_action: str,
        payload: Dict[str, Any] | None = None,
        artifacts: List[str] | None = None,
        priority: str = "normal",
    ) -> "Message":
        return cls(
            version="1.0",
            message_id=new_message_id(),
            message_type=message_type,
            project_id=project_id,
            task_id=task_id,
            from_role=from_role,
            to_role=to_role,
            priority=priority,
            summary=summary,
            required_action=required_action,
            payload=payload or {},
            artifacts=artifacts or [],
        )
