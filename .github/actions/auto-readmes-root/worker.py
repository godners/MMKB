#!/usr/bin/env python3
import os, json
from pathlib import Path

print("[PYTHON] Auto Readmes (Root)")
print(".github/actions/auto-readmes-root/worker.py")

def parse_readme_template(template_path: Path, dir_path: Path) -> str:
    """解析 .README JSON 模板文件并返回生成的文本内容"""
    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    content_buffer = []
    for item in data:
        if item.get('type') == 'text':
            content_buffer.append(item.get('value', ''))
        elif item.get('type') == 'file':
            target_file = dir_path / item.get('value', '')
            if target_file.exists():
                content_buffer.append(target_file.read_text(encoding='utf-8'))
            else:
                content_buffer.append(f"<!-- Include Failed: {target_file.resolve()} -->")
    
    return '\n'.join(content_buffer)

def main():
    root = Path.cwd()
    template_path = root / ".README"
    contents_path = root / "CONTENTS.md"
    readme_path = root/ "README.md"

    if template_path.exists():
        new_content = parse_readme_template(template_path, root)
    elif contents_path.exists():
        new_content = contents_path.read_text(encoding='utf-8')
    else:
        return
    
    old_content = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

    updated = new_content != old_content
    if updated:
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"README.md updated from {template_path.name if template_path.exists() else contents_path.name}")

    status = "ROOT README has been Updated." if updated else "ROOT README has NO Changed."
    if env_file := os.getenv("GITHUB_ENV"):
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"README_STATUS={status}\n")

if __name__ == "__main__":
    main()