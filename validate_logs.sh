#!/bin/bash

# 自动化日志验证脚本：确保日志文件记录了执行模式和执行结果

echo "验证日志功能..."

LOG_FILE="/home/gifylist/agentos/app/logs/task_execution.log"

# 检查日志文件是否存在
if [ -f "$LOG_FILE" ]; then
    echo "日志文件存在，验证日志记录..."
    # 检查日志中是否包含执行模式和执行结果
    if grep -q "Execution mode:" "$LOG_FILE" && grep -q "Execution result:" "$LOG_FILE"; then
        echo "日志记录正常，执行模式和执行结果已记录。"
    else
        echo "日志中未记录执行模式或执行结果，请检查日志记录配置。"
    fi
else
    echo "日志文件不存在，请检查 ExecutionAdapter 中的日志配置。"
fi
