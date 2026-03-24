from typing import Dict
from agentos.models.artifact import Artifact


class ArtifactStore:
    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    def save(self, artifact: Artifact) -> str:
        self._artifacts[artifact.artifact_id] = artifact
        return artifact.artifact_id

    def get(self, artifact_id: str) -> Artifact:
        return self._artifacts[artifact_id]

    def list_all(self) -> list[Artifact]:
        return list(self._artifacts.values())
