#!/bin/bash

# 检查 MultiModelDecisionService 类和 evaluate 方法
echo "检查 MultiModelDecisionService 类是否存在..."
grep -r "class MultiModelDecisionService" agentos/core/decision/

echo "检查模型是否实现 evaluate 方法..."
grep -r "def evaluate(" agentos/core/decision/

echo "检查 TaskServiceV2 类是否使用正确的 Decision 类..."
grep -r "class TaskServiceV2" agentos/core/task/
grep -r "generate_decision" agentos/core/task/task_service_v2.py

# 检查 ApprovedDecision 类
echo "检查 ApprovedDecision 类..."
grep -r "class ApprovedDecision" agentos/core/decision/

echo "检查代码中的决策生成和任务处理逻辑是否存在问题..."
