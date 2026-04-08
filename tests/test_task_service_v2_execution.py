import unittest
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.approved_decision import ApprovedDecision


class TestTaskServiceV2Execution(unittest.TestCase):

    def test_process_task_and_execute(self):
        service = TaskServiceV2(model_selector=None)

        result = service.process_task_and_execute({
            "task_type": "simple_task",
            "steps": ["step1", "step2"]
        })

        self.assertIn("decision", result)
        self.assertIn("execution", result)

        self.assertIsInstance(result["decision"], ApprovedDecision)
        self.assertEqual(result["decision"].execution_mode, "auto")

        self.assertEqual(result["execution"]["status"], "SUCCESS")
        self.assertIn("execution_result", result["execution"])
        self.assertEqual(
            result["execution"]["execution_result"]["result"]["executed_action"],
            "execute_simple_task"
        )
        self.assertEqual(
            result["execution"]["execution_result"]["result"]["steps_completed"],
            ["step1", "step2"]
        )


if __name__ == "__main__":
    unittest.main()
