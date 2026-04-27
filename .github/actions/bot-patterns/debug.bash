#!/bin/bash
set -euo pipefail

echo "[BASH] Bot Patterns (Debug)"
echo ".github/actions/bot-patterns/debug.bash"

echo "================== 分隔符 ==================="
echo "\${{ inputs.separator }} = \"${SEPARATOR}\""
echo "============ 匹配模式值（字符串） ============"
echo "\${{ inputs.patterns }} = "
echo "${PATTERNS}"
echo "============ 匹配输出值（字符串） ============"
echo "\${{ steps.glob.outputs.paths }} = ${PATHS}"
echo "============ 匹配文件清单（列表） ============"
echo "${PATHS}" | tr "${SEPARATOR}" '\n' |
    while IFS= read -r file
    do
        if [ -n "$file" ]
        then
            echo "$file"
        fi
    done
echo "============================================="
