from agentos.execution.tool_executor import ToolExecutor
from agentos.execution.openclaw_adapter import OpenClawAdapter

class ExecutionAdapter:
    """
    ExecutionAdapter provides the unified entry point for execution.
    It can route execution requests to the correct tool or adapter based on the request.
    """

    def __init__(self):
        # Initialize ToolExecutor (or replace with other tool if needed)
        self.tool_executor = ToolExecutor()

    def execute(self, request: dict) -> dict:
        if not isinstance(request, dict):
            raise ValueError("Execution request must be a dictionary")

        payload = request.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Execution request must contain a dict payload")

        execution_mode = payload.get("execution_mode", "auto")
        
        if execution_mode == "auto":
            # Direct execution through tool_executor
            result = self.tool_executor.execute(payload)
        elif execution_mode == "manual":
            # Potentially queue for manual approval or processing
            result = self._handle_manual_execution(payload)
        elif execution_mode == "block":
            # Handle blocking case if needed (e.g., reject the task)
            result = {"status": "blocked", "message": "Execution blocked"}
        else:
            result = {"status": "failed", "message": "Unknown execution mode"}

        return {
            "status": "SUCCESS" if result["status"] != "blocked" else "FAILURE",
            "execution_result": result,
        }

    def _handle_manual_execution(self, payload):
        """
        Handle the 'manual' execution mode - for cases requiring human approval or queuing.
        """
        # Implement logic for queuing or awaiting manual approval
        return {
            "status": "pending",
            "message": "Execution awaiting manual approval",
        }
