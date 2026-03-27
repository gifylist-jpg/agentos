from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import time
import uuid


# =========================================================
# 固定枚举（避免 suggestion / status 漂移）
# =========================================================

class Suggestion:
    WAIT_MORE_DATA = "WAIT_MORE_DATA"
    KEEP_OBSERVING = "KEEP_OBSERVING"
    KEEP = "KEEP"
    RETEST_SAME_ANGLE_NEW_HOOK = "RETEST_SAME_ANGLE_NEW_HOOK"
    RETEST_SAME_HOOK_NEW_CTA = "RETEST_SAME_HOOK_NEW_CTA"
    DISTRIBUTION_PROBLEM = "DISTRIBUTION_PROBLEM"
    DROP_CURRENT_VARIANT = "DROP_CURRENT_VARIANT"
    AMPLIFY_CANDIDATE = "AMPLIFY_CANDIDATE"
    ARCHIVE_NO_SIGNAL = "ARCHIVE_NO_SIGNAL"


class SignalStatus:
    INSUFFICIENT = "insufficient"
    PARTIAL = "partial"
    MATURE = "mature"


class Stage:
    EARLY = "early"
    MID = "mid"
    LATE = "late"


class ComparisonQuality:
    CLEAN = "clean"
    NOISY = "noisy"
    INVALID = "invalid"


class EnvironmentNoise:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CausalConfidence:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# =========================================================
# 输入结构
# =========================================================

@dataclass
class AssetPerformanceSnapshot:
    asset_id: str
    variant_id: str
    metrics: Dict[str, Any]
    timestamp: float

    # 数据可信度层
    data_trust: str = "medium"          # high | medium | low
    data_status: str = "complete"       # complete | partial | missing | delayed
    freshness_level: str = "fresh"      # fresh | warm | stale

    # 环境层
    publish_mode: str = "organic"       # organic | ads
    account_id: str = "unknown"
    environment_context: Dict[str, Any] = field(default_factory=dict)

    # 比较层
    comparison_quality: str = ComparisonQuality.CLEAN

    # 标签层（后期对接 CreativeTagSet）
    creative_tags: Dict[str, Any] = field(default_factory=dict)

    # 发布追踪层（后期对接 PublishRecord）
    publish_id: Optional[str] = None


@dataclass
class PerformanceAnalysisInput:
    product_id: str
    strategy_id: str
    snapshots: List[AssetPerformanceSnapshot]

    # baseline 必须按 publish_mode 分层，避免 organic / ads 混污染
    # 结构示例：
    # {
    #   "organic": {
    #       "product": {"ctr": 0.02, "watch_rate": 0.22, "avg_watch_time": 5.2, "views": 800, "cvr": 0.01},
    #       "account": {"ctr": 0.018, "watch_rate": 0.20},
    #       "style": {"ctr": 0.021, "watch_rate": 0.24}
    #   },
    #   "ads": {
    #       "product": {"ctr": 0.03, "watch_rate": 0.18}
    #   }
    # }
    baseline: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)

    # 目标层
    objective_context: Dict[str, Any] = field(default_factory=lambda: {
        "primary_metric": "watch_rate",
        "secondary_metric": "ctr",
        "optimization_goal": "test_creative_quality",
        "forbidden_optimization": [
            "misleading_hook_only",
            "high_ctr_low_quality",
            "high_views_low_retention",
        ]
    })


# =========================================================
# 中间聚合结构
# =========================================================

@dataclass
class VariantAggregate:
    asset_id: str
    variant_id: str
    publish_mode: str
    account_ids: List[str]

    snapshot_count: int
    first_timestamp: float
    last_timestamp: float
    time_window_hours: float

    latest_metrics: Dict[str, Any]
    peak_metrics: Dict[str, Any]

    data_trust: str
    data_status: str
    freshness_level: str
    comparison_quality: str
    environment_contexts: List[Dict[str, Any]]
    creative_tags: Dict[str, Any]


