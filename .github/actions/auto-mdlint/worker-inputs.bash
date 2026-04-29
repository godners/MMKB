#!/bin/bash
set -euo pipefail

echo "[BASH] Auto MDLint (Inputs)"
echo ".github/actions/auto-mdlint/worker-inputs.bash"

CLEAN_PATTERNS=$(echo "$RAW_PATTERNS" | awk 'NF')
PATTERNS_COUNT=$(echo "$CLEAN_PATTERNS" | wc -l)
LIST=$(echo "$CLEAN_PATTERNS" | tr '\n' ',' | sed 's/,$//')
PATTERNS_LIST=$(echo "$LIST" | sed 's/,/, /g')

echo "PATTERNS_LIST=${PATTERNS_LIST}" >> $GITHUB_ENV
echo "PATTERNS_COUNT=${PATTERNS_COUNT}" >> $GITHUB_ENV