from control.decision_record import DecisionRecord
from control.review_gate import ReviewGate
from control.freeze_gate import FreezeGate


class DecisionControlService:
    """
    Service Layer adapter:
    - 接收 Analysis 的 DecisionResult
    - 生成 DecisionRecord
    - 调用 ReviewGate / FreezeGate
    - 输出统一控制结果
    """

    def __init__(self):
        self.review_gate = ReviewGate()
        self.freeze_gate = FreezeGate()

    def process_analysis_result(self, task_id, variant_id, analysis_result):
        decision = DecisionRecord(
            task_id=task_id,
            variant_id=variant_id,
            action=analysis_result.summary.action,
            decision_type=analysis_result.summary.decision_type,
            confidence=analysis_result.confidence,
            review_required=analysis_result.summary.review_required,
            freeze_candidate=analysis_result.summary.freeze_candidate,
            memory_admission_candidate=analysis_result.summary.memory_admission_candidate,
            diagnostics=analysis_result.diagnostics.__dict__,
            metadata={
                "recommended_next_step": analysis_result.summary.recommended_next_step,
                "baseline_scope": analysis_result.summary.baseline_scope,
                "publish_scope": analysis_result.summary.publish_scope,
                "source": analysis_result.source,
            },
        )

        review_result = self.review_gate.evaluate(decision)
        freeze_result = self.freeze_gate.evaluate(decision)

        return {
            "decision_record": decision,
            "review_result": review_result,
            "freeze_result": freeze_result,
            "control_outcome": self._derive_control_outcome(
                decision, review_result, freeze_result
            ),
        }

    def _derive_control_outcome(self, decision, review_result, freeze_result):
        if freeze_result["frozen"]:
            return {
                "status": "FROZEN",
                "next_step": "stop automation and inspect task",
                "reason": freeze_result["reason"],
            }

        if review_result["blocked"]:
            return {
                "status": "REVIEW_REQUIRED",
                "next_step": "route to human review",
                "reason": review_result["reason"],
            }

        return {
            "status": "PASS",
            "next_step": decision.metadata.get("recommended_next_step", "no-op"),
            "reason": None,
        }
