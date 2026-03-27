from agents.performance_analysis_agent import (
    PerformanceAnalysisAgent,
    PerformanceAggregate,
    PublishContext,
    BaselineReference
)

from control.decision_record import DecisionRecord
from control.review_gate import ReviewGate
from control.freeze_gate import FreezeGate


def run_control_test():

    agent = PerformanceAnalysisAgent()
    review_gate = ReviewGate()
    freeze_gate = FreezeGate()

    baseline = BaselineReference(
        organic_baseline={"ctr": 0.03},
        ads_baseline={"ctr": 0.05}
    )

    aggregate = PerformanceAggregate(
        variant_id="v_test",
        metrics={
            "impressions": 3000,
            "clicks": 240,
            "ctr": 0.08,
            "cvr": 0.015,
            "watch_time": 6.5,
            "completion_rate": 0.38,
            "orders": 2
        },
        stage="mid",
        age_hours=24
    )

    context = PublishContext(
        publish_mode="ads",
        account_id="acc_test",
        product_id="prod_test",
        traffic_mix={
            "organic_ratio": 0.1,
            "ads_ratio": 0.9
        }
    )

    result = agent.analyze(aggregate, context, baseline)

    decision = DecisionRecord(
        task_id="task_1",
        variant_id=aggregate.variant_id,
        action=result.summary.action,
        decision_type=result.summary.decision_type,
        confidence=result.confidence,
        review_required=result.summary.review_required,
        freeze_candidate=result.summary.freeze_candidate,
        memory_admission_candidate=result.summary.memory_admission_candidate,
        diagnostics=result.diagnostics.__dict__,
        metadata={
            "recommended_next_step": result.summary.recommended_next_step
        }
    )

    review_result = review_gate.evaluate(decision)
    freeze_result = freeze_gate.evaluate(decision)

    print("\n=== DECISION RECORD ===")
    print(decision.to_dict())

    print("\n=== REVIEW GATE ===")
    print(review_result)

    print("\n=== FREEZE GATE ===")
    print(freeze_result)


if __name__ == "__main__":
    run_control_test()
