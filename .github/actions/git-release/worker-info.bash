#!/bin/bash
set -euo pipefail

echo "[BASH] Git Release (Info)"
echo ".github/actions/git-release/worker-info.bash"

TODAY=$(date -u -d '8 hours' '+%Y.%m.%d')
TAG="${TODAY}.auto"
echo "tag=${TAG}" >> $GITHUB_OUTPUT

TIME=$(date -u -d '8 hours' '+%F %T')
echo "time=${TIME}" >> $GITHUB_OUTPUT
