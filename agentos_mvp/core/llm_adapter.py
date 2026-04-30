import requests
from typing import Dict, Any
from .settings import MODEL_CONFIG

class LLMAdapterError(Exception):
    """LLM Adapter 错误的自定义异常"""
    pass

class LLMAdapter:
    def __init__(self, model_name: str = "deepseek", enabled: bool = True) -> None:
        self.enabled = enabled
        self.model_name = model_name

        # 获取模型的相关配置
        if self.model_name not in MODEL_CONFIG:
            raise LLMAdapterError(f"Model {self.model_name} is not supported.")

        self.api_url = MODEL_CONFIG[self.model_name]["api_url"]
        self.api_key = MODEL_CONFIG[self.model_name]["headers"]["Authorization"].replace("Bearer ", "")

        # 如果是 DeepSeek 模型，添加 /v1/messages 路径
        if self.model_name == "deepseek":
            self.api_url = self.api_url.rstrip("/") + "/v1/messages"

    def generate(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """根据任务类型调用对应模型的 API 生成数据"""
        if not self.enabled:
            raise LLMAdapterError("LLM is disabled")

        model_call_method = getattr(self, f"_call_{self.model_name}_api", None)

        # 如果没有特定模型方法，使用通用方法
        if not model_call_method:
            model_call_method = self._call_generic_api

        return model_call_method(task_type, prompt)

    def _call_deepseek_api(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """DeepSeek API调用"""
        url = self.api_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "task_type": task_type,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        return self._make_request(url, headers, payload)

    def _call_gpt_api(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """GPT API调用"""
        url = self.api_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-5.4",
            "task_type": task_type,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        return self._make_request(url, headers, payload)

    def _call_claude_api(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """Claude API调用"""
        url = self.api_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-sonnet-4-5-20250929",
            "task_type": task_type,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        return self._make_request(url, headers, payload)

    def _call_generic_api(self, task_type: str, prompt: str) -> Dict[str, Any]:
        """通用 API 调用方法"""
        url = self.api_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": f"{self.model_name}-chat",
            "task_type": task_type,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        return self._make_request(url, headers, payload)

    def _make_request(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求并返回响应"""
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxies, verify=False)
            response.raise_for_status()
            return self._parse_api_response(response.json())
        except requests.exceptions.RequestException as e:
            raise LLMAdapterError(f"Error calling {self.model_name} API: {e}")

    def _parse_api_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """解析 API 的返回结果，确保返回的数据格式符合预期"""
        # 直接从响应中获取 'content' 字段
        content = api_response.get("content", [])

        if not content:
            raise LLMAdapterError(f"Failed to parse API response: {api_response}")

        return content
