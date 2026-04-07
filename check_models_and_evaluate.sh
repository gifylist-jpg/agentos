#!/bin/bash

echo "检查 agentos/core/task 中的类..."
grep -r "class " agentos/core/task/
grep -r "def evaluate(" agentos/core/task/

echo "检查 agentos/core/decision 中的类..."
grep -r "class " agentos/core/decision/
grep -r "def evaluate(" agentos/core/decision/

echo "检查 agentos/core/domain 中的类..."
grep -r "class " agentos/core/domain/
grep -r "def evaluate(" agentos/core/domain/
