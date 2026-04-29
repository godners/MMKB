#!/bin/bash
set -euo pipefail

echo "[BASH] Bot Summary"
echo ".github/actions/bot-summary/worker.bash"

TIME="$(date '+%F %T') (UTC)"
SUMMARY="[${TITLE}] ${TIME}: ${MESSAGE}"
echo "${SUMMARY}" >> $GITHUB_STEP_SUMMARY
echo "${SUMMARY}"
