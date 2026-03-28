from services.decision_control_service import DecisionControlService
from agentos.schemas.analysis import AssetAnalysisResult
from agentos.schemas.enums import Stage, SignalStatus, Strength, Confidence, NoiseLevel, Suggestion


def main():
    service = DecisionControlService()

    fake_result = AssetAnalysisResult(
        asset_id="a",
        variant_id="v",
        stage=Stage.MID,
        signal_status=SignalStatus.PARTIAL,
        distribution_status=Strength.NORMAL,
        creative_status=Strength.NORMAL,
        commercial_status=Strength.NORMAL,
        causal_confidence=Confidence.MEDIUM,
        environment_noise=NoiseLevel.HIGH,
        data_trust="medium",
        data_status="complete",
        freshness_level="fresh",
        suggestion=Suggestion.WAIT_MORE_DATA,
        reason="force review",
        needs_human_review=True,
        review_reason="force review",
        should_freeze_task=False,
        freeze_reason=None,
        memory_candidate=False,
        memory_admission_ready=False,
    )

    bundle = service.process(
        task_id="test_blocked",
        asset_result=fake_result,
    )

    print("\n=== TEST BLOCKED ===")
    print(bundle["control_outcome"])

    assert bundle["control_outcome"]["status"] == "BLOCKED"
    print("✅ PASS: BLOCKED as expected")


if __name__ == "__main__":
    main()
