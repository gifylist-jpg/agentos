class TaskQueue:
    def __init__(self):
        self.pending_tasks = []
        self.running_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []

    def add_tasks(self, tasks):
        for task in tasks:
            self.pending_tasks.append(task)

    def get_ready_tasks(self):
        completed_ids = {t.id for t in self.completed_tasks}
        ready = []
        remaining = []

        for task in self.pending_tasks:
            if all(dep in completed_ids for dep in task.depends_on):
                ready.append(task)
            else:
                remaining.append(task)

        self.pending_tasks = remaining
        ready.sort(key=lambda x: x.priority)
        return ready

    def mark_running(self, task):
        task.status = "running"
        self.running_tasks.append(task)

    def mark_completed(self, task, result="", model=None, token_usage=0):
        task.status = "completed"
        task.result = result
        task.model = model
        task.token_usage = token_usage
        self.running_tasks = [t for t in self.running_tasks if t.id != task.id]
        self.completed_tasks.append(task)

    def mark_failed(self, task, result=""):
        task.status = "failed"
        task.result = result
        self.running_tasks = [t for t in self.running_tasks if t.id != task.id]
        self.failed_tasks.append(task)
    def load_from_dict(self, data):
        from models.task import Task

        self.pending_tasks = [Task.from_dict(t) for t in data.get("pending", [])]
        self.running_tasks = [Task.from_dict(t) for t in data.get("running", [])]
        self.completed_tasks = [Task.from_dict(t) for t in data.get("completed", [])]
        self.failed_tasks = [Task.from_dict(t) for t in data.get("failed", [])]
