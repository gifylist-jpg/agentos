from agentos.config.settings import WORKFLOW_SEQUENCE


class WorkflowEngine:
    def __init__(self) -> None:
        self.sequence = WORKFLOW_SEQUENCE

    def get_first_role(self) -> str:
        return self.sequence[0]

    def get_next_role(self, current_role: str) -> str | None:
        if current_role not in self.sequence:
            return None
        idx = self.sequence.index(current_role)
        if idx + 1 < len(self.sequence):
            return self.sequence[idx + 1]
        return None
