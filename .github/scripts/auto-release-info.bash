#!/bin/bash
set -euo pipefail

TODAY=$(date -u -d '8 hours' '+%Y.%m.%d')
TAG="${TODAY}.auto"
echo "tag=${TAG}" >> $GITHUB_OUTPUT

TIME=$(date -u -d '8 hours' '+%F %T')
echo "time=${TIME}" >> $GITHUB_OUTPUT

echo "Generated tag: ${TAG}" >> $GITHUB_STEP_SUMMARY
echo "Generated time (GMT+8): ${TIME}" >> $GITHUB_STEP_SUMMARY