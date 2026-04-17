#!/usr/bin/env bash
set -euo pipefail

JSON_FILE=".github/configs/git-info.json"

echo "Reading git configuration from ${JSON_FILE}..."

# ====================== 1. 确保 jq 已安装 ======================
if ! command jq > /dev/null 2>&1; then
    echo "Installing jq..."
    sudo apt-get update -qq
    sudo apt-get install -y jq
fi

# ====================== 2. 检查并创建默认 JSON ======================
if [ ! -f "${JSON_FILE}" ];
then
  echo "    ${JSON_FILE} not found, creating default..."
  cat > "${JSON_FILE}" << EOF
{
    "user": {
        "name": "github-actions[bot]",
        "email": "github-actions[bot]@users.noreply.github.com"
    }
}
EOF
fi

# ====================== 3. 动态读取 JSON 并设置所有 git config ======================
echo "Reading and alllying git configurations from JSON"

# 先把 jq 输出保存到临时变量，避免 pipefail + while read 的经典 broken pipe 问题
mapfile -t configs < <(jq -r '
    to_entries[] |
    .key as $section |
    (.value | to_entries[]?) |
    "\($section).\(.key)=\(.value)"
' "${JSON_FILE}" 2>/dev/null || echo "")

if [ ${#configs[@]} -eq 0 ]
then
    echo "    No configurations found in JSON or JSON is invalid."
else
    for line in "${configs[@]}"
    do
        if [ -n "$line" ]
        then
            key="${line%%=*}"
            value="${line#*=}"
            echo "    git confg --local ${key} \"${value}\""
            git config --local "${key}" "${value}"
        fi
    done
fi


git config --local --list 

