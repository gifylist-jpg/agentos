import unittest
from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.execution.execution_adapter import ExecutionAdapter

class TestTaskServiceV2Execution(unittest.TestCase):
    def test_process_task(self):
        mock_decision_service = MagicMock()
        mock_decision_service.generate_decision.return_value = {
            'execution_mode': 'auto',
            'selected_candidate_id': '123',
            'action': 'execute_task',
            'steps': ['step1', 'step2']
        }

        mock_execution_adapter = MagicMock()
        mock_execution_adapter.execute.return_value = {
            'status': 'success',
            'execution_result': {'executed_action': 'execute_task', 'steps_completed': ['step1', 'step2']}
        }

        task_service = TaskServiceV2(model_selector=None, execution_adapter=mock_execution_adapter)
        task_service.decision_service = mock_decision_service

        task_data = {'task_type': 'simple_task'}
        decision = task_service.process_task(task_data)

        self.assertIsInstance(decision, ApprovedDecision)
        self.assertEqual(decision.execution_mode, 'auto')
        self.assertEqual(decision.selected_candidate_id, '123')

if __name__ == "__main__":
    unittest.main()
