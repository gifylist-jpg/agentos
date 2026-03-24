from openai import OpenAI
import anthropic
from config import Settings
from monitor.token_tracker import tracker


class LLMClient:
    def __init__(self, provider: str):
        self.provider = provider
        self.client = None

        if provider == "deepseek":
            if not Settings.ENABLE_DEEPSEEK:
                raise ValueError("deepseek is disabled in config")
            if not Settings.DEEPSEEK_API_KEY:
                raise ValueError("deepseek api key is empty")

            self.client = OpenAI(
                api_key=Settings.DEEPSEEK_API_KEY,
                base_url=Settings.DEEPSEEK_BASE_URL,
            )

        elif provider == "gpt":
            if not Settings.ENABLE_GPT:
                raise ValueError("gpt is disabled in config")
            if not Settings.OPENAI_API_KEY:
                raise ValueError("openai api key is empty")

            self.client = OpenAI(
                api_key=Settings.OPENAI_API_KEY,
                base_url=Settings.OPENAI_BASE_URL,
            )

        elif provider == "claude":
            if not Settings.ENABLE_CLAUDE:
                raise ValueError("claude is disabled in config")
            if not Settings.ANTHROPIC_API_KEY:
                raise ValueError("anthropic api key is empty")

            self.client = anthropic.Anthropic(
                api_key=Settings.ANTHROPIC_API_KEY
            )

        elif provider == "doubao":
            if not Settings.ENABLE_DOUBAO:
                raise ValueError("doubao is disabled in config")
            if not Settings.DOUBAO_API_KEY:
                raise ValueError("doubao api key is empty")
            if not Settings.DOUBAO_BASE_URL:
                raise ValueError("doubao base url is empty")

            self.client = OpenAI(
                api_key=Settings.DOUBAO_API_KEY,
                base_url=Settings.DOUBAO_BASE_URL,
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _record_openai_usage(self, resp, model: str, task_id: str | None = None):
        usage = getattr(resp, "usage", None)
        if not usage:
            return

        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", None)

        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens

        tracker.record(
            provider=self.provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            task_id=task_id,
            cost=None,
        )

    def _record_claude_usage(self, resp, model: str, task_id: str | None = None):
        usage = getattr(resp, "usage", None)
        if not usage:
            return

        input_tokens = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0

        tracker.record(
            provider=self.provider,
            model=model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            task_id=task_id,
            cost=None,
        )

    def chat_with_metadata(self, model: str, messages: list, task_id: str | None = None):
        try:
            print(f"[LLMClient] Calling provider={self.provider} model={model}")

            if self.provider in ["deepseek", "gpt", "doubao"]:
                resp = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                self._record_openai_usage(resp, model=model, task_id=task_id)

                content = resp.choices[0].message.content
                return {
                    "content": content,
                    "provider": self.provider,
                    "model_name": model,
                }

            elif self.provider == "claude":
                system = ""
                user_messages = []

                for m in messages:
                    if m["role"] == "system":
                        system = m["content"]
                    else:
                        user_messages.append(m)

                resp = self.client.messages.create(
                    model=model,
                    max_tokens=2000,
                    system=system,
                    messages=user_messages,
                )
                self._record_claude_usage(resp, model=model, task_id=task_id)

                content = resp.content[0].text
                return {
                    "content": content,
                    "provider": self.provider,
                    "model_name": model,
                }

            raise ValueError(f"Unsupported provider in chat_with_metadata(): {self.provider}")

        except Exception as e:
            error_type = type(e).__name__
            raise RuntimeError(
                f"LLM call failed | provider={self.provider} | model={model} | "
                f"error_type={error_type} | error={repr(e)}"
            )

    def chat(self, model: str, messages: list, task_id: str | None = None):
        result = self.chat_with_metadata(model=model, messages=messages, task_id=task_id)
        return result["content"]
