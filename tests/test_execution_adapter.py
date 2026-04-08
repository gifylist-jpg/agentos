import unittest
from agentos.execution.execution_adapter import ExecutionAdapter

class TestExecutionAdapter(unittest.TestCase):

    def test_execution_adapter(self):
        adapter = ExecutionAdapter()

        result = adapter.execute({
            "payload": {
                "action": "openclaw_execute_video_workflow",
                "steps": ["step1", "step2"]
            }
        })

        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("execution_result", result)
        self.assertEqual(result["execution_result"]["status"], "success")

if __name__ == "__main__":
    unittest.main()
