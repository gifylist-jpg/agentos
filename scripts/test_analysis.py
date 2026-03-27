from agents.performance_analysis_agent import (
    PerformanceAnalysisAgent,
    PerformanceAggregate,
    PublishContext,
    BaselineReference
)


def run_case(case_name, aggregate, context, baseline):
    agent = PerformanceAnalysisAgent()
    result = agent.analyze(aggregate, context, baseline)

    print(f"\n=== {case_name} ===")
    print(result)


baseline = BaselineReference(
    organic_baseline={"ctr": 0.03},
    ads_baseline={"ctr": 0.05}
)

# Case 1: early + low data -> WAIT_MORE_DATA
aggregate_1 = PerformanceAggregate(
    variant_id="v1",
    metrics={
        "impressions": 50,
        "clicks": 2,
        "ctr": 0.04,
        "cvr": 0.01,
        "watch_time": 3.5,
        "completion_rate": 0.2,
        "orders": 0
    },
    stage="early",
    age_hours=2
)

context_1 = PublishContext(
    publish_mode="organic",
    account_id="acc1",
    product_id="prod1",
    traffic_mix={
        "organic_ratio": 1.0,
        "ads_ratio": 0.0
    }
)

# Case 2: ads strong ctr -> HUMAN_REVIEW
aggregate_2 = PerformanceAggregate(
    variant_id="v2",
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
    age_hours=30
)

context_2 = PublishContext(
    publish_mode="ads",
    account_id="acc2",
    product_id="prod2",
    traffic_mix={
        "organic_ratio": 0.1,
        "ads_ratio": 0.9
    }
)

# Case 3: low distribution but promising creative -> RETEST
aggregate_3 = PerformanceAggregate(
    variant_id="v3",
    metrics={
        "impressions": 1200,
        "clicks": 18,
        "ctr": 0.015,
        "cvr": 0.005,
        "watch_time": 7.0,
        "completion_rate": 0.42,
        "orders": 0
    },
    stage="mid",
    age_hours=36
)

context_3 = PublishContext(
    publish_mode="organic",
    account_id="acc3",
    product_id="prod3",
    traffic_mix={
        "organic_ratio": 1.0,
        "ads_ratio": 0.0
    }
)

# Case 4: delayed-growth-like mature organic winner -> SCALE_CANDIDATE
aggregate_4 = PerformanceAggregate(
    variant_id="v4",
    metrics={
        "impressions": 5000,
        "clicks": 220,
        "ctr": 0.044,
        "cvr": 0.025,
        "watch_time": 8.0,
        "completion_rate": 0.46,
        "orders": 8
    },
    stage="late",
    age_hours=96
)

context_4 = PublishContext(
    publish_mode="organic",
    account_id="acc4",
    product_id="prod4",
    traffic_mix={
        "organic_ratio": 1.0,
        "ads_ratio": 0.0
    }
)

# Case 5: high traffic but low commercial -> should not scale
aggregate_5 = PerformanceAggregate(
    variant_id="v5",
    metrics={
        "impressions": 8000,
        "clicks": 320,
        "ctr": 0.04,
        "cvr": 0.003,
        "watch_time": 6.8,
        "completion_rate": 0.37,
        "orders": 1
    },
    stage="late",
    age_hours=72
)

context_5 = PublishContext(
    publish_mode="organic",
    account_id="acc5",
    product_id="prod5",
    traffic_mix={
        "organic_ratio": 1.0,
        "ads_ratio": 0.0
    }
)

# Case 6: mixed traffic contamination -> confidence should stay MEDIUM
aggregate_6 = PerformanceAggregate(
    variant_id="v6",
    metrics={
        "impressions": 4000,
        "clicks": 180,
        "ctr": 0.045,
        "cvr": 0.02,
        "watch_time": 7.5,
        "completion_rate": 0.4,
        "orders": 4
    },
    stage="mid",
    age_hours=40
)

context_6 = PublishContext(
    publish_mode="organic",
    account_id="acc6",
    product_id="prod6",
    traffic_mix={
        "organic_ratio": 0.55,
        "ads_ratio": 0.45
    }
)

run_case("CASE 1 - EARLY LOW DATA", aggregate_1, context_1, baseline)
run_case("CASE 2 - ADS STRONG CTR", aggregate_2, context_2, baseline)
run_case("CASE 3 - LOW DISTRIBUTION BUT PROMISING CREATIVE", aggregate_3, context_3, baseline)
run_case("CASE 4 - MATURE ORGANIC WINNER", aggregate_4, context_4, baseline)
run_case("CASE 5 - HIGH TRAFFIC LOW COMMERCIAL", aggregate_5, context_5, baseline)
run_case("CASE 6 - MIXED TRAFFIC CONTAMINATION", aggregate_6, context_6, baseline)
