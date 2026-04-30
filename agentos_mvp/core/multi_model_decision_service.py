from typing import Any, Dict
from .model_router import ModelRouter  # 引入 ModelRouter 用于模型选择
from .llm_adapter import LLMAdapter  # 引入 LLMAdapter 用于与大模型交互

class MultiModelDecisionService:
    def __init__(self, task_type: str, enabled_providers: List[str], llm_adapter: LLMAdapter) -> None:
        self.task_type = task_type
        self.model_router = ModelRouter(task_type, enabled_providers)  # 初始化 ModelRouter
        self.llm_adapter = llm_adapter  # LLM适配器，用于生成模型决策结果

    def make_decision(self, prompt: str) -> Dict[str, Any]:
        """
        根据任务类型选择模型并调用相应的API生成决策。
        """
        try:
            # 选择合适的模型
            model_name = self.model_router.select_model()  # 调用 ModelRouter 的选择逻辑

            # 设置 LLMAdapter 使用选中的模型
            self.llm_adapter.model_name = model_name  # 更新 LLMAdapter 中的模型

            # 使用 LLMAdapter 生成模型输出
            response = self.llm_adapter.generate(self.task_type, prompt)

            # 返回模型生成的响应
            return response

        except ValueError as e:
            # 如果没有有效模型提供者，抛出错误
            return {"error": str(e)}

        except Exception as e:
            # 其他异常处理
            return {"error": f"An error occurred during decision making: {str(e)}"}
