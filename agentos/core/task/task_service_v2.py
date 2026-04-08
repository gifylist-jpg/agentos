from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.decision.model_selector import ModelSelector
from agentos.execution.execution_adapter import ExecutionAdapter

class TaskServiceV2:
    def __init__(self, model_selector: ModelSelector, execution_adapter: ExecutionAdapter):
        self.decision_service = MultiModelDecisionService(model_selector)
        self.execution_adapter = execution_adapter

    def process_task(self, task_data, manual_model=None):
        # 自动选择模型或手动指定模型
        if manual_model:
            task_data["model"] = manual_model
        else:
            task_type = task_data.get("task_type")
            task_data["model"] = "DeepSeek" if task_type == "simple_task" else "Claude"

        decision = self.decision_service.generate_decision(task_data)

        if task_data.get("task_type") == "simple_task":
            decision["execution_mode"] = "auto"
        else:
            decision["execution_mode"] = "manual"  # Example: Set manual for other tasks

        # 通过 ExecutionAdapter 执行任务
        execution_result = self.execution_adapter.execute({
            "payload": {
                "action": decision["action"],
                "execution_mode": decision["execution_mode"],
                "steps": decision.get("steps", [])
            }
        })

        return ApprovedDecision(
            execution_mode=execution_result['execution_result']['status'],
            selected_candidate_id=decision.get('selected_candidate_id')
        )
