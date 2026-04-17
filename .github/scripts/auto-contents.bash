#!/bin/bash
set -euo pipefail

git config --local user.email "github-actions[bot]@users.noreply.github.com"
git config --local user.name "github-actions[bot]"

git add "**/CONTENTS.md" "CONTENTS.md"
if git diff --cached --quiet
then
    echo "没有检测到任何变更，跳过提交。"
else
    COMMIT_TIME=$(date '+%F %T')
    git commit -m "Auto Contents on ${COMMIT_TIME}"
    git push
fi