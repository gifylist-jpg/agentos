from services.decision_control_service import DecisionControlService
from agentos.schemas.analysis import AssetAnalysisResult
from agentos.schemas.enums import Stage, SignalStatus, Strength, Confidence, NoiseLevel, Suggestion


def main():
    service = DecisionControlService()

    fake_result = AssetAnalysisResult(
        asset_id="a",
        variant_id="v",
        stage=Stage.LATE,
        signal_status=SignalStatus.INSUFFICIENT,
        distribution_status=Strength.WEAK,
        creative_status=Strength.WEAK,
        commercial_status=Strength.WEAK,
        causal_confidence=Confidence.LOW,
        environment_noise=NoiseLevel.HIGH,
        data_trust="low",
        data_status="missing",
        freshness_level="stale",
        suggestion=Suggestion.WAIT_MORE_DATA,
        reason="force freeze",
        needs_human_review=True,
        review_reason="test",
        should_freeze_task=True,
        freeze_reason="force freeze",
        memory_candidate=False,
        memory_admission_ready=False,
    )

    bundle = service.process(
        task_id="test_frozen",
        asset_result=fake_result,
    )

    print("\n=== TEST FROZEN ===")
    print(bundle["control_outcome"])

    assert bundle["control_outcome"]["status"] == "FROZEN"
    print("✅ PASS: FROZEN as expected")


if __name__ == "__main__":
    main()
