import json
import logging
from typing import Dict, Any
from agentos_mvp.core.llm_adapter import LLMAdapterError
from agentos_mvp.core.llm_adapter import LLMAdapter
from agentos_mvp.runtime.task_loader_v2 import load_tasks_from_json

# 日志配置
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TaskIntakeError(Exception):
    """自定义异常，处理任务输入错误"""
    pass

class TaskIntake:
    def __init__(self, task_data: Dict[str, Any], model_name: str = "deepseek"):
        """
        初始化任务输入处理类
        :param task_data: 任务数据
        :param model_name: 选择调用的模型，默认是 deepseek
        """
        self.task_data = task_data
        self.model_name = model_name

    def validate_task_input(self):
        """
        任务数据验证，确保输入符合系统要求
        """
        required_fields = ['goal', 'product_name']
        for field in required_fields:
            if field not in self.task_data:
                logger.error(f"Missing required field: {field}")  # 增加日志输出
                raise TaskIntakeError(f"Missing required field: {field}")

        logger.info(f"Task input validated: {self.task_data}")

    def process_task_input(self) -> Dict[str, Any]:
        """
        处理任务输入，根据需要进行数据转换、模型选择等操作
        """
        # 验证任务输入
        self.validate_task_input()

        # 创建 LLMAdapter 实例，调用深度学习模型进行生成
        try:
            llm_adapter = LLMAdapter(model_name=self.model_name)
            result = llm_adapter.generate(task_type="director", prompt=self._build_prompt())
            return result
        except LLMAdapterError as e:
            logger.error(f"Error in LLM Adapter: {e}")
            raise

    def _build_prompt(self) -> str:
        """
        根据任务数据生成适合大模型调用的 prompt
        :return: 拼接好的 prompt 字符串
        """
        task = self.task_data
        prompt = (
            f"goal={task.get('goal', '')}\n"
            f"product_name={task.get('product_name', '')}\n"
            "请输出 video_angle, hooks, selling_points, script_outline, storyboard"
        )
        logger.info(f"Prompt built: {prompt}")
        return prompt

    def handle_task(self) -> Dict[str, Any]:
        """
        主方法：处理任务输入，调用决策层等模块
        :return: 最终的任务结果
        """
        try:
            result = self.process_task_input()
            logger.info(f"Task processed successfully, result: {result}")
            return result
        except TaskIntakeError as e:
            logger.error(f"Task intake error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

# 示例：初始化并处理任务输入
if __name__ == "__main__":
    task_data = {
        "goal": "生成完整方案",
        "product_name": "Test Product"
    }
    task_intake = TaskIntake(task_data)
    try:
        result = task_intake.handle_task()
        logger.info(f"Final Task Result: {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"Task processing failed: {e}")
