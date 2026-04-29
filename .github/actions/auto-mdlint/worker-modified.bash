#!/bin/bash
set -euo pipefail

echo "[BASH] Auto MDLint (Modified)"
echo ".github/actions/auto-mdlint/worker-modified.bash"

TOTAL_MODIFIED=$(git status --porcelain | wc -l)
echo "TOTAL_MODIFIED=${TOTAL_MODIFIED}" >> $GITHUB_ENV