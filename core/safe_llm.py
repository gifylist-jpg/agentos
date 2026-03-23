import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from llm.client import LLMClient


class TimeoutException(Exception):
    pass


class ProviderConcurrencyManager:
    _locks = {}
    _global_lock = threading.Lock()

    @classmethod
    def get_semaphore(cls, provider: str, limit: int):
        key = f"{provider}:{limit}"
        with cls._global_lock:
            if key not in cls._locks:
                cls._locks[key] = threading.BoundedSemaphore(limit)
            return cls._locks[key]


class SafeLLMCaller:
    def __init__(
        self,
        model_router,
        timeout=120,
        max_retries=3,
        provider_limits=None,
    ):
        self.model_router = model_router
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider_limits = provider_limits or {
            "deepseek": 2,
            "gpt": 2,
            "claude": 2,
            "doubao": 2,
        }

    def _classify_exception(self, e: Exception):
        text = repr(e).lower()

        if isinstance(e, FutureTimeoutError) or "timeout" in text:
            return "timeout"

        if "apiconnectionerror" in text or "connection error" in text:
            return "connection"

        if "rate limit" in text or "ratelimit" in text or "429" in text:
            return "rate_limit"

        if "api key" in text or "auth" in text or "unauthorized" in text or "invalid_request" in text:
            return "fatal"

        if isinstance(e, ValueError) or isinstance(e, TypeError):
            return "fatal"

        return "unknown"

    def _sleep_with_backoff(self, attempt: int, error_kind: str):
        base = 2 ** attempt

        if error_kind == "connection":
            wait_s = 3 * base + random.uniform(0.3, 1.2)
        elif error_kind == "rate_limit":
            wait_s = 5 * base + random.uniform(0.5, 1.5)
        elif error_kind == "timeout":
            wait_s = 2 * base + random.uniform(0.2, 0.8)
        else:
            wait_s = 2 * base + random.uniform(0.2, 1.0)

        time.sleep(wait_s)

    def _execute_with_route(self, route: dict, messages, task_id=None):
        if not isinstance(route, dict):
            raise TypeError(f"route must be dict, got: {type(route)}")

        provider = route.get("provider")
        model_name = route.get("model")

        if not provider:
            raise ValueError("Missing 'provider' in route")
        if not model_name:
            raise ValueError("Missing 'model' in route")

        provider_limit = self.provider_limits.get(provider, 2)
        semaphore = ProviderConcurrencyManager.get_semaphore(provider, provider_limit)

        acquired = semaphore.acquire(timeout=self.timeout)
        if not acquired:
            raise TimeoutException(
                f"Provider semaphore acquire timeout | provider={provider} | limit={provider_limit}"
            )

        try:
            llm_client = LLMClient(provider)
            return llm_client.chat_with_metadata(
                model=model_name,
                messages=messages,
                task_id=task_id,
            )
        finally:
            semaphore.release()

    def _call_single_route_with_retries(self, route: dict, messages, task_id=None):
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self._execute_with_route,
                        route,
                        messages,
                        task_id,
                    )
                    response = future.result(timeout=self.timeout)
                    return response

            except FutureTimeoutError:
                error_kind = "timeout"
                last_exception = TimeoutException("LLM call timeout")
                print(
                    f"[SafeLLM][Timeout] provider={route.get('provider')} "
                    f"model={route.get('model')} attempt={attempt}"
                )

            except Exception as e:
                error_kind = self._classify_exception(e)
                last_exception = e
                print(
                    f"[SafeLLM][Error] provider={route.get('provider')} "
                    f"model={route.get('model')} attempt={attempt} "
                    f"kind={error_kind} type={type(e).__name__} error={repr(e)}"
                )

                if error_kind == "fatal":
                    raise e

            if attempt < self.max_retries - 1:
                self._sleep_with_backoff(attempt, error_kind)

        raise last_exception

    def call_with_metadata(self, task_type, messages, task_id=None):
        primary_route = self.model_router.route(task_type)

        try:
            return self._call_single_route_with_retries(
                route=primary_route,
                messages=messages,
                task_id=task_id,
            )
        except Exception as primary_error:
            error_kind = self._classify_exception(primary_error)
            current_provider = primary_route.get("provider")

            # 只有非致命错误才尝试 fallback
            if error_kind == "fatal":
                raise primary_error

            fallback_provider = self.model_router.fallback(current_provider)
            if not fallback_provider:
                raise primary_error

            fallback_model = self.model_router.provider_default_models.get(fallback_provider)
            fallback_route = {
                "provider": fallback_provider,
                "model": fallback_model,
                "strict": False,
            }

            print(
                f"[SafeLLM][Fallback] from provider={current_provider} "
                f"to provider={fallback_provider} for task_type={task_type}"
            )

            return self._call_single_route_with_retries(
                route=fallback_route,
                messages=messages,
                task_id=task_id,
            )

    def call(self, task_type, messages, task_id=None):
        result = self.call_with_metadata(
            task_type=task_type,
            messages=messages,
            task_id=task_id,
        )
        return result["content"]
