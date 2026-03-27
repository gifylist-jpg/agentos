from agents.performance_analysis_agent import (
    PerformanceAnalysisAgent,
    PerformanceAggregate,
    PublishContext,
    BaselineReference,
)
from services.decision_control_service import DecisionControlService


def run_case(case_name, aggregate, context, baseline):
    agent = PerformanceAnalysisAgent()
    control_service = DecisionControlService()

    analysis_result = agent.analyze(aggregate, context, baseline)

    result = control_service.process_analysis_result(
        task_id=f"task_{case_name.lower().replace(' ', '_')}",
        variant_id=aggregate.variant_id,
        analysis_result=analysis_result,
    )

    print(f"\n=== {case_name} ===")
    print("\n[ANALYSIS RESULT]")
    print(analysis_result)

    print("\n[DECISION RECORD]")
    print(result["decision_record"].to_dict())

    print("\n[REVIEW RESULT]")
    print(result["review_result"])

    print("\n[FREEZE RESULT]")
    print(result["freeze_result"])

    print("\n[CONTROL OUTCOME]")
    print(result["control_outcome"])


baseline = BaselineReference(
    organic_baseline={"ctr": 0.03},
    ads_baseline={"ctr": 0.05},
)

# Case A: ads dominated -> should require review
aggregate_a = PerformanceAggregate(
    variant_id="v_ads",
    metrics={
        "impressions": 3000,
        "clicks": 240,
        "ctr": 0.08,
        "cvr": 0.015,
        "watch_time": 6.5,
        "completion_rate": 0.38,
        "orders": 2,
    },
    stage="mid",
    age_hours=24,
)

context_a = PublishContext(
    publish_mode="ads",
    account_id="acc_ads",
    product_id="prod_ads",
    traffic_mix={
        "organic_ratio": 0.1,
        "ads_ratio": 0.9,
    },
)

# Case B: mature organic winner -> should pass
aggregate_b = PerformanceAggregate(
    variant_id="v_win",
    metrics={
        "impressions": 5000,
        "clicks": 220,
        "ctr": 0.044,
        "cvr": 0.025,
        "watch_time": 8.0,
        "completion_rate": 0.46,
        "orders": 8,
    },
    stage="late",
    age_hours=96,
)

context_b = PublishContext(
    publish_mode="organic",
    account_id="acc_win",
    product_id="prod_win",
    traffic_mix={
        "organic_ratio": 1.0,
        "ads_ratio": 0.0,
    },
)

run_case("CASE A - ADS REVIEW", aggregate_a, context_a, baseline)
run_case("CASE B - ORGANIC PASS", aggregate_b, context_b, baseline)
