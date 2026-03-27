# agentos/schemas/invariant_checker.py

from agentos.schemas.enums import SignalStatus, Confidence, NoiseLevel, Suggestion


def check_analysis_invariants(asset_result):
    """
    核心约束：防止错误决策进入系统
    违反 = 系统错误（必须中断）
    """

    # =========================
    # INV-D4：信号不足禁止强决策
    # =========================
    if asset_result.signal_status == SignalStatus.INSUFFICIENT:
        assert asset_result.suggestion != Suggestion.SCALE, \
            "[INVARIANT ERROR] INSUFFICIENT signal cannot SCALE"

    # =========================
    # INV-D5：低因果禁止放大
    # =========================
    if asset_result.causal_confidence == Confidence.LOW:
        assert asset_result.suggestion != Suggestion.SCALE, \
            "[INVARIANT ERROR] LOW causality cannot SCALE"

    # =========================
    # INV-D6：高噪声必须降级
    # =========================
    if asset_result.environment_noise == NoiseLevel.HIGH:
        assert asset_result.needs_human_review, \
            "[INVARIANT ERROR] HIGH noise must trigger review"

    # =========================
    # INV-DL1：允许不决策
    # =========================
    assert asset_result.suggestion is not None, \
        "[INVARIANT ERROR] suggestion cannot be None"
