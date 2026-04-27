#!/usr/bin/env python3
import os, re
from pathlib import Path

print("[PYTHON] Auto Readmes")
print(".github/actions/auto-readmes/worker.py")

# 全局计数器
total_scanned = 0
total_modified = 0

REGEX_INCLUDE = r'^\s*<include>\s*.+?\s*</include>\s*$'
REGEX_MARKDOWN = r'^\s*</markdown>\s*$'

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
    """处理 <markdown> 标签及其包裹的内容。"""
    i = start_index + 1
    markdown_content = []
    while i < len(lines):
        inner_line = lines[i].rstrip('\n')
        if re.match(REGEX_MARKDOWN, inner_line, re.IGNORECASE):
            return (''.join(markdown_content).strip('\n') + '\n', i + 1)
        markdown_content.append(lines[i])
        i += 1
    return ("", i)

def parse_custom_tags(content: str, base_dir: Path) -> str:
    """解析文本内容中的 <include> 和 <markdown> 标签。"""
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip('\n')

        # 检查是否为 <include>
        if re.match(REGEX_INCLUDE, line, re.IGNORECASE):
            result.append(handle_include_tag(line, base_dir))
            i += 1
            continue
        
        # 检查是否为 <markdown>
        if re.match(REGEX_MARKDOWN, line, re.IGNORECASE):
            content_str, next_i = handle_markdown_tag(lines, i)
            result.append(content_str)
            i = next_i
            continue
        
        result.append(lines[i])
        i += 1

    return ''.join(result)

def is_valid_process_target(dir_path: Path) -> bool:
    """判断目标目录是否包含需要处理的模板文件"""
    return (dir_path / ".README").is_file() or (dir_path / "CONTENTS.md").is_file()

def is_update_needed(readme_path: Path, new_content: str) -> bool:
    """比较当前 README.md 内容与新生成的内容，判断是否需要写入更新。"""
    if not readme_path.exists():
        return True
    try:
        old_content = readme_path.read_text(encoding="utf-8")
        return old_content.strip() != new_content.strip()
    except:
        return True

def process_directory(dir_path: Path, root: Path):
    """处理单个目录，读取模板并生成 README.md。"""
    global total_modified

    template_path = dir_path / ".README"
    contents_path = dir_path / "CONTENTS.md"
    readme_path = dir_path / "README.md"

    final_content = ""

    if template_path.exists():
        try:
            with open(template_path, encoding="utf-8") as f:
                template_content = f.read()
            final_content = parse_custom_tags(template_content, dir_path)
        except:
            return
    elif contents_path.exists():
        try:
            final_content = f"# {dir_path.name}\n\n"
            with open(contents_path, encoding="utf-8") as f:
                final_content += f.read()
        except:
            return
    
    final_content = final_content.rstrip()

    if is_update_needed(readme_path, final_content):
        readme_path.write_text(final_content, encoding="utf-8")
        total_modified += 1
        print(f"更新：{dir_path.relative_to(root) or '/'}")

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
        file_paths = [Path(p.strip()) for p in files_input.splitlines() if p.strip()]

        target_dirs = set()
        for p in file_paths:
            full_path = (root / p).resolve()
            if full_path.exists():
                target = full_path if full_path.is_dir() else full_path.parent
                if not target.name.startswith('.'):
                    target_dirs.add(target)
        
        for dir_path in target_dirs:
            if dir_path.is_relative_to(root) and is_valid_process_target(dir_path):
                total_scanned += 1
                process_directory(dir_path, root)
    else:
        print("未接收到任何文件变更，跳过执行。")

    set_github_env_var("TOTAL_SCANNED", total_scanned)
    set_github_env_var("TOTAL_MODIFIED", total_modified)
    
    print(f"完成。共扫描目录: {total_scanned}，修改文件: {total_modified}")