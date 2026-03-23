import json
import os


class CheckpointManager:
    def __init__(self, run_dir):
        self.path = os.path.join(run_dir, "checkpoint.json")

    def save(self, task_queue):
        data = {
            "pending": [t.to_dict() for t in getattr(task_queue, "pending_tasks", [])],
            "running": [t.to_dict() for t in getattr(task_queue, "running_tasks", [])],
            "completed": [t.to_dict() for t in getattr(task_queue, "completed_tasks", [])],
            "failed": [t.to_dict() for t in getattr(task_queue, "failed_tasks", [])],
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self):
        if not os.path.exists(self.path):
            return None

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)
