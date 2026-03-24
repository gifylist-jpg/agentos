from __future__ import annotations

from typing import Any, Dict


class ActionExecutor:
    """
    Minimal action interpreter.

    This version does NOT execute anything.
    It only converts action strings into structured execution guidance.
    """

    VALID_ACTIONS = {"retry", "rollback", "human_intervention"}

    def interpret(
        self,
        *,
        task_id: str,
        action: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if action not in self.VALID_ACTIONS:
            raise ValueError(f"Invalid action: {action}")

        context = context or {}

        if action == "retry":
            return {
                "task_id": task_id,
                "action": "retry",
                "execute": False,
                "message": "Retry is recommended, but requires explicit caller handling.",
                "context": context,
            }

        if action == "rollback":
            return {
                "task_id": task_id,
                "action": "rollback",
                "execute": False,
                "message": "Rollback is recommended, but requires explicit caller handling.",
                "context": context,
            }

        return {
            "task_id": task_id,
            "action": "human_intervention",
            "execute": False,
            "message": "Human intervention is required before any further action.",
            "context": context,
        }
