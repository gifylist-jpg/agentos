#!/usr/bin/env bash
set -euo pipefail

# 获取 Git 仓库根目录
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# 创建临时补丁文件
PATCH_FILE="$(mktemp)"
cleanup() {
  rm -f "$PATCH_FILE"
}
trap cleanup EXIT

# 将补丁内容写入临时文件
cat >"$PATCH_FILE" <<'PATCH'
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

PATCH

log() {
  printf '[apply_patch] %s\n' "$*"
}

log "repository: $REPO_ROOT"
log "patch file generated: $PATCH_FILE"

# 验证补丁并应用
if git apply --check "$PATCH_FILE"; then
  log "patch validation passed, applying with 3-way merge"
  git apply --3way "$PATCH_FILE"
  log "patch applied successfully"
elif git apply --reverse --check "$PATCH_FILE"; then
  log "patch already applied; skipping"
else
  log "patch failed validation and is not already applied"
  exit 1
fi

# 运行单元测试，验证补丁应用后系统是否正常
log "running unit tests"
python -m unittest discover -s tests
log "done"
