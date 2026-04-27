def load_tasks_from_json(path: str = "task.json"):
    """
    Task Intake v3：
    - 支持单任务（dict）
    - 支持多任务（list）
    - 自动补默认值
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"找不到任务文件: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # === 统一为 list ===
    if isinstance(data, dict):
        data = [data]

    tasks = []

    for item in data:
        # 必填校验
        missing = [k for k in REQUIRED_FIELDS if k not in item]
        if missing:
            raise ValueError(f"任务缺少字段: {missing}")

        # 默认值补全
        for k, v in DEFAULTS.items():
            if k not in item:
                item[k] = v

        tasks.append(TaskRequest(**item))

    return tasks
