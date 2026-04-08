import unittest
from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.approved_decision import ApprovedDecision


class TestTaskServiceV2Execution(unittest.TestCase):
    def test_process_task_and_execute(self):
        mock_decision_service = MagicMock()
        mock_decision_service.generate_decision.return_value = {
            'execution_mode': 'auto',
            'selected_candidate_id': '123',
            'action': 'execute_task',
            'steps': ['step1', 'step2']
        }

        mock_execution_adapter = MagicMock()
        mock_execution_adapter.execute.return_value = {
            'status': 'SUCCESS',
            'execution_result': {
                'status': 'success',
                'result': {
                    'executed_action': 'execute_simple_task',
                    'steps_completed': ['step1', 'step2']
                }
            }
        }

        task_service = TaskServiceV2(model_selector=None)
        task_service.decision_service = mock_decision_service
        task_service.execution_adapter = mock_execution_adapter

        result = task_service.process_task_and_execute({
            'task_type': 'simple_task',
            'steps': ['step1', 'step2']
        })

        self.assertIn("decision", result)
        self.assertIn("execution", result)

        self.assertIsInstance(result["decision"], ApprovedDecision)
        self.assertEqual(result["decision"].execution_mode, 'auto')
        self.assertEqual(result["decision"].selected_candidate_id, '123')

        self.assertEqual(result["execution"]["status"], 'SUCCESS')
        self.assertIn("execution_result", result["execution"])


if __name__ == "__main__":
    unittest.main()
