class TaskRequest:
    def __init__(self, task_type, task_data, risk_level="medium"):
        self.task_type = task_type  # 任务类型
        self.task_data = task_data  # 任务数据
        self.risk_level = risk_level  # 风险级别（默认：medium）
