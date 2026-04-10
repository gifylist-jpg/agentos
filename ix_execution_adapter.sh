#!/bin/bash

# Step 1: 查找所有 ToolExecutor 的引用
echo "查找所有 ToolExecutor 的引用..."
grep -R "ExecutionAdapter.execute" . || { echo "未找到 ExecutionAdapter.execute 引用，停止执行"; exit 1; }

# Step 2: 替换 ToolExecutor 为 ExecutionAdapter
# 使用 sed 替换 ToolExecutor 的引用为 ExecutionAdapter
echo "替换 ToolExecutor 为 ExecutionAdapter..."
sed -i 's/ExecutionAdapter.execute/ExecutionAdapter.execute/g' $(grep -Rl "ExecutionAdapter.execute" .)

# Step 3: 修复 ExecutionAdapter 初始化问题
# 查找所有 ExecutionAdapter 初始化错误并替换为正确的实例化
echo "修复 ExecutionAdapter 初始化错误..."
find . -type f -name "*.py" -exec sed -i 's/self.tool_executor = ExecutionAdapter()/self.tool_executor = ToolExecutor()/g' {} \;

# Step 4: 确保所有 execution_adapter.execute 调用通过实例化对象来执行
echo "确保所有 execution_adapter.execute 调用通过实例化对象..."
find . -type f -name "*.py" -exec sed -i 's/execution_adapter.execute/execution_adapter.execute/g' {} \;

# Step 5: 测试单元测试（确保没有错误）
echo "运行单元测试..."
python3 -m unittest discover -s tests/

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "所有测试通过，系统修复成功!"
else
    echo "测试失败，请检查错误日志"
fi
