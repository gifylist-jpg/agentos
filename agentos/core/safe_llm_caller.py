import requests

from agentos.config.settings import (
    ENABLE_DEEPSEEK,
    ENABLE_GPT,
    ENABLE_CLAUDE,
    ENABLE_DOUBAO,
    ENABLE_QWEN,
    ENABLE_KIMI,
    ENABLE_HUNYUAN,
    ENABLE_GEMINI,
    ENABLE_CUSTOM_CN_1,
    MODEL_NAME_MAP,
    LLM_MAX_RETRIES,
    DEBUG_FORCE_FAIL_PROVIDER,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    GPT_API_KEY,
    GPT_BASE_URL,
    CLAUDE_API_KEY,
    CLAUDE_BASE_URL,
    DOUBAO_API_KEY,
    DOUBAO_BASE_URL,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    KIMI_API_KEY,
    KIMI_BASE_URL,
    HUNYUAN_API_KEY,
    HUNYUAN_BASE_URL,
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    CUSTOM_CN_1_API_KEY,
    CUSTOM_CN_1_BASE_URL,
)


class SafeLLMCaller:
    def __init__(self) -> None:
        self.enabled_map = {
            "deepseek": ENABLE_DEEPSEEK,
            "gpt": ENABLE_GPT,
            "claude": ENABLE_CLAUDE,
            "doubao": ENABLE_DOUBAO,
            "qwen": ENABLE_QWEN,
            "kimi": ENABLE_KIMI,
            "hunyuan": ENABLE_HUNYUAN,
            "gemini": ENABLE_GEMINI,
            "custom_cn_1": ENABLE_CUSTOM_CN_1,
        }

    def is_enabled(self, provider: str) -> bool:
        return self.enabled_map.get(provider, False)

    def call_with_fallback(self, task_type: str, prompt: str, provider_chain: list[str]) -> dict:
        last_error = None

        for provider in provider_chain:
            if not self.is_enabled(provider):
                print(f"[SafeLLM][SKIP] provider={provider} reason=disabled")
                continue

            for attempt in range(1, LLM_MAX_RETRIES + 1):
                try:
                    print(f"[SafeLLM][TRY] provider={provider} attempt={attempt} task_type={task_type}")

                    if DEBUG_FORCE_FAIL_PROVIDER and provider == DEBUG_FORCE_FAIL_PROVIDER:
                        raise RuntimeError(f"Simulated failure for provider={provider}")

                    result = self._call_provider(provider, prompt)

                    print(
                        f"[SafeLLM][SUCCESS] provider={result['provider']} "
                        f"model={result['model']}"
                    )
                    return result

                except Exception as e:
                    last_error = e
                    print(f"[SafeLLM][FAIL] provider={provider} attempt={attempt} error={e}")

            print(f"[SafeLLM][FALLBACK] move_to_next_provider after={provider}")

        raise RuntimeError(f"All providers failed. last_error={last_error}")

    def _call_provider(self, provider: str, prompt: str) -> dict:
        model_name = MODEL_NAME_MAP.get(provider, "unknown-model")

        # =========================
        # DeepSeek（真实实现）
        # =========================
        if provider == "deepseek":
            if not DEEPSEEK_API_KEY:
                raise RuntimeError("Missing DEEPSEEK_API_KEY")

            url = f"{DEEPSEEK_BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI agent."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                raise RuntimeError(f"DeepSeek API error: {response.text}")

            result = response.json()

            return {
                "provider": provider,
                "model": model_name,
                "content": result["choices"][0]["message"]["content"],
                "token_usage": result.get("usage", {}).get("total_tokens", 0),
                "cost": 0,
            }

        # =========================
        # Claude（真实实现）
        # =========================
        elif provider == "claude":
            if not CLAUDE_API_KEY:
                raise RuntimeError("Missing CLAUDE_API_KEY")

            url = f"{CLAUDE_BASE_URL}/v1/messages"
            headers = {
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            data = {
                "model": model_name,
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                raise RuntimeError(f"Claude API error: {response.text}")

            result = response.json()

            text_output = ""
            if "content" in result and isinstance(result["content"], list):
                for block in result["content"]:
                    if block.get("type") == "text":
                        text_output += block.get("text", "")

            return {
                "provider": provider,
                "model": model_name,
                "content": text_output,
                "token_usage": (
                    result.get("usage", {}).get("input_tokens", 0)
                    + result.get("usage", {}).get("output_tokens", 0)
                ),
                "cost": 0,
            }

        # =========================
        # 其他 provider 先占位
        # =========================
        elif provider == "gpt":
            if not GPT_API_KEY:
                raise RuntimeError("Missing GPT_API_KEY")
            raise RuntimeError("Provider not implemented yet: gpt")

        elif provider == "doubao":
            if not DOUBAO_API_KEY:
                raise RuntimeError("Missing DOUBAO_API_KEY")
            raise RuntimeError("Provider not implemented yet: doubao")

        elif provider == "qwen":
            if not QWEN_API_KEY:
                raise RuntimeError("Missing QWEN_API_KEY")
            raise RuntimeError("Provider not implemented yet: qwen")

        elif provider == "kimi":
            if not KIMI_API_KEY:
                raise RuntimeError("Missing KIMI_API_KEY")
            raise RuntimeError("Provider not implemented yet: kimi")

        elif provider == "hunyuan":
            if not HUNYUAN_API_KEY:
                raise RuntimeError("Missing HUNYUAN_API_KEY")
            raise RuntimeError("Provider not implemented yet: hunyuan")

        elif provider == "gemini":
            if not GEMINI_API_KEY:
                raise RuntimeError("Missing GEMINI_API_KEY")
            raise RuntimeError("Provider not implemented yet: gemini")

        elif provider == "custom_cn_1":
            if not CUSTOM_CN_1_API_KEY:
                raise RuntimeError("Missing CUSTOM_CN_1_API_KEY")
            raise RuntimeError("Provider not implemented yet: custom_cn_1")

        else:
            raise RuntimeError(f"Unknown provider: {provider}")
