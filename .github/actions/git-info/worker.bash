#!/usr/bin/env bash
set -euo pipefail

echo "[BASH] Git Info"
echo ".github/actions/git-info/worker.bash"

CONFIG_FILE="${ACTION_PATH}/configs.jsonc"

if [ ! -f "${CONFIG_FILE}" ]; then
  echo "    ${CONFIG_FILE} 未找到..."
  exit 1
fi

echo "从配置文件读取： ${CONFIG_FILE}..."

# 读取配置到数组，确保过滤掉空行
# mapfile -t git_configs < <(grep -v '^//' "${CONFIG_FILE}" |
#     jq -r 'paths(scalars) as $p | "\(path($p) | join("."))=\(getpath($p))"' 2>/dev/null)

mapfile -t git_configs < <(sed 's|//.*||g' "${CONFIG_FILE}" | 
    jq -r 'paths(scalars) as $p | "\(path($p) | join("."))=\(getpath($p))"' | 
    grep -v '^=')


# 再次过滤掉数组中可能存在的空字符串，确保计数准确
git_configs=(${git_configs[@]})

# 计算读取到的条目数量
COUNT=${#git_configs[@]}

# 输出到 GitHub 环境变量
echo "CONFIG_COUNT=$COUNT" >> "$GITHUB_ENV"
echo "已从配置中读取并应用了 $COUNT 条 Git 设置。"

# 循环应用配置
for line in "${git_configs[@]}"; do
    if [ -n "$line" ]; then
        key="${line%%=*}"
        value="${line#*=}"
        echo "Applying: ${key} === ${value}"
        git config --local "${key}" "${value}"
    fi
done