# =========================================================
# 输出结构
# =========================================================

@dataclass
class AssetAnalysisResult:
    asset_id: str
    variant_id: str

    stage: str
    signal_status: str

    distribution_status: str
    creative_status: str
    commercial_status: str

    causal_confidence: str
    comparison_quality: str
    environment_noise: str

    data_trust: str
    data_status: str
    freshness_level: str

    suggestion: str
    reason: str

    memory_candidate: bool
    memory_admission_ready: bool

    needs_human_review: bool
    review_reason: Optional[str] = None

    should_freeze_task: bool = False
    freeze_reason: Optional[str] = None


@dataclass
class PerformanceAnalysisOutput:
    analysis_id: str
    strategy_id: str
    product_id: str
    asset_results: List[AssetAnalysisResult]
    recommended_next_action: str
    summary: str


# =========================================================
# 主 Agent
# =========================================================

class PerformanceAnalysisAgent:
    """
    v3.2 = 审查对齐版
    核心特点：
    1. 先聚合 variant，再判断
    2. organic / ads baseline 强隔离
    3. 先判断能不能判，再判断好不好
    4. 输出固定 suggestion enum
    5. 支持 memory admission / human review / freeze
    """

    def analyze(self, input_data: PerformanceAnalysisInput) -> PerformanceAnalysisOutput:
        aggregates = self._build_variant_aggregates(input_data.snapshots)
        results: List[AssetAnalysisResult] = []

        for agg in aggregates:
            stage = self._judge_stage(agg)
            signal_status = self._judge_signal_status(agg, stage)
            environment_noise = self._judge_environment_noise(agg)
            causal_confidence = self._judge_causal_confidence(agg, signal_status, environment_noise)

            if not self._can_decide(agg, signal_status):
                result = AssetAnalysisResult(
                    asset_id=agg.asset_id,
                    variant_id=agg.variant_id,
                    stage=stage,
                    signal_status=signal_status,
                    distribution_status="unknown",
                    creative_status="unknown",
                    commercial_status="unknown",
                    causal_confidence=causal_confidence,
                    comparison_quality=agg.comparison_quality,
                    environment_noise=environment_noise,
                    data_trust=agg.data_trust,
                    data_status=agg.data_status,
                    freshness_level=agg.freshness_level,
                    suggestion=Suggestion.WAIT_MORE_DATA,
                    reason="数据未成熟 / 不完整 / 不新鲜，禁止进入强判断",
                    memory_candidate=False,
                    memory_admission_ready=False,
                    needs_human_review=False,
                    review_reason=None,
                    should_freeze_task=False,
                    freeze_reason=None,
                )
                results.append(result)
                continue

            baseline_bundle = self._get_baseline_bundle(
                publish_mode=agg.publish_mode,
                baseline=input_data.baseline,
            )

            distribution_status = self._judge_distribution(agg, baseline_bundle)
            creative_status = self._judge_creative(agg, baseline_bundle)
            commercial_status = self._judge_commercial(agg, baseline_bundle)

            suggestion, reason = self._decide_action(
                aggregate=agg,
                stage=stage,
                signal_status=signal_status,
                distribution_status=distribution_status,
                creative_status=creative_status,
                commercial_status=commercial_status,
                causal_confidence=causal_confidence,
                environment_noise=environment_noise,
                objective_context=input_data.objective_context,
                baseline_bundle=baseline_bundle,
            )

            memory_candidate, memory_admission_ready = self._judge_memory_admission(
                agg=agg,
                signal_status=signal_status,
                causal_confidence=causal_confidence,
                environment_noise=environment_noise,
            )

            needs_human_review, review_reason = self._judge_human_review(
                agg=agg,
                suggestion=suggestion,
                causal_confidence=causal_confidence,
                environment_noise=environment_noise,
            )

            should_freeze_task, freeze_reason = self._judge_freeze(
                agg=agg,
                suggestion=suggestion,
                signal_status=signal_status,
                causal_confidence=causal_confidence,
                environment_noise=environment_noise,
            )

            result = AssetAnalysisResult(
                asset_id=agg.asset_id,
                variant_id=agg.variant_id,
                stage=stage,
                signal_status=signal_status,
                distribution_status=distribution_status,
                creative_status=creative_status,
                commercial_status=commercial_status,
                causal_confidence=causal_confidence,
                comparison_quality=agg.comparison_quality,
                environment_noise=environment_noise,
                data_trust=agg.data_trust,
                data_status=agg.data_status,
                freshness_level=agg.freshness_level,
                suggestion=suggestion,
                reason=reason,
                memory_candidate=memory_candidate,
                memory_admission_ready=memory_admission_ready,
                needs_human_review=needs_human_review,
                review_reason=review_reason,
                should_freeze_task=should_freeze_task,
                freeze_reason=freeze_reason,
            )
            results.append(result)

        global_action = self._global_decision(results)

        return PerformanceAnalysisOutput(
            analysis_id=str(uuid.uuid4()),
            strategy_id=input_data.strategy_id,
            product_id=input_data.product_id,
            asset_results=results,
            recommended_next_action=global_action,
            summary="analysis_v32_completed"
        )

    # =========================================================
    # 聚合层
    # =========================================================

    def _build_variant_aggregates(self, snapshots: List[AssetPerformanceSnapshot]) -> List[VariantAggregate]:
        """
        按 (asset_id, variant_id, publish_mode) 聚合。
        这一步就是前面审查里要求的 variant aggregation。
        """
        grouped: Dict[Tuple[str, str, str], List[AssetPerformanceSnapshot]] = defaultdict(list)

        for s in snapshots:
            key = (s.asset_id, s.variant_id, s.publish_mode)
            grouped[key].append(s)

        aggregates: List[VariantAggregate] = []

        for (_, _, _), group in grouped.items():
            group_sorted = sorted(group, key=lambda x: x.timestamp)
            first_ts = group_sorted[0].timestamp
            last_ts = group_sorted[-1].timestamp
            time_window_hours = max((last_ts - first_ts) / 3600.0, 0.0)

            latest_metrics = group_sorted[-1].metrics
            peak_snapshot = max(group_sorted, key=lambda x: x.metrics.get("views", 0))
            peak_metrics = peak_snapshot.metrics

            agg = VariantAggregate(
                asset_id=group_sorted[0].asset_id,
                variant_id=group_sorted[0].variant_id,
                publish_mode=group_sorted[0].publish_mode,
                account_ids=list(sorted(set(x.account_id for x in group_sorted))),
                snapshot_count=len(group_sorted),
                first_timestamp=first_ts,
                last_timestamp=last_ts,
                time_window_hours=time_window_hours,
                latest_metrics=latest_metrics,
                peak_metrics=peak_metrics,
                data_trust=self._merge_data_trust([x.data_trust for x in group_sorted]),
                data_status=self._merge_data_status([x.data_status for x in group_sorted]),
                freshness_level=self._merge_freshness([x.freshness_level for x in group_sorted]),
                comparison_quality=self._merge_comparison_quality([x.comparison_quality for x in group_sorted]),
                environment_contexts=[x.environment_context for x in group_sorted],
                creative_tags=group_sorted[-1].creative_tags or {},
            )
            aggregates.append(agg)

        return aggregates

    def _merge_data_trust(self, values: List[str]) -> str:
        if "low" in values:
            return "low"
        if "medium" in values:
            return "medium"
        return "high"

    def _merge_data_status(self, values: List[str]) -> str:
        if "missing" in values:
            return "missing"
        if "delayed" in values:
            return "delayed"
        if "partial" in values:
            return "partial"
        return "complete"

    def _merge_freshness(self, values: List[str]) -> str:
        if "stale" in values:
            return "stale"
        if "warm" in values:
            return "warm"
        return "fresh"

    def _merge_comparison_quality(self, values: List[str]) -> str:
        if ComparisonQuality.INVALID in values:
            return ComparisonQuality.INVALID
        if ComparisonQuality.NOISY in values:
            return ComparisonQuality.NOISY
        return ComparisonQuality.CLEAN

    # =========================================================
    # baseline 层（强制 organic / ads 隔离）
    # =========================================================

    def _get_baseline_bundle(self, publish_mode: str, baseline: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        return baseline.get(publish_mode, {})

    # =========================================================
    # 时间阶段判断
    # =========================================================

    def _judge_stage(self, agg: VariantAggregate) -> str:
        delta = time.time() - agg.last_timestamp

        if delta < 2 * 3600:
            return Stage.EARLY
        elif delta < 24 * 3600:
            return Stage.MID
        else:
            return Stage.LATE

    # =========================================================
    # 信号成熟度判断
    # =========================================================

    def _judge_signal_status(self, agg: VariantAggregate, stage: str) -> str:
        views = agg.latest_metrics.get("views", 0)

        if agg.data_status in {"missing", "delayed"}:
            return SignalStatus.INSUFFICIENT

        if agg.data_trust == "low":
            return SignalStatus.INSUFFICIENT

        if stage == Stage.EARLY:
            if views < 100 or agg.snapshot_count < 1:
                return SignalStatus.INSUFFICIENT
            return SignalStatus.PARTIAL

        if stage == Stage.MID:
            if views < 200 or agg.snapshot_count < 1:
                return SignalStatus.PARTIAL
            return SignalStatus.MATURE

        # late
        if views < 150:
            return SignalStatus.PARTIAL
        return SignalStatus.MATURE

    # =========================================================
    # 环境噪声判断
    # =========================================================

    def _judge_environment_noise(self, agg: VariantAggregate) -> str:
        if agg.comparison_quality == ComparisonQuality.INVALID:
            return EnvironmentNoise.HIGH

        # 同一聚合里多个账号，本身就是高噪声
        if len(agg.account_ids) > 1:
            return EnvironmentNoise.HIGH

        if agg.comparison_quality == ComparisonQuality.NOISY:
            return EnvironmentNoise.MEDIUM

        if agg.publish_mode == "ads":
            return EnvironmentNoise.MEDIUM

        return EnvironmentNoise.LOW

    # =========================================================
    # 因果可信度
    # =========================================================

    def _judge_causal_confidence(
        self,
        agg: VariantAggregate,
        signal_status: str,
        environment_noise: str,
    ) -> str:
        if signal_status == SignalStatus.INSUFFICIENT:
            return CausalConfidence.LOW

        if environment_noise == EnvironmentNoise.HIGH:
            return CausalConfidence.LOW

        if environment_noise == EnvironmentNoise.MEDIUM:
            return CausalConfidence.MEDIUM

        # low noise 才可能给 high
        if agg.snapshot_count >= 2 and agg.time_window_hours >= 24:
            return CausalConfidence.HIGH

        return CausalConfidence.MEDIUM

    # =========================================================
    # 是否允许进入决策
    # =========================================================

    def _can_decide(self, agg: VariantAggregate, signal_status: str) -> bool:
        if signal_status == SignalStatus.INSUFFICIENT:
            return False
        if agg.data_status in {"missing", "delayed"}:
            return False
        if agg.freshness_level == "stale":
            return False
        return True

    # =========================================================
    # 分发表现判断
    # =========================================================

    def _judge_distribution(self, agg: VariantAggregate, baseline_bundle: Dict[str, Dict[str, float]]) -> str:
        views = agg.latest_metrics.get("views", 0)
        watch_rate = agg.latest_metrics.get("watch_rate", 0.0)

        product_base = baseline_bundle.get("product", {})
        base_watch = product_base.get("watch_rate", 0.20)
        base_views = product_base.get("views", 300)

        if views >= base_views * 2 and watch_rate >= base_watch * 1.2:
            return "strong"
        if views >= base_views * 0.8:
            return "normal"
        return "weak"

    # =========================================================
    # 内容表现判断
    # =========================================================

    def _judge_creative(self, agg: VariantAggregate, baseline_bundle: Dict[str, Dict[str, float]]) -> str:
        watch_rate = agg.latest_metrics.get("watch_rate", 0.0)
        avg_watch_time = agg.latest_metrics.get("avg_watch_time", 0.0)
        shares = agg.latest_metrics.get("shares", 0)
        comments = agg.latest_metrics.get("comments", 0)

        style_base = baseline_bundle.get("style", {})
        base_watch = style_base.get("watch_rate", 0.22)
        base_avg_watch = style_base.get("avg_watch_time", 5.0)

        if watch_rate >= base_watch * 1.2 and avg_watch_time >= base_avg_watch and (shares + comments) >= 5:
            return "strong"
        if watch_rate >= base_watch * 0.9:
            return "normal"
        return "weak"

    # =========================================================
    # 商业表现判断
    # =========================================================

    def _judge_commercial(self, agg: VariantAggregate, baseline_bundle: Dict[str, Dict[str, float]]) -> str:
        ctr = agg.latest_metrics.get("ctr", 0.0)
        orders = agg.latest_metrics.get("orders", 0)
        cvr = agg.latest_metrics.get("cvr", 0.0)

        product_base = baseline_bundle.get("product", {})
        base_ctr = product_base.get("ctr", 0.02)
        base_cvr = product_base.get("cvr", 0.01)

        if orders >= 2 or (ctr >= base_ctr * 1.3 and cvr >= base_cvr):
            return "strong"
        if ctr >= base_ctr * 0.9:
            return "normal"
        return "weak"

    # =========================================================
    # 决策逻辑
    # =========================================================

    def _decide_action(
        self,
        aggregate: VariantAggregate,
        stage: str,
        signal_status: str,
        distribution_status: str,
        creative_status: str,
        commercial_status: str,
        causal_confidence: str,
        environment_noise: str,
        objective_context: Dict[str, Any],
        baseline_bundle: Dict[str, Dict[str, float]],
    ) -> Tuple[str, str]:
        # 先处理不能强判的情况
        if signal_status != SignalStatus.MATURE:
            return Suggestion.WAIT_MORE_DATA, "信号未成熟，继续观察"

        if causal_confidence == CausalConfidence.LOW:
            return Suggestion.KEEP_OBSERVING, "因果可信度低，先不下强结论"

        if environment_noise == EnvironmentNoise.HIGH:
            return Suggestion.KEEP_OBSERVING, "环境噪声高，结论不稳定"

        # early 阶段禁止 hard drop
        if stage == Stage.EARLY:
            if creative_status == "weak" and distribution_status == "weak":
                return Suggestion.KEEP_OBSERVING, "早期信号弱，但阶段过早，禁止误杀"
            return Suggestion.WAIT_MORE_DATA, "早期阶段只允许观察"

        # mid / late 才进入更强判断
        if distribution_status == "weak" and creative_status == "strong":
            return Suggestion.DISTRIBUTION_PROBLEM, "内容表现好，问题更像分发或账号环境"

        if distribution_status == "strong" and creative_status == "strong" and commercial_status == "weak":
            return Suggestion.RETEST_SAME_ANGLE_NEW_HOOK, "内容和分发都可以，但商业层偏弱，优先改 CTA / 商业表达"

        if creative_status == "weak" and commercial_status == "weak":
            return Suggestion.DROP_CURRENT_VARIANT, "内容层和商业层都弱，当前变体不值得继续"

        if distribution_status == "strong" and creative_status == "strong" and commercial_status == "strong":
            return Suggestion.AMPLIFY_CANDIDATE, "三层都强，属于放大候选"

        if creative_status == "strong" and commercial_status == "normal":
            return Suggestion.KEEP, "内容稳定，可继续观察并保留"

        return Suggestion.RETEST_SAME_HOOK_NEW_CTA, "有一定信号，但结论不够强，优先小改重测"

    # =========================================================
    # 记忆准入判断
    # =========================================================

    def _judge_memory_admission(
        self,
        agg: VariantAggregate,
        signal_status: str,
        causal_confidence: str,
        environment_noise: str,
    ) -> Tuple[bool, bool]:
        memory_candidate = signal_status == SignalStatus.MATURE

        memory_admission_ready = (
            signal_status == SignalStatus.MATURE
            and causal_confidence in {CausalConfidence.MEDIUM, CausalConfidence.HIGH}
            and environment_noise == EnvironmentNoise.LOW
            and agg.snapshot_count >= 2
            and agg.time_window_hours >= 24
            and agg.data_trust in {"high", "medium"}
            and agg.data_status == "complete"
            and agg.publish_mode == "organic"  # 默认先只让 organic 更容易进入长期经验
        )

        return memory_candidate, memory_admission_ready

    # =========================================================
    # 是否需要人工复核
    # =========================================================

    def _judge_human_review(
        self,
        agg: VariantAggregate,
        suggestion: str,
        causal_confidence: str,
        environment_noise: str,
    ) -> Tuple[bool, Optional[str]]:
        if suggestion == Suggestion.AMPLIFY_CANDIDATE:
            return True, "涉及可能放大，建议人工复核"
        if causal_confidence == CausalConfidence.LOW:
            return True, "因果可信度低，建议人工确认"
        if environment_noise == EnvironmentNoise.HIGH:
            return True, "环境噪声高，建议人工确认"
        if agg.publish_mode == "ads":
            return True, "广告流量样本建议人工确认后再动作"
        return False, None

    # =========================================================
    # freeze 判断
    # =========================================================

    def _judge_freeze(
        self,
        agg: VariantAggregate,
        suggestion: str,
        signal_status: str,
        causal_confidence: str,
        environment_noise: str,
    ) -> Tuple[bool, Optional[str]]:
        if agg.data_status == "missing" and agg.snapshot_count >= 2:
            return True, "连续缺失数据，建议冻结任务人工检查"

        if signal_status == SignalStatus.INSUFFICIENT and agg.snapshot_count >= 3:
            return True, "多次仍无有效信号，建议冻结任务"

        if causal_confidence == CausalConfidence.LOW and environment_noise == EnvironmentNoise.HIGH:
            return True, "高噪声 + 低因果可信度，建议冻结等待人工判断"

        return False, None

    # =========================================================
    # 全局决策
    # =========================================================

    def _global_decision(self, results: List[AssetAnalysisResult]) -> str:
        amplify = [r for r in results if r.suggestion == Suggestion.AMPLIFY_CANDIDATE]
        keep = [r for r in results if r.suggestion == Suggestion.KEEP]
        retest = [
            r for r in results
            if r.suggestion in {
                Suggestion.RETEST_SAME_ANGLE_NEW_HOOK,
                Suggestion.RETEST_SAME_HOOK_NEW_CTA,
            }
        ]
        wait = [
            r for r in results
            if r.suggestion in {
                Suggestion.WAIT_MORE_DATA,
                Suggestion.KEEP_OBSERVING,
            }
        ]
        freeze = [r for r in results if r.should_freeze_task]

        if freeze:
            return "FREEZE_AND_REVIEW"
        if amplify:
            return "SELECT_BEST_AMPLIFY_CANDIDATE"
        if retest:
            return "RUN_SMALL_RETEST_BATCH"
        if keep:
            return "KEEP_CURRENT_BATCH_ALIVE"
        if wait:
            return "WAIT_MORE_DATA_BEFORE_DECISION"
        return "ARCHIVE_NO_SIGNAL"
