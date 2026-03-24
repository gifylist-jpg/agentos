from typing import Dict, Any, List


class ContractViolationError(Exception):
    """Raised when execution violates contract rules."""
    pass


class ExecutionContract:
    """
    Execution behavior constraint.

    Responsibilities:
    - validate allowed actions
    - enforce step limits
    - enforce basic execution rules

    Explicitly NOT included:
    - authorization logic
    - guard logic
    - review logic
    - database interaction
    """

    def __init__(self, contract: Dict[str, Any]):
        self.allowed_actions: List[str] = contract.get("allowed_actions", [])
        self.forbidden_actions: List[str] = contract.get("forbidden_actions", [])
        self.max_steps: int = contract.get("max_steps", 0)
        self.max_runtime: int = contract.get("max_runtime", 0)
        self.no_self_planning: bool = contract.get("no_self_planning", True)
        self.no_state_modification: bool = contract.get("no_state_modification", True)

    # ----------------------------
    # Validation
    # ----------------------------

    def validate_action(self, action: str) -> None:
        """
        Check whether an action is allowed.
        """

        if self.allowed_actions:
            if action not in self.allowed_actions:
                raise ContractViolationError(f"ACTION_NOT_ALLOWED: {action}")

        if action in self.forbidden_actions:
            raise ContractViolationError(f"ACTION_FORBIDDEN: {action}")

    def validate_step(self, runtime: Any) -> None:
        """
        Check step limit using runtime.
        """
        if self.max_steps > 0 and runtime.step_count > self.max_steps:
            raise ContractViolationError("STEP_LIMIT_EXCEEDED")

    def validate_runtime(self, runtime: Any) -> None:
        """
        Check overall runtime constraints.
        """
        # 当前版本只做 step 校验
        self.validate_step(runtime)
