#!/usr/bin/env bash
set -euo pipefail

echo "[BASH] Git Commit"

CONFIG_FILE="${ACTION_PATH}/configs.jsonc"

# ====================== 1. 确保 jq 已安装 ======================
if ! command jq > /dev/null 2>&1; then
    echo "Installing jq..."
    sudo apt-get update -qq
    sudo apt-get install -y jq
fi

# 读取 commit-prefix（如果 Inputs 传入则使用，否则后面从 JSON 读取）
COMMIT_PREFIX="${INPUT_COMMIT_PREFIX:-}"

# 读取 patterns（支持多行输入）
if [ -n "${INPUT_PATTERNS:-}" ]
then
    mapfile -t PATTERNS <<< ${INPUT_PATTERNS}
else
    PATTERNS=()
fi

# ====================== 2. 如果 Inputs 未提供，则从 JSON 读取 ==================
if [ -z "${COMMIT_PREFIX}" ] || [ ${#PATTERNS[@]} -eq 0 ];
then
    echo "Inputs 未提供参数，从 ${CONFIG_FILE} 中读取默认值..."

    if [ -f "${JSON_FILE}" ];
    then
        # 读取 commit-prefix（如果 Inputs 为空则从 JSON 获取）
        if [ -z "${COMMIT_PREFIX}" ]
        then
            COMMIT_PREFIX=$(grep -v '^//' "${CONFIG_FILE}" |
                jq -r '.default["commit-prefix"] // ""')
        fi

        # 从 JSON 读取 patterns，如果不存在则使用 DEFAULT_PATTERNS
        if [ ${#PATTERNS[@]} -eq 0 ]
        then
            mapfile -t PATTERNS < <(grep -v '^//' "${CONFIG_FILE}" |
                jq -r '.default.patterns[]? // empty')
        fi
    else
        echo "未找到 ${CONFIG_FILE}，使用默认值..."
    fi
fi

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

CURRENT_BRANCH=$(git branch --show-current)

echo "Pushing changes..."
git stash save "Stash dirty files before pull" || true
git pull --rebase origin "${CURRENT_BRANCH}"
git stash pop || true
git push origin "${CURRENT_BRANCH}"

echo "Auto commit and push completed successfully!"