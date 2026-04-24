#!/usr/bin/env python3
import os
import json5
import re
from pathlib import Path

print("[PYTHON] Auto Readmes")
print(".github/actions/auto-readmes/worker.py")

# 全局计数器
total_scanned = 0
total_modified = 0

CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json5.load(f)
    except:
        return {}
    
config = load_config()

def parse_readme_template(content: str, base_dir: Path) -> str:
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip('\n')
        include_match = re.match(r'^\s*<include>\s*(.+?)\s*</include>\s*$', line, re.IGNORECASE)
        if include_match:
            filename = include_match.group(1).strip()
            include_path = (base_dir / filename).resolve()
            if include_path.is_file() and include_path.is_relative_to(base_dir.resolve()):
                try:
                    with open(include_path, encoding="utf-8") as f:
                        included = f.read()
                    result.append(included)
                except Exception as e:
                    result.append(f"\n")
            else:
                result.append(f"\n")
            i += 1
            continue

        markdown_match = re.match(r'^\s*<markdown>\s*$', line, re.IGNORECASE)
        if markdown_match:
            i += 1
            markdown_content = []
            while i < n:
                inner_line = lines[i].rstrip('\n')
                if re.match(r'^\s*</markdown>\s*$', inner_line, re.IGNORECASE):
                    i += 1
                    break
                markdown_content.append(lines[i])
                i += 1
            markdown_str = ''.join(markdown_content).strip('\n')
            if markdown_str:
                result.append(markdown_str + '\n')
            continue
        
        result.append(lines[i])
        i += 1
    
    return ''.join(result)

def generate_readme_for_dir(dir_path: Path, root: Path):
    global total_modified
    if dir_path.name.startswith('.'):
        return
    
    readme_path = dir_path / "README.md"
    template_path = dir_path / ".README"
    contents_path = dir_path / "CONTENTS.md"

    if template_path.exists() and template_path.is_file():
        try:
            with open(template_path, encoding="utf-8") as f:
                template_content = f.read()
            final_content = parse_readme_template(template_content, dir_path)
        except Exception as e:
            return
    elif contents_path.exists() and contents_path.is_file():
        try:
            with open(contents_path, encoding="utf-8") as f:
                final_content = f.read()
        except Exception as e:
            return
    else:
        return

    final_content = (final_content if final_content is not None else "").rstrip()

    if readme_path.exists():
        try:
            old_content = readme_path.read_text(encoding="utf-8")
            if old_content.strip() == final_content.strip():
                return
        except Exception:
            pass

    readme_path.write_text(final_content, encoding="utf-8")
    total_modified += 1
    print(f"  生成/更新: {dir_path.relative_to(root) or '根目录'}")

def set_github_env_var(key, value):
    """将变量写入 GitHub 环境文件"""
    env_file = os.getenv("GITHUB_ENV")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"非 GitHub 环境: {key}={value}")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    repo = os.getenv("GITHUB_REPOSITORY", "godners/MMKB")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    print(f"开始生成 READMEs，仓库：{repo}，分支：{ref}，根路径：{root}")

    for dirpath, dirnames, _ in os.walk(root):
        total_scanned += 1
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        current = Path(dirpath)
        if not current.name.startswith('.'):
            generate_readme_for_dir(current, root)
    
    # 输出结果到环境变量
    set_github_env_var("TOTAL_SCANNED", total_scanned)
    set_github_env_var("TOTAL_MODIFIED", total_modified)
    
    print(f"完成。共扫描目录: {total_scanned}，修改文件: {total_modified}")