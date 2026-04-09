#!/bin/bash

# 自动化测试脚本：确保回滚、异常处理和执行模式的功能正常

echo "Running unit tests for execution modes and rollback mechanism..."

# 运行测试
python3 -m unittest discover tests/

echo "Unit tests executed. Check the results above for any failures."
