#!/bin/bash

echo "检查所有模型类是否实现 evaluate 方法..."

# 检查 agentos/core/models 目录下的模型类
echo "检查 agentos/core/models/ 中的类..."
grep -r "class " agentos/core/models/
grep -r "def evaluate(" agentos/core/models/

# 检查 agentos/core/decision 目录下的模型类
echo "检查 agentos/core/decision/ 中的类..."
grep -r "class " agentos/core/decision/
grep -r "def evaluate(" agentos/core/decision/

# 检查所有模型类中是否有评估方法
echo "检查所有模型类是否实现 evaluate 方法..."
grep -r "def evaluate(" agentos/core/
