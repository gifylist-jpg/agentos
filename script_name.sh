#!/bin/bash
# 查找并确保执行路径都通过 ExecutionAdapter 执行

# 查找所有执行路径，并替换
grep -R ".execute(" . | grep -v ExecutionAdapter | while read line; do
    echo "Updating: $line"
    # 替换为正确的 ExecutionAdapter 执行路径
    sed -i 's/.*\.execute(.*)/self.execution_adapter.execute(request)/' "$line"
done
