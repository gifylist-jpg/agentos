from unittest.mock import MagicMock
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.model_selector import ModelSelector

def test_task_service_integration():
    task_data = {"task_type": "simple_task"}

    model_selector = ModelSelector()
    task_service = TaskServiceV2(model_selector)

    decision = task_service.process_task(task_data)
    assert decision.execution_mode == "auto"
    assert decision.selected_candidate_id is not None

    decision_manual = task_service.process_task(task_data, manual_model="DeepSeek")
    assert decision_manual.execution_mode == "auto"
