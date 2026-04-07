import unittest
from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.approved_decision import ApprovedDecision

class TestTaskServiceV2(unittest.TestCase):

    def test_process_task(self):
        mock_decision_service = MagicMock()
        mock_decision_service.generate_decision.return_value = {
            'execution_mode': 'auto',
            'selected_candidate_id': '123'
        }
        
        task_service = TaskServiceV2()
        task_service.decision_service = mock_decision_service
        
        task_data = {'some_key': 'some_value'}
        decision = task_service.process_task(task_data)

        self.assertIsInstance(decision, ApprovedDecision)
        self.assertEqual(decision.execution_mode, 'auto')
        self.assertEqual(decision.selected_candidate_id, '123')

if __name__ == "__main__":
    unittest.main()
