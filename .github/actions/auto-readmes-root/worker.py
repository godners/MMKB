#!/usr/bin/env python3
import re
from pathlib import Path

print("[PYTHON] Auto Readmes (Root)")

include_regex=r'^\s*<include>\s*(.+?)\s*</include>\s*$'
markdown_regex=r'^\s*<markdown>\s*$'

def parse_template(content: str, base_dir: Path) -> str:
    lines = content.splitlines(keepends=True)
    result = []
    i = 0

    while i < n:
        line = lines[i].rstrip('\n')

        # 处理 <include>
        if match := re.match(include_regex, line, re.IGNORECASE):
            path = (base_dir / match.group(1).strip()).resolve()
            if path.is_file() and path.is_relative_to(base_dir.resolve()):
                result.append(path.read_text(encoding='utf-8'))
            else:
                result.append(f"\n")

        # 处理 <markdown>
        elif re.match(markdown_regex, line, re.IGNORECASE):
            i += 1
            block = []
            while i < len(lines) and not re.match(markdown_regex, lines[i], re.IGNORECASE):
                block.append(lines[i]
                i += 1
            result.append(''.join(block))
        else:
            result.append(lines[i])
        i += 1
    return ''.join(result).strip()

if __name__ == "__main__":
    root = Path.cwd()
    readme_path = root / ".README"
    contents_path = root / "CONTENTS.md"

    # 1. 明确源文件查找逻辑
    if readme_path.exists():
        src = readme_path
    elif contents_path.exists():
        src = contents_path
    else:
        return
    
    # 2. 根据文件类型处理内容
    raw_text = src.read_text(encoding='utf-8')
    
    if src.name == ".README":
        content = parse_template(raw_text, root)
    else:
        content = raw_text
    
    content = content.strip()

    # 3.写入文件
    dest = root / README.md
    needs_update = True

    if dest.exists():
        current_content = dest.read_text(encoding='utf-8').strip()
        if current_content = content:
            needs_update = False

    if needs_update:
        dest.write_text(content, encoding='utf-8')
        print(f"README.md updated from {src.name}")

if __name__ == "__main__":
    main()