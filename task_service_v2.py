#!/bin/bash

# Step 1: 查找与 TaskService 相关的所有文件
echo "Searching for TaskService related files..."
find . -name "*task_service*"

# Step 2: 查找与 MultiModelDecisionService 相关的所有文件
echo "Searching for MultiModelDecisionService related files..."
find . -name "*multi_model_decision_service*"

# Step 3: 查找 TaskService 和 MultiModelDecisionService 的类定义
echo "Searching for class definitions in related files..."
grep -r "class TaskService" .
grep -r "class MultiModelDecisionService" .

# Step 4: 查找 TaskRequest 和 ApprovedDecision 的文件路径
echo "Searching for TaskRequest and ApprovedDecision related files..."
find . -name "*task_request*" -o -name "*approved_decision*"

# Step 5: 如果有测试文件，确认路径是否正确
echo "Checking test files for TaskService and MultiModelDecisionService..."
grep -r "TaskService" tests/
grep -r "MultiModelDecisionService" tests/

echo "Search completed. Please review the files and provide the relevant code."
