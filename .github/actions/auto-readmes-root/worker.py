#!/usr/bin/env python3
import os, re
from pathlib import Path

print("[PYTHON] Auto Readmes (Root)")

# 正则表达式预编译
INCLUDE_RE = re.compile(r'^\s*<include>\s*(.+?)\s*</include>\s*$', re.I)
MARKDOWN_RE = re.compile(r'^\s*<markdown>\s*$', re.I)

def parse_template(content: str, base_dir: Path) -> str:
    lines = content.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if match := INCLUDE_RE.match(line):
            path = (base_dir / match.group(1).strip()).resolve()
            result.append(path.read_text(encoding='utf-8') if path.is_file() and path.is_relative_to(base_dir) else "")
        elif MARKDOWN_RE.match(line):
            i += 1
            block = []
            while i < len(lines) and not MARKDOWN_RE.match(lines[i]):
                block.append(lines[i])
                i += 1
            result.append('\n'.join(block))
        else:
            result.append(line)
        i += 1
    return '\n'.join(result).strip()

def main():
    root = Path.cwd()
    # 优先查找 .README，其次查找 CONTENTS.md
    src = next((root / f for f in [".README", "CONTENTS.md"] if (root / f).exists()), None)
    if not src: return

    # 生成内容
    content = parse_template(src.read_text(encoding='utf-8'), root) if src.name == ".README" else src.read_text(encoding='utf-8')
    content = content.strip()

    # 检查并更新
    dest = root / "README.md"
    old_content = dest.read_text(encoding='utf-8').strip() if dest.exists() else ""
    
    updated = content != old_content
    if updated:
        dest.write_text(content, encoding='utf-8')
        print(f"README.md updated from {src.name}")

    # 输出状态到 GITHUB_ENV
    status = "ROOT README has been Updated." if updated else "ROOT README has NO Changed."
    if env_file := os.getenv("GITHUB_ENV"):
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"README_STATUS={status}\n")

if __name__ == "__main__":
    main()