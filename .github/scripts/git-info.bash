#!/usr/bin/env bash
set -euo pipefail

JSON_FILE="../configs/git-info.json"

echo "Reading git configuration from ${JSON_FILE}..."

# ====================== 1. 确保 jq 已安装 ======================
if ! command jq > /dev/null 2>&1; then
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

# 使用 jq 递归遍历所有 leaf 节点（key路径 -> value），自动转为 git config key
jq -r '
    to_entries[] |
    .key as $section |
    .value |
    to_entries[] |
    "\($section).\(.key)=\(.value)"
' "${JSON_FILE}" |
while IFS=read -r config_line; do
    if [ -n "${config_line}" ]; then
        echo "    git confg --local ${config_line}"
        git config --local "${config_line%%=*}" "${config_line#*=}"
    fi
done

git config --local --list 

