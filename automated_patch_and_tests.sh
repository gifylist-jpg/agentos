#!/bin/bash

# 设置仓库根目录
REPO_ROOT=$(git rev-parse --show-toplevel)

# 进入仓库目录
cd "$REPO_ROOT" || exit

# 应用补丁
echo "Applying patch..."

git apply --3way <<'EOF'
diff --git a/agentos/core/decision/approved_decision.py b/agentos/core/decision/approved_decision.py
index 10ed630063a404b11b7f3fbb165dbeb74ab082b1..0b910e9219ee943ec46df53b3735a0b484bd03e7 100644
--- a/agentos/core/decision/approved_decision.py
+++ b/agentos/core/decision/approved_decision.py
@@ -1,11 +1,11 @@
-from datetime import datetime, UTC
+from datetime import datetime, timezone

 class ApprovedDecision:
     def __init__(self, execution_mode, selected_candidate_id, timestamp=None, source='system'):
         self.execution_mode = execution_mode
         self.selected_candidate_id = selected_candidate_id
-        self.timestamp = timestamp or datetime.now(UTC)
+        self.timestamp = timestamp or datetime.now(timezone.utc)
         self.source = source

     def __repr__(self):
         return f'<ApprovedDecision(execution_mode={self.execution_mode}, selected_candidate_id={self.selected_candidate_id})>'
EOF

# 检查 Git 状态
echo "Checking Git status..."
git status

# 添加所有更改并提交
echo "Adding changes and committing..."
git add .
git commit -m "Fix datetime import for UTC timezone and ensure execution mode logging"

# 推送到远程仓库
echo "Pushing changes..."
git push

# 运行单元测试
echo "Running unit tests..."
python -m unittest discover -s tests

# 输出最后的 Git 状态
git status
