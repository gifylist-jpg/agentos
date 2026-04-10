from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.decision.model_selector import ModelSelector
from agentos.execution.execution_adapter import ExecutionAdapter


class TaskServiceV2:
    def __init__(self, model_selector: ModelSelector | None = None):
        self.decision_service = MultiModelDecisionService(model_selector)
        self.execution_adapter = ExecutionAdapter()

    def process_task(self, task_data, manual_model=None):
        # 如果手动指定模型，则覆盖自动选择
        if manual_model:
            task_data["model"] = manual_model
        else:
            # 自动根据任务类型选择模型
            task_type = task_data.get("task_type")
            if task_type == "simple_task":
                task_data["model"] = "DeepSeek"
            else:
                task_data["model"] = "Claude"

        # 生成决策
        decision = self.decision_service.generate_decision(task_data)

        # simple_task 强制 auto
        if task_data.get("task_type") == "simple_task":
            decision["execution_mode"] = "auto"

        return ApprovedDecision(
            execution_mode=decision["execution_mode"],
            selected_candidate_id=decision["selected_candidate_id"],
        )

    def _build_execution_request(self, task_data, decision: ApprovedDecision) -> dict:
        task_type = task_data.get("task_type", "unknown_task")
        steps = task_data.get("steps", [f"execute_{task_type}"])

        return {
            "payload": {
                "action": f"execute_{task_type}",
                "steps": steps,
                "decision": {
                    "execution_mode": decision.execution_mode,
                    "selected_candidate_id": decision.selected_candidate_id,
                },
            }
        }

    def process_task_and_execute(self, task_data, manual_model=None):
        decision = self.process_task(task_data, manual_model=manual_model)
        request = self._build_execution_request(task_data, decision)
        execution = self.execution_adapter.execute(request)

        return {
            "decision": decision,
            "execution": execution,
        }

# Ensure that ExecutionAdapter is called with the right execution mode
