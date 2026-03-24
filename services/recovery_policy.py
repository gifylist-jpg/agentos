from __future__ import annotations


class RecoveryPolicy:
    def get_action(
        self,
        *,
        severity: str,
        error_type: str,
    ) -> str:
        _ = error_type

        if severity == "L1":
            return "retry"
        if severity == "L2":
            return "rollback"
        if severity == "L3":
            return "human_intervention"

        raise ValueError(f"Invalid severity: {severity}")
