import time
from typing import Dict, List
from agentos.models.task import Task


class TaskQueue:
    def __init__(self) -> None:
        self.tasks: Dict[str, Task] = {}

    def add_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def list_all(self) -> List[Task]:
        return list(self.tasks.values())

    def update_status(self, task_id: str, status: str) -> None:
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = time.time()
