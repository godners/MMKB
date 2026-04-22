#!/usr/bin/env bash
set -e

echo "[BASH] Auto Version"

echo "Load last release info..."
# TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName' 2>/dev/null || echo "暂无 Release")
#TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName' 2>/dev/null || echo "暂无 Release")
# TAG=$(gh release list --limit 1 | head -n 1 | awk '{print $1}' 2>/dev/null || echo "暂无 Release")
PUBLISHED_AT=$(gh release list --limit 1 --json publishedAt -q '.[0].publishedAt' 2>/dev/null || echo "null" )

# 1. 直接获取完整输出并打印，确保不是环境变量问题
RAW_RELEASE=$(gh release list --limit 1)
echo "DEBUG: 捕获到的原始数据: '$RAW_RELEASE'"

# 2. 检查输出是否为空
if [ -z "$RAW_RELEASE" ]; then
    echo "DEBUG: 未捕获到 Release 数据"
    TAG="暂无 Release"
else
    # 3. 使用 awk 提取第一列，并赋值给 TAG
    # 如果输出包含制表符，awk 默认处理
    TAG=$(echo "$RAW_RELEASE" | awk '{print $1}')
    echo "DEBUG: 提取后的 TAG 变量值: '$TAG'"
fi

# 4. 最终赋值
if [ -z "$TAG" ] || [ "$TAG" = "null" ]; then
    RELEASE_TAG="暂无 Release"
else
    RELEASE_TAG="$TAG"
fi


if [ "$TAG" = "null" ] || [ -z "$TAG" ] || [ -z "$PUBLISHED_AT" ] || [ "$PUBLISHED_AT" = "null" ]
then
    RELEASE_TAG="暂无 Release"
    RELEASE_TIME="N/A"
else
    if [[ "$PUBLISHED_AT" == *Z ]]
    then
        PUBLISHED_AT="${PUBLISHED_AT%Z}+00:00"
    fi
    TIMESTAMP=$(date -d "$PUBLISHED_AT" +%s 2>/dev/null || echo "")
    if [ -n "$TIMESTAMP" ]
    then
        NEW_TIMESTAMP=$((TIMESTAMP + 28800))
        RELEASE_TIME=$(date -d "@$NEW_TIMESTAMP" '+%T %F')
    else
        RELEASE_TIME="N/A"
    fi
fi

echo "Load last commit by authors..."
COMMITS_DATA=$(git log --pretty=format:"%an|%aI|%s" | awk -F'|' '!seen[$1]++' | tr '\n' ';' | sed 's/;$//')

echo "LAST_RELEASE_TAG=$RELEASE_TAG" >> $GITHUB_ENV
echo "LAST_RELEASE_TIME=$RELEASE_TIME" >> $GITHUB_ENV
echo "COMMITS_DATA=$COMMITS_DATA" >> $GITHUB_ENV

echo "Data load successful."
echo "   Tag: $RELEASE_TAG"
echo "   Time: $RELEASE_TIME"
echo "   Commits collected: $(echo "$COMMITS_DATA" | tr ';' '\n' | wc -l)"

