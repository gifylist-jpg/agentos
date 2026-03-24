class ShortTermMemory:
    def __init__(self):
        self.current_goal = None
        self.current_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.step_count = 0

    def start_session(self, goal, tasks):
        self.current_goal = goal
        self.current_tasks = tasks
        self.completed_tasks = []
        self.failed_tasks = []
        self.step_count = 0

    def record_completed_task(self, task):
        self.completed_tasks.append(task)

    def record_failed_task(self, task):
        self.failed_tasks.append(task)

    def increment_step(self):
        self.step_count += 1

    def get_summary(self):
        return {
            "goal": self.current_goal,
            "total_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "step_count": self.step_count
        }
