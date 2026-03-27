class SystemContext:
    def __init__(self):
        self.version = "v3.2-core-stable"
        self.mode = "controlled"
        self.auto_execution = False

        # 当前真实执行链（不可被修改）
        self.execution_flow = [
            "TaskService.check_and_handle_stuck_tasks",
            "StuckTaskHandler",
            "StuckTaskDetector",
            "AlertService",
            "RecoveryPolicy",
            "ActionExecutor"
        ]

        # 当前系统能力
        self.capabilities = [
            "detect",
            "alert",
            "policy",
            "interpret"
        ]

        # 未实现能力（必须明确）
        self.not_implemented = [
            "execution",
            "scheduler",
            "openclaw",
            "auto_loop"
        ]

        # 严格规则（不可违反）
        self.strict_rules = [
            "no_auto_execution",
            "no_state_mutation_outside_taskservice",
            "no_model_direct_execution",
            "no_bypass_guard"
        ]
