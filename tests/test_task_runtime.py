import unittest

from runtime.task_runtime import TaskRuntime


class TestTaskRuntime(unittest.TestCase):
    def test_init_with_defaults(self):
        runtime = TaskRuntime("task_001")

        self.assertEqual(runtime.task_id, "task_001")
        self.assertEqual(runtime.context_scope, {})
        self.assertEqual(runtime.memory_scope, {})
        self.assertEqual(runtime.token_budget, 0)
        self.assertEqual(runtime.token_used, 0)
        self.assertEqual(runtime.max_steps, 0)
        self.assertEqual(runtime.step_count, 0)
        self.assertEqual(runtime.allowed_tools, [])
        self.assertIsNone(runtime.state_snapshot)
        self.assertEqual(runtime.status, "init")

    def test_invalid_task_id_should_fail(self):
        with self.assertRaises(ValueError):
            TaskRuntime("")

    def test_negative_token_budget_should_fail(self):
        with self.assertRaises(ValueError):
            TaskRuntime("task_001", token_budget=-1)

    def test_negative_max_steps_should_fail(self):
        with self.assertRaises(ValueError):
            TaskRuntime("task_001", max_steps=-1)

    def test_task_start_changes_status(self):
        runtime = TaskRuntime("task_001")
        runtime.on_task_start()
        self.assertEqual(runtime.status, "running")

    def test_step_lifecycle(self):
        runtime = TaskRuntime("task_001", max_steps=2)
        runtime.on_task_start()

        runtime.on_step_start()
        self.assertEqual(runtime.step_count, 1)
        self.assertEqual(runtime.status, "step_running")

        runtime.on_step_end()
        self.assertEqual(runtime.status, "running")

        runtime.on_step_start()
        self.assertEqual(runtime.step_count, 2)
        self.assertEqual(runtime.status, "step_running")

    def test_step_limit_exceeded(self):
        runtime = TaskRuntime("task_001", max_steps=1)
        runtime.on_task_start()

        runtime.on_step_start()
        runtime.on_step_end()

        with self.assertRaises(RuntimeError) as ctx:
            runtime.on_step_start()

        self.assertEqual(str(ctx.exception), "STEP_LIMIT_EXCEEDED")

    def test_end_step_without_start_should_fail(self):
        runtime = TaskRuntime("task_001")
        runtime.on_task_start()

        with self.assertRaises(RuntimeError):
            runtime.on_step_end()

    def test_cannot_start_step_when_not_running(self):
        runtime = TaskRuntime("task_001")

        with self.assertRaises(RuntimeError):
            runtime.on_step_start()

    def test_task_end_changes_status(self):
        runtime = TaskRuntime("task_001")
        runtime.on_task_start()
        runtime.on_task_end()

        self.assertEqual(runtime.status, "completed")

    def test_task_fail_changes_status(self):
        runtime = TaskRuntime("task_001")
        runtime.on_task_start()
        runtime.on_task_fail()

        self.assertEqual(runtime.status, "failed")

    def test_cannot_end_failed_task(self):
        runtime = TaskRuntime("task_001")
        runtime.on_task_start()
        runtime.on_task_fail()

        with self.assertRaises(RuntimeError):
            runtime.on_task_end()

    def test_add_token_usage(self):
        runtime = TaskRuntime("task_001", token_budget=100)
        runtime.add_token_usage(30)
        runtime.add_token_usage(40)

        self.assertEqual(runtime.token_used, 70)
        self.assertFalse(runtime.is_token_budget_exceeded())

    def test_token_budget_exceeded(self):
        runtime = TaskRuntime("task_001", token_budget=50)
        runtime.add_token_usage(51)

        self.assertTrue(runtime.is_token_budget_exceeded())

    def test_negative_token_usage_should_fail(self):
        runtime = TaskRuntime("task_001")

        with self.assertRaises(ValueError):
            runtime.add_token_usage(-1)

    def test_steps_remaining(self):
        runtime = TaskRuntime("task_001", max_steps=3)
        runtime.on_task_start()
        self.assertEqual(runtime.steps_remaining(), 3)

        runtime.on_step_start()
        self.assertEqual(runtime.steps_remaining(), 2)

    def test_unlimited_steps_returns_none(self):
        runtime = TaskRuntime("task_001", max_steps=0)
        self.assertIsNone(runtime.steps_remaining())

    def test_context_scope_is_isolated(self):
        base_context = {"goal": "A"}
        runtime = TaskRuntime("task_001", context_scope=base_context)

        runtime.set_context_value("goal", "B")

        self.assertEqual(base_context["goal"], "A")
        self.assertEqual(runtime.get_context_value("goal"), "B")

    def test_memory_scope_is_isolated(self):
        base_memory = {"summary": "old"}
        runtime = TaskRuntime("task_001", memory_scope=base_memory)

        runtime.set_memory_value("summary", "new")

        self.assertEqual(base_memory["summary"], "old")
        self.assertEqual(runtime.get_memory_value("summary"), "new")

    def test_to_dict_returns_copy(self):
        runtime = TaskRuntime(
            "task_001",
            context_scope={"a": 1},
            memory_scope={"b": 2},
            allowed_tools=["tool_a"],
            state_snapshot={"state": "planning"},
        )

        data = runtime.to_dict()
        data["context_scope"]["a"] = 999
        data["memory_scope"]["b"] = 999
        data["allowed_tools"].append("tool_b")
        data["state_snapshot"]["state"] = "broken"

        self.assertEqual(runtime.get_context_value("a"), 1)
        self.assertEqual(runtime.get_memory_value("b"), 2)
        self.assertEqual(runtime.allowed_tools, ["tool_a"])
        self.assertEqual(runtime.state_snapshot, {"state": "planning"})


if __name__ == "__main__":
    unittest.main()
