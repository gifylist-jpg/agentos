from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

def test_task_service_v2():
    task_data = {'task_type': 'classification', 'task_data': 'test_data'}
    
    # 模拟 MultiModelDecisionService 的 generate_decision 方法
    mock_decision_service = MagicMock(MultiModelDecisionService)
    mock_decision_service.generate_decision.return_value = {'execution_mode': 'auto', 'selected_candidate_id': '123'}
    
    task_service = TaskServiceV2()
    task_service.decision_service = mock_decision_service
    
    # 执行任务处理
    result = task_service.process_task(task_data)
    
    # 验证返回的决策对象
    assert isinstance(result, ApprovedDecision)
    assert result.execution_mode == 'auto'
    assert result.selected_candidate_id == '123'

test_task_service_v2()
