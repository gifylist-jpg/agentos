class ConsistencyGuard:

    VALID_STATES = [
        "planning", "script_ready", "waiting_review",
        "approved", "executing", "completed",
        "rejected", "failed"
    ]

    def check(self, context, snapshot):

        # 1. 禁止自动执行
        if context.auto_execution:
            raise Exception("AUTO_EXECUTION_FORBIDDEN")

        # 2. 状态合法性检查
        if snapshot.current_state not in self.VALID_STATES:
            raise Exception(f"INVALID_STATE: {snapshot.current_state}")

        # 3. 冻结任务禁止继续
        if snapshot.is_frozen:
            raise Exception("TASK_FROZEN")

        return True
