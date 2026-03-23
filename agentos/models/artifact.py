from dataclasses import dataclass, field
from typing import Any, Dict
import time
import uuid


def new_artifact_id() -> str:
    return f"artifact_{uuid.uuid4().hex[:8]}"


@dataclass
class Artifact:
    artifact_id: str
    project_id: str
    task_id: str
    artifact_type: str
    name: str
    content: Dict[str, Any]
    created_by: str
    created_at: float = field(default_factory=time.time)

    @classmethod
    def create(
        cls,
        project_id: str,
        task_id: str,
        artifact_type: str,
        name: str,
        content: Dict[str, Any],
        created_by: str,
    ) -> "Artifact":
        return cls(
            artifact_id=new_artifact_id(),
            project_id=project_id,
            task_id=task_id,
            artifact_type=artifact_type,
            name=name,
            content=content,
            created_by=created_by,
        )
