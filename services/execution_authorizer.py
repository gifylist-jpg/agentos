from typing import Any


class AuthorizationError(Exception):
    """Raised when execution is not authorized."""
    pass


class ExecutionAuthorizer:
    """
    First version of Execution Authorizer.

    Responsibilities:
    - check task state
    - check review status
    - check guard status
    - check runtime budget

    Explicitly NOT included:
    - database access
    - complex policy engine
    - dynamic rule system
    """

    ALLOWED_EXECUTION_STATES = {"approved", "executing"}

    def authorize(
        self,
        *,
        task_state: str,
        review_passed: bool,
        guard_blocked: bool,
        runtime: Any,
    ) -> bool:
        """
        Main authorization entry.

        Args:
            task_state: current task state
            review_passed: whether required review is passed
            guard_blocked: whether guard is blocking execution
            runtime: TaskRuntime instance

        Returns:
            True if authorized

        Raises:
            AuthorizationError if any check fails
        """

        self._check_state(task_state)
        self._check_review(review_passed)
        self._check_guard(guard_blocked)
        self._check_budget(runtime)

        return True

    # ----------------------------
    # Checks
    # ----------------------------

    def _check_state(self, task_state: str) -> None:
        if task_state not in self.ALLOWED_EXECUTION_STATES:
            raise AuthorizationError(f"INVALID_STATE: {task_state}")

    def _check_review(self, review_passed: bool) -> None:
        if not review_passed:
            raise AuthorizationError("REVIEW_NOT_PASSED")

    def _check_guard(self, guard_blocked: bool) -> None:
        if guard_blocked:
            raise AuthorizationError("GUARD_BLOCKED")

    def _check_budget(self, runtime: Any) -> None:
        if hasattr(runtime, "is_token_budget_exceeded"):
            if runtime.is_token_budget_exceeded():
                raise AuthorizationError("TOKEN_BUDGET_EXCEEDED")
