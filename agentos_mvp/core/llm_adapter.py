from __future__ import annotations

import json
from typing import Any, Dict


class LLMAdapterError(Exception):
    pass


class LLMAdapter:
    """
    当前阶段的最小 LLM 适配层（mock 版）

    目标：
    - 只服务当前 decision.py 的接口需求
    - 提供统一 generate(task_type, prompt) 方法
    - 不接真实 LLM
    - 不引入旧系统配置树
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def generate(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """
        统一返回结构：
        {
            "provider": str,
            "model": str,
            "content": str,
            "parsed": dict,
            "token_usage": int,
            "cost": float,
        }
        """
        if not self.enabled:
            raise LLMAdapterError("LLM is disabled")

        if task_type == "director":
            parsed = self._mock_director_output(prompt)
        elif task_type == "editor":
            parsed = self._mock_editor_output(prompt)
        else:
            raise LLMAdapterError(f"Unsupported task_type: {task_type}")

        return {
            "provider": "mock",
            "model": "mock-model",
            "content": json.dumps(parsed, ensure_ascii=False),
            "parsed": parsed,
            "token_usage": 0,
            "cost": 0.0,
        }

    def _mock_director_output(self, prompt: str) -> Dict[str, Any]:
        return {
            "video_angle": "突出产品最值得展示的核心使用价值",
            "hooks": [
                "这个细节一出场就能抓住注意力",
                "如果你也在意这个使用场景，这条一定要看",
                "别急着划走，这个点很多人都会忽略",
            ],
            "selling_points": [
                "卖点1：解决真实使用痛点",
                "卖点2：适合短视频展示",
            ],
            "script_outline": [
                "开场用主钩子快速抓注意力",
                "展示产品核心细节与差异点",
                "给出使用场景和行动召唤",
            ],
            "storyboard": [
                "镜头1：产品快速出场并强调第一眼记忆点",
                "镜头2：近景展示核心细节",
                "镜头3：展示典型使用场景并收尾",
            ],
        }

    def _mock_editor_output(self, prompt: str) -> Dict[str, Any]:
        return {
            "asset_plan": [
                {"type": "hook_shot", "source": "ai_or_real"},
                {"type": "detail_shot", "source": "ai_or_real"},
                {"type": "usage_shot", "source": "ai_or_real"},
            ],
            "edit_plan": [
                "前3秒快速进入主钩子画面",
                "中段用细节镜头强化卖点",
                "结尾用简洁CTA收束",
            ],
            "execution_plan": [
                "准备开场钩子镜头素材",
                "准备产品细节展示素材",
                "准备使用场景展示素材",
            ],
        }
