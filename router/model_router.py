from config import Settings


class ModelRouter:
    def __init__(self):
        # 主路由策略：先给出“推荐模型”
        # 后面你只需要改这里，就能切换系统默认调度策略
        self.default_routes = {
            "research": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "data": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "analysis": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "content": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "marketing": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "summary": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "video": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
            "planner": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "strict": False,
            },
        }

        self.default_fallback_route = {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "strict": False,
        }

        # provider 的兜底顺序
        self.provider_priority = ["deepseek", "gpt", "claude", "doubao"]

        # 各 provider 默认模型
        self.provider_default_models = {
            "deepseek": "deepseek-chat",
            "gpt": "gpt-4o-mini",
            "claude": "claude-sonnet-4-20250514",
            "doubao": "doubao-seed-1-6-thinking",
        }

    def _normalize_task_type(self, task_or_type):
        # 兼容 task 对象 or 直接字符串
        if isinstance(task_or_type, str):
            return task_or_type.lower()

        task_type = getattr(task_or_type, "type", "research")
        return str(task_type).lower()

    def route(self, task_or_type):
        task_type = self._normalize_task_type(task_or_type)

        route = self.default_routes.get(task_type, self.default_fallback_route)
        provider = route["provider"]
        strict = route.get("strict", False)

        if self._is_provider_enabled(provider):
            return route

        if strict:
            raise ValueError(
                f"Route provider '{provider}' is disabled for strict task type '{task_type}'"
            )

        return self._fallback_route(task_type, exclude_provider=provider)

    def _is_provider_enabled(self, provider: str) -> bool:
        if provider == "deepseek":
            return bool(Settings.ENABLE_DEEPSEEK)

        if provider == "gpt":
            return bool(Settings.ENABLE_GPT)

        if provider == "claude":
            return bool(Settings.ENABLE_CLAUDE)

        if provider == "doubao":
            return bool(Settings.ENABLE_DOUBAO)

        return False

    def _fallback_route(self, task_type: str, exclude_provider: str | None = None):
        for provider in self.provider_priority:
            if provider == exclude_provider:
                continue

            if self._is_provider_enabled(provider):
                return {
                    "provider": provider,
                    "model": self.provider_default_models[provider],
                    "strict": False,
                }

        raise ValueError(
            f"No enabled model provider available for task type: {task_type}"
        )

    def fallback(self, current_provider: str | None):
        for provider in self.provider_priority:
            if provider == current_provider:
                continue

            if self._is_provider_enabled(provider):
                return provider

        return None

    def set_route(self, task_type: str, provider: str, model: str, strict: bool = False):
        self.default_routes[str(task_type).lower()] = {
            "provider": provider,
            "model": model,
            "strict": strict,
        }

    def get_route(self, task_type: str):
        task_type = str(task_type).lower()
        return self.default_routes.get(task_type, self.default_fallback_route)

    def get_routes(self):
        return self.default_routes

    def get_enabled_providers(self):
        enabled = []

        for provider in self.provider_priority:
            if self._is_provider_enabled(provider):
                enabled.append(provider)

        return enabled
