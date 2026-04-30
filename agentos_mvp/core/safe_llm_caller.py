import requests
from typing import Any
from .settings import MODEL_CONFIG  # 从settings.py动态加载模型配置

class SafeLLMCaller:
    def __init__(self, model_name: str) -> None:
        """
        初始化 LLM 调用器，基于模型名称从配置中加载 API URL 和 API Key。
        """
        if model_name not in MODEL_CONFIG:
            raise ValueError(f"Model {model_name} not supported.")
        
        self.model_name = model_name
        self.api_url = MODEL_CONFIG[model_name]["api_url"]
        self.api_key = MODEL_CONFIG[model_name]["headers"]["Authorization"].replace("Bearer ", "")  # 提取 API Key

    def call(self, prompt: str, model: str) -> Any:
        """
        调用大模型 API，返回模型的输出。
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "model": model}

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()  # 确保捕捉到 HTTP 错误
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling model API ({self.model_name}): {e}")
        except Exception as e:
            raise Exception(f"Unexpected error while calling model API: {e}")
