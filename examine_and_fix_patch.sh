#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./examine_and_fix_patch.sh --patch_file /path/to/patch.diff [--test_cmd "pytest -q"]

Description:
  Reviews a patch by validating it can be applied with 3-way merge,
  applies it to the current git repository, and optionally runs tests.
USAGE
}

PATCH_FILE=""
TEST_CMD=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --patch_file)
      PATCH_FILE="${2:-}"
      shift 2
      ;;
    --test_cmd)
      TEST_CMD="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$PATCH_FILE" ]]; then
  echo "Error: --patch_file is required." >&2
  usage
  exit 2
fi

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "Error: patch file not found: $PATCH_FILE" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: current directory is not a git repository." >&2
  exit 1
fi

echo "[1/4] Checking patch applicability..."
git apply --check --3way "$PATCH_FILE"

echo "[2/4] Applying patch..."
git apply --3way "$PATCH_FILE"

echo "[3/4] Showing changed files..."
git status --short

if [[ -n "$TEST_CMD" ]]; then
  echo "[4/4] Running tests: $TEST_CMD"
  eval "$TEST_CMD"
else
  echo "[4/4] No tests requested."
fi

echo "Done. Review changes with: git diff"
