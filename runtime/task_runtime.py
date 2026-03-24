from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


class TaskRuntime:
    """
    Task-level isolated runtime context.

    First version scope:
    - task isolation
    - token counting
    - step counting
    - lifecycle hooks
    - minimal state fields

    Explicitly NOT included in v1:
    - authorization logic
    - guard logic
    - review checking
    - database access
    - distributed runtime
    """

    VALID_STATUSES = {
        "init",
        "running",
        "step_running",
        "completed",
        "failed",
    }

    def __init__(
        self,
        task_id: str,
        *,
        context_scope: Optional[Dict[str, Any]] = None,
        memory_scope: Optional[Dict[str, Any]] = None,
        token_budget: int = 0,
        max_steps: int = 0,
        allowed_tools: Optional[List[str]] = None,
        state_snapshot: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not task_id or not isinstance(task_id, str):
            raise ValueError("task_id must be a non-empty string")

        if token_budget < 0:
            raise ValueError("token_budget cannot be negative")

        if max_steps < 0:
            raise ValueError("max_steps cannot be negative")

        self.task_id = task_id

        # Isolation scopes
        self.context_scope: Dict[str, Any] = deepcopy(context_scope) if context_scope else {}
        self.memory_scope: Dict[str, Any] = deepcopy(memory_scope) if memory_scope else {}

        # Resource control
        self.token_budget: int = token_budget
        self.token_used: int = 0
        self.max_steps: int = max_steps
        self.step_count: int = 0

        # Execution constraints
        self.allowed_tools: List[str] = list(allowed_tools) if allowed_tools else []
        self.state_snapshot: Optional[Dict[str, Any]] = (
            deepcopy(state_snapshot) if state_snapshot else None
        )

        # Lifecycle
        self.status: str = "init"

    # ----------------------------
    # Lifecycle hooks
    # ----------------------------
    def on_task_start(self) -> None:
        self._set_status("running")

    def on_step_start(self) -> None:
        if self.status not in {"running", "step_running"}:
            raise RuntimeError("cannot start step when task is not running")

        if self.max_steps > 0 and self.step_count >= self.max_steps:
            raise RuntimeError("STEP_LIMIT_EXCEEDED")

        self.step_count += 1
        self._set_status("step_running")

    def on_step_end(self) -> None:
        if self.status != "step_running":
            raise RuntimeError("cannot end step when no step is running")

        self._set_status("running")

    def on_task_end(self) -> None:
        if self.status == "failed":
            raise RuntimeError("cannot end a failed task")

        self._set_status("completed")

    def on_task_fail(self) -> None:
        self._set_status("failed")

    # ----------------------------
    # Resource tracking
    # ----------------------------
    def add_token_usage(self, tokens: int) -> None:
        if tokens < 0:
            raise ValueError("tokens cannot be negative")

        self.token_used += tokens

    def is_token_budget_exceeded(self) -> bool:
        if self.token_budget <= 0:
            return False
        return self.token_used > self.token_budget

    def steps_remaining(self) -> Optional[int]:
        if self.max_steps <= 0:
            return None
        return self.max_steps - self.step_count

    # ----------------------------
    # Scope helpers
    # ----------------------------
    def set_context_value(self, key: str, value: Any) -> None:
        self.context_scope[key] = value

    def get_context_value(self, key: str, default: Any = None) -> Any:
        return self.context_scope.get(key, default)

    def set_memory_value(self, key: str, value: Any) -> None:
        self.memory_scope[key] = value

    def get_memory_value(self, key: str, default: Any = None) -> Any:
        return self.memory_scope.get(key, default)

    # ----------------------------
    # Serialization / snapshot
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "context_scope": deepcopy(self.context_scope),
            "memory_scope": deepcopy(self.memory_scope),
            "token_budget": self.token_budget,
            "token_used": self.token_used,
            "max_steps": self.max_steps,
            "step_count": self.step_count,
            "allowed_tools": list(self.allowed_tools),
            "state_snapshot": deepcopy(self.state_snapshot),
            "status": self.status,
        }

    # ----------------------------
    # Internal
    # ----------------------------
    def _set_status(self, new_status: str) -> None:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"invalid status: {new_status}")
        self.status = new_status
