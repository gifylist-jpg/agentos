from agentos.schemas.analysis import PerformanceAnalysisOutput, AssetAnalysisResult
from agentos.schemas.control import ControlStatus


def validate_feedback_result(feedback_result: dict):
    """
    最终输出校验：
    系统唯一对外结构必须合法
    """

    required_keys = [
        "analysis_result",
        "primary_asset_result",
        "decision_record",
        "review_result",
        "freeze_result",
        "control_outcome",
    ]

    for key in required_keys:
        assert key in feedback_result, f"[FEEDBACK ERROR] missing field: {key}"

    assert isinstance(
        feedback_result["analysis_result"], PerformanceAnalysisOutput
    ), "[FEEDBACK ERROR] analysis_result must be PerformanceAnalysisOutput"

    assert isinstance(
        feedback_result["primary_asset_result"], AssetAnalysisResult
    ), "[FEEDBACK ERROR] primary_asset_result must be AssetAnalysisResult"

    outcome = feedback_result["control_outcome"]

    assert isinstance(outcome, dict), "[FEEDBACK ERROR] control_outcome must be dict"
    assert "status" in outcome, "[FEEDBACK ERROR] control_outcome missing status"

    assert outcome["status"] in {
        ControlStatus.ALLOWED,
        ControlStatus.BLOCKED,
        ControlStatus.FROZEN,
    }, f"[FEEDBACK ERROR] invalid control_outcome status: {outcome['status']}"

    assert feedback_result["decision_record"] is not None, (
        "[FEEDBACK ERROR] decision_record cannot be None"
    )
