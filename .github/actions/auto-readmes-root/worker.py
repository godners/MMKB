#!/usr/bin/env python3
import os, re
from pathlib import Path

print("[PYTHON] Auto Readmes (Root)")

def parse_readme_template(content: str, base_dir: Path) -> str:
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip('\n')

        # 匹配 <include>xxx</include>
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
                    print(f"  嵌入失败: {filename} -> {e}")
            else:
                result.append(f"\n")
                print(f"  警告: 文件不存在 {filename}")
            i += 1
            continue

        # 匹配 <markdown> ... </markdown>（支持多行）
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
            # 去除首尾空行，但保留内部空行
            markdown_str = ''.join(markdown_content).strip('\n')
            if markdown_str:
                result.append(markdown_str + '\n')
            continue
        
        # 普通行直接保留
        result.append(lines[i])
        i += 1

    return ''.join(result)

def generate_readme_for_dir(dir_path: Path, root: Path):
    readme_path = dir_path / "README.md"
    template_path = dir_path / ".README"
    contents_path = dir_path / "CONTENTS.md"

     # 情况1: 存在 .README 模板
    if template_path.exists() and template_path.is_file():
        try:
            with open(template_path, encoding="utf-8") as f:
                template_content = f.read()
            final_content = parse_readme_template(template_content, dir_path)
        except Exception as e:
            print(f"读取 .README 失败: {dir_path} -> {e}")
            return
    
    # 情况2: 不存在 .README，但存在 CONTENTS.md
    elif contents_path.exists() and contents_path.is_file():
        try:
            with open(contents_path, encoding="utf-8") as f:
                final_content = f.read()
        except Exception as e:
            print(f"读取 CONTENTS.md 失败: {dir_path} -> {e}")
            return
    
    # 情况3: 两者都不存在
    else:
        return
    
    final_content = (final_content if final_content is not None else "").rstrip()

    # 写入或更新
    if readme_path.exists():
        try:
            old_content = readme_path.read_text(encoding="utf-8")
            if old_content.strip() == final_content.strip():
                return
        except Exception:
            pass

    readme_path.write_text(final_content, encoding="utf-8")
    print(f"  生成/更新: 根目录")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    repo = os.getenv("GITHUB_REPOSITORY", "N/A")
    ref = os.getenv("GITHUB_REF_NAME", "N/A")

    print(f"开始生成 README，仓库：{repo}，分支：{ref}，根路径：{root}")

    generate_readme_for_dir(root, root)
    
    print("根目录 README.md 处理完成")