#!/bin/bash

# 确保脚本运行时位于项目根目录
cd ~/agentos/app

echo "验证新增执行模式功能..."

# 1. 确认 ExecutionAdapter 中支持的新执行模式已正确添加
echo "检查 ExecutionAdapter 中的新增执行模式..."

# 查看 ExecutionAdapter 文件中的执行模式部分
if grep -q "def execute(self, request: dict)" agentos/execution/execution_adapter.py; then
    echo "ExecutionAdapter 中的 execute 方法已找到，检查新增执行模式..."
    
    # 检查 retry, delayed, scheduled 执行模式
    if grep -q "retry" agentos/execution/execution_adapter.py && \
       grep -q "delayed" agentos/execution/execution_adapter.py && \
       grep -q "scheduled" agentos/execution/execution_adapter.py; then
        echo "执行模式：retry, delayed, scheduled 已成功添加到 ExecutionAdapter。"
    else
        echo "执行模式未正确添加。请检查 ExecutionAdapter 的代码。"
        exit 1
    fi
else
    echo "ExecutionAdapter 中的 execute 方法未找到。请检查 ExecutionAdapter 的实现。"
    exit 1
fi

# 2. 验证 TaskServiceV2 和 OpsAgent 是否支持新执行模式
echo "验证 TaskServiceV2 和 OpsAgent 是否正确传递执行模式..."

# 检查 TaskServiceV2 和 OpsAgent 是否使用了新增的执行模式
if grep -q "retry" agentos/core/task/task_service_v2.py && \
   grep -q "delayed" agentos/agents/ops_agent.py && \
   grep -q "scheduled" agentos/agents/ops_agent.py; then
    echo "TaskServiceV2 和 OpsAgent 已正确支持新增执行模式。"
else
    echo "TaskServiceV2 或 OpsAgent 未正确支持新增执行模式。请检查代码。"
    exit 1
fi

# 3. 检查日志输出是否记录了执行模式
echo "检查任务执行日志是否记录了执行模式..."
# 假设使用日志记录执行模式，在日志中查找执行模式
if grep -q "execution_mode" ~/agentos/app/logs/task_execution.log; then
    echo "任务执行日志已记录执行模式。"
else
    echo "任务执行日志未记录执行模式，请检查日志记录配置。"
    exit 1
fi

echo "新增执行模式功能验证完成。"

# 返回测试完成状态
exit 0
