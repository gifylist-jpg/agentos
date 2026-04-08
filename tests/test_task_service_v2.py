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

        task_service = TaskServiceV2(model_selector=None)
        task_service.decision_service = mock_decision_service

        task_data = {'task_type': 'simple_task'}
        decision = task_service.process_task(task_data)

        self.assertIsInstance(decision, ApprovedDecision)
        self.assertEqual(decision.execution_mode, 'auto')
        self.assertEqual(decision.selected_candidate_id, '123')

    def test_injected_model_selector_is_used(self):
        fake_model = MagicMock()
        fake_model.evaluate.return_value = {
            'execution_mode': 'manual',
            'selected_candidate_id': 'fake-1'
        }

        fake_selector = MagicMock()
        fake_selector.select_model.return_value = fake_model

        task_service = TaskServiceV2(model_selector=fake_selector)
        decision = task_service.process_task({'task_type': 'complex_task'})

        fake_selector.select_model.assert_called_once_with('complex_task')
        fake_model.evaluate.assert_called_once()

        self.assertIsInstance(decision, ApprovedDecision)
        self.assertEqual(decision.execution_mode, 'manual')
        self.assertEqual(decision.selected_candidate_id, 'fake-1')

    def test_simple_task_forces_auto_execution_mode(self):
        fake_model = MagicMock()
        fake_model.evaluate.return_value = {
            'execution_mode': 'manual',
            'selected_candidate_id': 'simple-1'
        }

        fake_selector = MagicMock()
        fake_selector.select_model.return_value = fake_model

        task_service = TaskServiceV2(model_selector=fake_selector)
        decision = task_service.process_task({'task_type': 'simple_task'})

        fake_selector.select_model.assert_called_once_with('simple_task')
        fake_model.evaluate.assert_called_once()

        self.assertIsInstance(decision, ApprovedDecision)
        self.assertEqual(decision.execution_mode, 'auto')
        self.assertEqual(decision.selected_candidate_id, 'simple-1')


if __name__ == "__main__":
    unittest.main()
