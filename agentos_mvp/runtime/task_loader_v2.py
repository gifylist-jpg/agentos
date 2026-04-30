from pathlib import Path
import json
from agentos_mvp.schemas.task_request import TaskRequest

# 必填字段列表包括 'objective'
REQUIRED_FIELDS = ["goal", "product_name", "objective"]  # 将 objective 添加为必填字段
DEFAULTS = {
    "objective": "default",
    "ai_generation_needed": True,
    "output_type": "Video"
}

def load_tasks_from_json(path: str = "task.json"):
    """
    Task Intake v3：
    - 支持单任务（dict）
    - 支持多任务（list）
    - 自动补默认值
    """
    file_path = Path(path)

    # 如果任务文件不存在，抛出异常
    if not file_path.exists():
        raise FileNotFoundError(f"找不到任务文件: {path}")

    # 打开任务文件并读取数据
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 如果是单个任务数据（dict），将其转换为列表格式
    if isinstance(data, dict):
        data = [data]

    tasks = []

    for item in data:
        # 记录任务字段
        print(f"Validating task: {item}")

        # 校验必填字段
        missing = [k for k in REQUIRED_FIELDS if k not in item]

        # 如果缺失字段，抛出 ValueError 异常
        if missing:
            print(f"Missing fields detected: {missing}")
            raise ValueError(f"任务缺少字段: {', '.join(missing)}")

        # 自动填充默认值
        for k, v in DEFAULTS.items():
            if k not in item:
                item[k] = v

        tasks.append(TaskRequest(**item))  # 创建 TaskRequest 对象

    return tasks
