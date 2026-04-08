class ExecutionAdapter:
    """
    P1 Minimal ExecutionAdapter

    Current goal:
    - Provide unified execution entry point
    - Compatible with existing ToolExecutor
    - Do not change old bypass logic
    """

    def __init__(self):
        from agentos.execution.tool_executor import ToolExecutor
        self.tool_executor = ToolExecutor()

    def execute(self, request: dict) -> dict:
        if not isinstance(request, dict):
            raise ValueError("Execution request must be a dict")

        payload = request.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Execution request must contain a dict payload")

        result = self.tool_executor.execute(payload)

        return {
            "status": "SUCCESS",
            "execution_result": result,
        }
