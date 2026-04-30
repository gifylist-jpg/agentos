from typing import List
from .settings import SUPPORTED_PROVIDERS  # 从 settings.py 获取可用的模型
import random

class ModelRouter:
    def __init__(self, task_type: str, enabled_providers: List[str]):
        self.task_type = task_type
        self.enabled_providers = enabled_providers

    def select_model(self) -> str:
        """
        Selects the appropriate model based on the task type and enabled providers.
        Implements fallback logic.
        """
        # 获取所有启用的模型提供者
        available_providers = [provider for provider in SUPPORTED_PROVIDERS if provider in self.enabled_providers]

        if not available_providers:
            raise ValueError("No enabled providers for task type")

        # 任务类型可以决定使用的模型，可以在这里加入更细化的控制逻辑
        # 例如，我们可以为某些特定任务类型优先选择特定的模型
        if self.task_type == "research":
            preferred_providers = ["deepseek", "claude"]
        elif self.task_type == "content":
            preferred_providers = ["claude", "deepseek"]
        else:
            preferred_providers = available_providers

        # 根据任务类型选择一个模型，优先选择已启用的提供者
        for provider in preferred_providers:
            if provider in available_providers:
                return provider

        # 如果没有直接选到，随机返回一个模型
        return random.choice(available_providers)
