# agentos/schemas/feedback_validator.py

from agentos.schemas.analysis import PerformanceAnalysisOutput, AssetAnalysisResult
from agentos.schemas.control import ControlOutcome


def validate_feedback_result(feedback_result: dict):
    """
    最终输出校验：
    系统唯一对外结构必须合法
    """

    # =========================
    # 必须字段存在
    # =========================
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

    # =========================
    # 类型校验
    # =========================
    assert isinstance(feedback_result["analysis_result"], PerformanceAnalysisOutput)
    assert isinstance(feedback_result["primary_asset_result"], AssetAnalysisResult)

    # =========================
    # control_outcome 校验
    # =========================
    outcome = feedback_result["control_outcome"]

    assert isinstance(outcome, dict), "[FEEDBACK ERROR] control_outcome must be dict"

    assert "status" in outcome
    assert outcome["status"] in {"ALLOWED", "BLOCKED", "FROZEN"}

    # =========================
    # 单一真相源（关键）
    # =========================
    assert feedback_result["decision_record"] is not None, \
        "[FEEDBACK ERROR] decision_record cannot be None"
