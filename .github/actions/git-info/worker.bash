#!/usr/bin/env bash
set -euo pipefail

echo "[BASH] Git Info"

# CONFIG_FILE=".github/configs/auto-commit.json"
CONFIG_FILE="${ACTION_PATH}/configs.json"

echo "从配置文件读取： ${CONFIG_FILE}..."

# ====================== 1. 确保 jq 已安装 ======================
if ! command jq > /dev/null 2>&1; then
    echo "Installing jq..."
    sudo apt-get update -qq
    sudo apt-get install -y jq
fi

# ====================== 2. 检查并创建默认 JSON ======================
if [ ! -f "${CONFIG_FILE}" ];
then
  echo "    ${CONFIG_FILE} 未找到, 按默认配置创建..."
  cat > "${CONFIG_FILE}" << EOF
{
    "git": {
        "user": {
            "name": "github-actions[bot]",
            "email": "github-actions[bot]@users.noreply.github.com"
        }
    }
}
EOF
fi

# ====================== 3. 动态读取 JSON 并设置所有 git config ======================
echo "读取应用全部参数..."

mapfile -t git_configs < <(jq -r '
    .git.user | to_entries[] |
    "user.\(.key)=\(.value)"
' "${CONFIG_FILE}" 2>/dev/null || echo "")

if [ ${#git_configs[@]} -gt 0 ]
then
    for line in "${git_configs[@]}"
    do
        if [ -n "$line" ]
        then
            key="${line%%=*}"
            value="${line#*=}"
            git config --local "${key}" "${value}"
        fi
    done
fi

echo "======== 参数列表 ========"
git config --local --list 
echo "========================="

