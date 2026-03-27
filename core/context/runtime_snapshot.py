class RuntimeSnapshot:
    def __init__(self, task):
        self.task_id = getattr(task, "id", None)
        self.current_state = getattr(task, "state", None)
        self.previous_state = getattr(task, "prev_state", None)

        self.retry_count = getattr(task, "retry_count", 0)
        self.review_conflict_count = getattr(task, "review_conflict_count", 0)

        self.is_frozen = getattr(task, "is_frozen", False)
        self.last_action = getattr(task, "last_action", None)
