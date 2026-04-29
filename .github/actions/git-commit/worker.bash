#!/usr/bin/env bash
set -euo pipefail

echo "[BASH] Git Commit"
echo ".github/actions/git-commit/worker.bash"

# 默认设置状态为 Canceled (用于未产生变更的情况)
echo "COMMIT_STATUS=Commit has been Canceled" >> "$GITHUB_ENV"

CONFIG_FILE="${ACTION_PATH}/configs.jsonc"

# 加载配置函数
load_config() {
    if [[ -z "${INPUT_COMMIT_PREFIX:-}" ]]; then
        COMMIT_PREFIX=$(sed 's|//.*||g' "${CONFIG_FILE}" 2>/dev/null | jq -r '.default["commit-prefix"] // ""')
    else
        COMMIT_PREFIX="${INPUT_COMMIT_PREFIX}"
    fi

    if [[ -z "${INPUT_PATTERNS:-}" ]]; then
        mapfile -t PATTERNS < <(sed 's|//.*||g' "${CONFIG_FILE}" "${CONFIG_FILE}" 2>/dev/null | jq -r '.default.patterns[]? // empty')
    else
        mapfile -t PATTERNS <<< "${INPUT_PATTERNS}"
    fi
}

load_config

# 添加文件
echo "Adding files..."
for pattern in "${PATTERNS[@]}"; do
    trimmed_pattern=$(echo "$pattern" | xargs)
    if [[ -n "$trimmed_pattern" ]]; then
        git add "$trimmed_pattern" 2>/dev/null || true
    fi
done

if [ "$INPUT_CHECK_CHANGED" != "true" ]
then
    echo "check-changed = false，强制执行提交"
else
    # 检查变更
    if git diff --staged --quiet
    then
        echo "没有检测到任何变更，跳过提交。"
        exit 0
    fi
fi

# 执行提交
COMMIT_TIME=$(date -u -d '8 hours' '+%F %T')
COMMIT_MESSAGE="${COMMIT_PREFIX:-Auto Commit} on ${COMMIT_TIME}"

echo "Committing: ${COMMIT_MESSAGE}"
if git commit -m "${COMMIT_MESSAGE}"; then
    # 提交成功，更新状态字符串
    echo "COMMIT_STATUS=Commit has been Completed" >> "$GITHUB_ENV"
    
    # Push 操作
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Pushing changes..."
    git stash save "Stash dirty files before pull" || true
    git pull --rebase origin "${CURRENT_BRANCH}"
    git stash pop || true
    git push origin "${CURRENT_BRANCH}"
    echo "Git commit and push completed successfully!"
fi