class Supervisor:
    def __init__(
        self,
        max_tasks=10,
        max_steps=20,
        max_retries=2,
        max_task_tokens=3000,
    ):
        self.max_tasks = max_tasks
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.max_task_tokens = max_task_tokens
        self.seen_task_signatures = set()

    def reset(self):
        self.seen_task_signatures = set()

    def check_task_count(self, tasks):
        task_count = len(tasks or [])
        if task_count > self.max_tasks:
            raise Exception(f"Too many tasks: {task_count} > {self.max_tasks}")

    def check_step_limit(self, step_count):
        if int(step_count) > self.max_steps:
            raise Exception(f"Step limit exceeded: {step_count} > {self.max_steps}")

    def _get_task_text(self, task):
        raw_text = getattr(task, "task", None)
        if raw_text is None:
            raw_text = getattr(task, "name", None)
        if raw_text is None:
            raw_text = ""
        return str(raw_text).strip().lower()

    def _get_task_type(self, task):
        return str(getattr(task, "type", "unknown")).strip().lower()

    def _get_task_token_usage(self, task):
        token_usage = getattr(task, "token_usage", 0)

        if token_usage is None:
            return 0

        if isinstance(token_usage, dict):
            if "total_tokens" in token_usage:
                return int(token_usage.get("total_tokens", 0) or 0)
            if "tokens" in token_usage:
                return int(token_usage.get("tokens", 0) or 0)
            if "usage" in token_usage:
                return int(token_usage.get("usage", 0) or 0)
            return 0

        try:
            return int(token_usage)
        except Exception:
            return 0

    def check_token_limit(self, task):
        task_tokens = self._get_task_token_usage(task)
        if task_tokens > self.max_task_tokens:
            raise Exception(
                f"Task token exceeded: {task_tokens} > {self.max_task_tokens}"
            )

    def is_duplicate_task(self, task):
        signature = (
            self._get_task_type(task),
            self._get_task_text(task),
        )
        if signature in self.seen_task_signatures:
            return True

        self.seen_task_signatures.add(signature)
        return False

    def can_retry(self, task):
        retries = getattr(task, "retries", 0)
        try:
            retries = int(retries)
        except Exception:
            retries = 0
        return retries < self.max_retries

    def get_status(self):
        return {
            "max_tasks": self.max_tasks,
            "max_steps": self.max_steps,
            "max_retries": self.max_retries,
            "max_task_tokens": self.max_task_tokens,
            "seen_task_signatures_count": len(self.seen_task_signatures),
        }

