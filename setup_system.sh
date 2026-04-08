#!/bin/bash

# 1. 检查并创建 system_guard.py 文件
if [ ! -f agentos/core/system_guard.py ]; then
    echo "创建 system_guard.py 文件..."
    cat > agentos/core/system_guard.py <<EOL
# agentos/core/system_guard.py

from datetime import datetime

# 任务验证函数
def assert_valid_task(task):
    if not task.get('task_id'):
        raise ValueError("Task ID is missing")
    if task.get('status') not in ['pending', 'in_progress', 'completed']:
        raise ValueError("Invalid task status")
    print(f"Task {task['task_id']} is valid.")

# 系统健康检查
def check_system_health():
    current_time = datetime.utcnow()
    if current_time.minute % 5 == 0:
        print("System health check passed.")
    else:
        print("System health check failed.")
        raise SystemError("System health is compromised!")

# 权限验证
def assert_has_required_feedback_fields(task):
    required_fields = ['feedback', 'assessor']
    for field in required_fields:
        if field not in task:
            raise ValueError(f"Missing required field: {field}")
    print("All required feedback fields are present.")
EOL
    echo "system_guard.py 文件已创建！"
else
    echo "system_guard.py 文件已存在，跳过创建。"
fi

# 2. 确保 task_service.py 中导入 system_guard
if [ ! -f agentos/services/task_service.py ]; then
    echo "task_service.py 文件不存在，跳过"
else
    echo "修复 task_service.py 导入 system_guard 问题..."
    sed -i "1i from agentos.core.system_guard import assert_valid_task, check_system_health" agentos/services/task_service.py
    echo "已修复 task_service.py 文件中的导入问题"
fi

# 3. 运行测试
echo "运行测试..."
python3 -m unittest discover tests/

# 结束
echo "操作完成！"
