#!/usr/bin/env bash
set -euo pipefail

echo "[BASH] Auto Version"
echo ".github/actions/auto-version/worker.bash"

# 尝试获取最新 Release 信息
RELEASE_INFO=$(gh release list --limit 1 2>/dev/null || echo "")

if [ -n "$RELEASE_INFO" ]
then
    RELEASE_TAG=$(echo "$RELEASE_INFO" | awk '{print $1}')
    PUBLISHED_AT=$(echo "$RELEASE_INFO" | awk '{print $4}')
    RELEASE_TIME=$(date -d "$PUBLISHED_AT" '+%F %T' 2>/dev/null || echo "N/A")
else
    RELEASE_TAG="No Release"
    RELEASE_TIME="N/A"
fi

# 收集 Commit 信息
COMMITS_DATA=$(git log --pretty=format:"%an|%aI|%s" |
    awk -F'|' '!seen[$1]++' | tr '\n' ';' | sed 's/;$//')

# 导出环境变量
echo "LAST_RELEASE_TAG=$RELEASE_TAG" >> $GITHUB_ENV
echo "LAST_RELEASE_TIME=$RELEASE_TIME" >> $GITHUB_ENV
echo "COMMITS_DATA=$COMMITS_DATA" >> $GITHUB_ENV

echo "Data load successful."
echo "   Tag: $RELEASE_TAG"
echo "   Time: $RELEASE_TIME"
echo "   Commits collected: $(echo "$COMMITS_DATA" | tr ';' '\n' | wc -l)"

