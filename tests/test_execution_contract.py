import unittest

from runtime.execution_contract import ExecutionContract, ContractViolationError
from runtime.task_runtime import TaskRuntime


class TestExecutionContract(unittest.TestCase):

    def test_allowed_action_pass(self):
        contract = ExecutionContract({
            "allowed_actions": ["run", "stop"]
        })

        contract.validate_action("run")  # 不报错

    def test_action_not_allowed(self):
        contract = ExecutionContract({
            "allowed_actions": ["run"]
        })

        with self.assertRaises(ContractViolationError) as ctx:
            contract.validate_action("delete")

        self.assertIn("ACTION_NOT_ALLOWED", str(ctx.exception))

    def test_forbidden_action(self):
        contract = ExecutionContract({
            "forbidden_actions": ["delete"]
        })

        with self.assertRaises(ContractViolationError) as ctx:
            contract.validate_action("delete")

        self.assertIn("ACTION_FORBIDDEN", str(ctx.exception))

    def test_step_limit_pass(self):
        runtime = TaskRuntime("task_1", max_steps=0)
        runtime.on_task_start()
        runtime.on_step_start()  # step_count = 1

        contract = ExecutionContract({
            "max_steps": 5
        })

        contract.validate_runtime(runtime)  # 不报错

    def test_step_limit_exceeded(self):
        runtime = TaskRuntime("task_1", max_steps=0)
        runtime.on_task_start()
        runtime.on_step_start()  # 1
        runtime.on_step_end()
        runtime.on_step_start()  # 2
        runtime.on_step_end()
        runtime.on_step_start()  # 3

        contract = ExecutionContract({
            "max_steps": 2
        })

        with self.assertRaises(ContractViolationError) as ctx:
            contract.validate_runtime(runtime)

        self.assertEqual(str(ctx.exception), "STEP_LIMIT_EXCEEDED")


if __name__ == "__main__":
    unittest.main()
