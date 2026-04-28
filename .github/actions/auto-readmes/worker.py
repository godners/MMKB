#!/usr/bin/env python3
import os, re
from pathlib import Path

print("[PYTHON] Auto Readmes")
print(".github/actions/auto-readmes/worker.py")

# 全局计数器
total_folders = 0
total_updates = 0

# REGEX_INCLUDE = r'^\s*<include>\s*.+?\s*</include>\s*$'
# REGEX_MARKDOWN = r'^\s*</markdown>\s*$'
REGEX_INCLUDE = r'^\s*<include>\s*(.+?)\s*</include>\s*$'
REGEX_MARKDOWN_START = r'^\s*<markdown>(.*)$' 
REGEX_MARKDOWN_CLOSE = r'^(.*)</markdown>\s*$'

def handle_include_tag(line: str, base_dir: Path) -> str:
    """处理 <include> 标签，读取指定文件内容。"""
    match = re.match(REGEX_INCLUDE, line, re.IGNORECASE)
    if not match:
        return ""
    filename = match.group(1).strip()
    include_path = (base_dir / filename).resolve()
    
    if include_path.is_file() and include_path.is_relative_to(base_dir.resolve()):
        try:
            return include_path.read_text(encoding="utf-8")
        except:
            return f"<!-- Include Failed: {include_path.resolve()} -->"
    return f"<!-- Include Failed: {include_path.resolve()} -->"

def handle_markdown_tag(lines: list, start_index: int) -> tuple[str, int]:
    """处理 <markdown> 块，从当前行读取直到遇到 </markdown> 为止。"""
    content = []
    i = start_index + 1
    
    while i < len(lines):
        line = lines[i]
        # 检查是否匹配结束标签
        if re.match(REGEX_MARKDOWN_CLOSE, line, re.IGNORECASE):
            return '\n'.join(content), i + 1
        content.append(line)
        i += 1
    return '\n'.join(content), i

def parse_custom_tags(content: str, base_dir: Path) -> str:
    """解析文本内容，识别 <include> 和 <markdown> 标签并调用对应处理器。"""
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # 检查是否为 <include>
        if re.match(REGEX_INCLUDE, line, re.IGNORECASE):
            result.append(handle_include_tag(line, base_dir))
            i += 1
            continue
        
        # 检查是否为 <markdown>
        if re.match(REGEX_MARKDOWN_START, line, re.IGNORECASE):
            markdown_content, next_i = handle_markdown_tag(lines, i)
            result.append(markdown_content)
            i = next_i
            continue
        
        result.append(lines[i])
        i += 1

    return '\n'.join(result)

def is_valid_process_target(dir_path: Path) -> bool:
    """判断目标目录是否包含需要处理的模板文件"""
    return (dir_path / ".README").is_file() or (dir_path / "CONTENTS.md").is_file()

# def is_update_needed(readme_path: Path, new_content: str) -> bool:
#     """比较当前 README.md 内容与新生成的内容，判断是否需要写入更新。"""
#     if not readme_path.exists():
#         return True
#     try:
#         old_content = readme_path.read_text(encoding="utf-8")
#         return old_content.strip() != new_content.strip()
#     except:
#         return True

def process_directory(dir_path: Path, root: Path):
    """处理单个目录，读取模板并生成 README.md。"""
    global total_updates

    template_path = dir_path / ".README"
    contents_path = dir_path / "CONTENTS.md"
    readme_path = dir_path / "README.md"

    final_content = ""

    if template_path.exists():
        try:
            content = template_path.read_text(encoding="utf-8")
            final_content = parse_custom_tags(template_content, dir_path)
        except:            
            print(f"  [ERROR] 读取 {template_path} 失败: {e}")
            return
    elif contents_path.exists():
        try:
            final_content = contents_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [ERROR] 读取 {contents_path} 失败: {e}")
            return
    
    final_content = final_content.rstrip()

    try:
        if not readme_path.exists() or readme_path.read_text(encoding="utf-8").strip() != final_content.strip():
            readme_path.write_text(final_content, encoding="utf-8")
            total_updates += 1
            print(f"  更新: {dir_path.relative_to(root)}")
    except Exception as e:
        print(f"  [ERROR] 写入 {readme_path} 失败: {e}")


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
    files_input = os.getenv("FILES", "")
    
    print("开始生成 README 文件")

    if files_input:
        formatted_files = files_input.replace(',', '\n').replace('\\','')
        file_paths = [Path(p.strip()) for p in formatted_files.splitlines() if p.strip()]

        target_dirs = {(root / p).resolve().parent if not (root / p).resolve().is_dir() else (root / p).resolve() for p in file_paths}

        for dir_path in target_dirs:
            if dir_path.is_relative_to(root) and is_valid_process_target(dir_path):
                total_folders += 1
                process_directory(dir_path, root)

    set_github_env_var("TOTAL_FOLDERS", total_folders)
    set_github_env_var("TOTAL_UPDATES", total_updates)
    
    print(f"完成。共扫描目录: {total_folders}，修改文件: {total_updates}")