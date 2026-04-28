#!/usr/bin/env python3
import os, json
from pathlib import Path
from typing import Set, Optional

print("[PYTHON] Auto Readmes")
print(".github/actions/auto-readmes/worker.py")

def get_unique_directories(files_str: str) -> Set[Path]:
    """解析环境变量中的文件列表，返回去重后的目录路径集合"""
    if not files_str: return set()

    raw_files = [f.replace('\\','').strip() for f in files_str.split(',') if f.strip()]
    return {Path(f).parent for f in raw_files}

def parse_readme_template(template_path: Path, dir_path: Path) -> str:
    """解析 .README 模板文件并返回生成的文本内容"""
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

def get_existing_content(readme_path: Path) -> Optional[str]:
    """如果文件存在，读取其内容，否则返回 None"""
    if readme_path.exists():
        return readme_path.read_text(encoding='utf-8')
    return None

def process_directory(dir_path: Path) -> bool:
    """处理单个目录，返回是否进行了更新（布尔值）"""
    readme_path = dir_path / "README.md"
    template_path = dir_path / ".README"
    contents_path = dir_path / "CONTENTS.md"

    if template_path.exists():
        try:
            new_content = parse_readme_template(template_path, dir_path)
#            readme_path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error processing {template_path.resolve()}: {e}")
            return False
    elif contents_path.exists():
        new_content = contents_path.read_text(encoding='utf-8')
    else: 
        return False

    old_content: Optional[str] = get_existing_content(readme_path)
    if new_content != old_content:
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"更新 {readme_path}")
        return True

    return False

def update_github_env(folders: int, updates: int) -> None:
    """将统计结果写入 GITHUB_ENV"""
    env_file = os.getenv('GITHUB_ENV')
    if env_file:
        with open (env_file, 'a', encoding='utf-8') as f:
            f.write(f"TOTAL_FOLDERS={folders}\n")
            f.write(f"TOTAL_UPDATES={updates}\n")

def main() -> None:
    files_str = os.environ.get('FILES', '')
    unique_dirs = get_unique_directories(files_str)
    total_folders = len(unique_dirs)
    total_updates = 0
    for dir_path in unique_dirs:
        if process_directory(dir_path):
            total_updates += 1

    update_github_env(total_folders, total_updates)

if __name__ == "__main__":
    main()
    