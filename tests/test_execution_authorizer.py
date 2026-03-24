import unittest

from services.execution_authorizer import ExecutionAuthorizer, AuthorizationError
from runtime.task_runtime import TaskRuntime


class TestExecutionAuthorizer(unittest.TestCase):

    def setUp(self):
        self.authorizer = ExecutionAuthorizer()

    def test_authorize_success(self):
        runtime = TaskRuntime("task_1", token_budget=100)
        runtime.add_token_usage(50)

        result = self.authorizer.authorize(
            task_state="approved",
            review_passed=True,
            guard_blocked=False,
            runtime=runtime,
        )

        self.assertTrue(result)

    def test_invalid_state_should_fail(self):
        runtime = TaskRuntime("task_1")

        with self.assertRaises(AuthorizationError) as ctx:
            self.authorizer.authorize(
                task_state="planning",
                review_passed=True,
                guard_blocked=False,
                runtime=runtime,
            )

        self.assertIn("INVALID_STATE", str(ctx.exception))

    def test_review_not_passed_should_fail(self):
        runtime = TaskRuntime("task_1")

        with self.assertRaises(AuthorizationError) as ctx:
            self.authorizer.authorize(
                task_state="approved",
                review_passed=False,
                guard_blocked=False,
                runtime=runtime,
            )

        self.assertEqual(str(ctx.exception), "REVIEW_NOT_PASSED")

    def test_guard_blocked_should_fail(self):
        runtime = TaskRuntime("task_1")

        with self.assertRaises(AuthorizationError) as ctx:
            self.authorizer.authorize(
                task_state="approved",
                review_passed=True,
                guard_blocked=True,
                runtime=runtime,
            )

        self.assertEqual(str(ctx.exception), "GUARD_BLOCKED")

    def test_token_budget_exceeded_should_fail(self):
        runtime = TaskRuntime("task_1", token_budget=50)
        runtime.add_token_usage(100)

        with self.assertRaises(AuthorizationError) as ctx:
            self.authorizer.authorize(
                task_state="approved",
                review_passed=True,
                guard_blocked=False,
                runtime=runtime,
            )

        self.assertEqual(str(ctx.exception), "TOKEN_BUDGET_EXCEEDED")


if __name__ == "__main__":
    unittest.main()
