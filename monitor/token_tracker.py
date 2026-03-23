import json
import time
from pathlib import Path


class TokenTracker:
    def __init__(
        self,
        log_file: str = "logs/token_usage.jsonl",
        hour_limit: int = 200000,
        daily_limit: int = 1000000,
    ):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.hour_limit = hour_limit
        self.daily_limit = daily_limit

        self._hour_bucket = self._current_hour_bucket()
        self._day_bucket = self._current_day_bucket()

        self.hourly_tokens = 0
        self.daily_tokens = 0

    def _current_hour_bucket(self) -> str:
        return time.strftime("%Y-%m-%d-%H")

    def _current_day_bucket(self) -> str:
        return time.strftime("%Y-%m-%d")

    def _reset_if_needed(self) -> None:
        now_hour = self._current_hour_bucket()
        now_day = self._current_day_bucket()

        if now_hour != self._hour_bucket:
            self._hour_bucket = now_hour
            self.hourly_tokens = 0

        if now_day != self._day_bucket:
            self._day_bucket = now_day
            self.daily_tokens = 0

    def _read_entries(self) -> list[dict]:
        if not self.log_file.exists():
            return []

        entries = []
        with self.log_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    def record(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        task_id: str | None = None,
        cost: float | None = None,
    ) -> dict:
        self._reset_if_needed()

        prompt_tokens = int(prompt_tokens or 0)
        completion_tokens = int(completion_tokens or 0)
        total_tokens = prompt_tokens + completion_tokens

        projected_hourly = self.hourly_tokens + total_tokens
        projected_daily = self.daily_tokens + total_tokens

        if projected_hourly > self.hour_limit:
            raise RuntimeError(
                f"Hourly token limit exceeded: {projected_hourly} > {self.hour_limit}"
            )

        if projected_daily > self.daily_limit:
            raise RuntimeError(
                f"Daily token limit exceeded: {projected_daily} > {self.daily_limit}"
            )

        self.hourly_tokens = projected_hourly
        self.daily_tokens = projected_daily

        entry = {
            "timestamp": int(time.time()),
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "hourly_tokens": self.hourly_tokens,
            "daily_tokens": self.daily_tokens,
            "hour_limit": self.hour_limit,
            "daily_limit": self.daily_limit,
            "task_id": task_id,
            "cost": cost,
        }

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def get_all_by_task_id(self, task_id: str | None) -> list[dict]:
        if not task_id:
            return []

        entries = self._read_entries()
        return [entry for entry in entries if entry.get("task_id") == task_id]

    def get_latest_by_task_id(self, task_id: str | None) -> dict | None:
        matches = self.get_all_by_task_id(task_id)
        if not matches:
            return None
        return matches[-1]

    def get_total_tokens_by_task_id(self, task_id: str | None) -> int:
        latest = self.get_latest_by_task_id(task_id)
        if not latest:
            return 0
        return int(latest.get("total_tokens", 0) or 0)

    def get_status(self) -> dict:
        self._reset_if_needed()
        return {
            "hour_bucket": self._hour_bucket,
            "day_bucket": self._day_bucket,
            "hourly_tokens": self.hourly_tokens,
            "daily_tokens": self.daily_tokens,
            "hour_limit": self.hour_limit,
            "daily_limit": self.daily_limit,
        }

tracker = TokenTracker()
