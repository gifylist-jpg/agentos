from agentos.execution.openclaw_adapter import OpenClawAdapter


class ExecutionAdapter:
    def __init__(self) -> None:
        self.openclaw = OpenClawAdapter()

    def execute(self, payload: dict) -> dict:
        return self.openclaw.run(payload)
