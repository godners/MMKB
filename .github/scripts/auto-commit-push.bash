#!/usr/bin/env bash
set -euo pipefail

# ====================== 从 inputs 读取参数 ======================
# 默认值
DEFAULT_PATTERNS=("**/*.md" "*.md")
DEFAULT_COMMIT_PREFIX="Auto Commit"

# 读取 commit-prefix（优先使用传入值）
COMMIT_PREFIX="${INPUT_COMMIT_PREFIX:-${DEFAULT_COMMIT_PREFIX}}"

# 读取 patterns（支持多行列表）
if [ -n "${INPUT_PATTERNS:-}" ]
then
    # 将多行输入转为数组
    mapfile -t PATTERNS <<< "${INPUT_PATTERNS}"
else
    # 使用默认值
    PATTERNS=("${DEFAULT_PATTERNS[@]}")
fi

# 显示配置
echo "Commit Prefix : ${COMMIT_PREFIX}"
for pattern in "${PATTERNS[@]}"; do
    echo "   Pattern     : ${pattern}"
done

# ====================== 执行 git add ======================
echo "Adding files..."
for pattern in "${PATTERNS[@]}"; do
    if [ -n "${pattern}" ]; then
        echo "   git add \"${pattern}\""
        git add "${pattern}" 2>/dev/null || true
    fi
done

# 检查是否有实际变更
if git diff --staged --quiet; then
    echo "没有检测到任何变更，跳过提交。"
    exit 0
fi

# ====================== Commit & Push ======================
COMMIT_TIME=$(date -u -d '8 hours' '+%F %T')
COMMIT_MESSAGE="${COMMIT_PREFIX} on ${COMMIT_TIME}"

echo "Committing: ${COMMIT_MESSAGE}"
git commit -m "${COMMIT_MESSAGE}"

echo "Pushing changes..."
git push

echo "Auto commit and push completed successfully!"