from agentos.config.settings import FALLBACK_CHAINS


class ModelRouter:
    def get_provider_chain(self, task_type: str) -> list[str]:
        return FALLBACK_CHAINS.get(task_type, FALLBACK_CHAINS["default"])

    def get_primary_provider(self, task_type: str) -> str:
        chain = self.get_provider_chain(task_type)
        return chain[0] if chain else "deepseek"
