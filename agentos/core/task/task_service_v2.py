from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.decision.model_selector import ModelSelector

class TaskServiceV2:
    def __init__(self, model_selector: ModelSelector):
        self.decision_service = MultiModelDecisionService(model_selector)

    def process_task(self, task_data, manual_model=None):
        # 如果手动指定模型，则覆盖自动选择
        if manual_model:
            task_data["model"] = manual_model
        decision = self.decision_service.generate_decision(task_data)
        return ApprovedDecision(execution_mode=decision['execution_mode'], selected_candidate_id=decision['selected_candidate_id'])
