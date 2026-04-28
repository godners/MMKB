#!/usr/bin/env python3
import json5, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Tuple, List

print("[PYTHON] Auto Version")
print(".github/actions/auto-version/worker.py")

CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"

def load_config() -> int:
    """从 configs.jsonc 文件中读取配置。"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json5.load(f)
        return int(data.get("commits_review", 50))
    except:
        return 50

def size_hr(n: int) -> str:
    """将字节大小转换为易读的格式。"""
    for unit in ['Byte', 'KiB', 'MiB', 'GiB']:
        if n < 1024: 
            return f"{n:.2f} {unit}" if unit != 'Byte' else f"{n} Byte"
        n /= 1024
    return f"{n:.2f} TiB"

def get_file_stats(file_list: List[str]) -> Tuple[int, int, str]:
    """基于文件列表计算文件夹数量、文件数量及总大小。"""
    f_count = 0
    fi_count = 0
    total_size = 0

    if file_list:
        folders = set()
        for f_path in file_list:
            if os.path.isfile(f_path):
                fi_count += 1
                try:
                    total_size += os.path.getsize(f_path)
                    folders.add(os.path.dirname(f_path) or '.')
                except OSError:
                    pass
        f_count = len(folders)
    
    return f_count, fi_count, size_hr(total_size)

def parse_commits(commits_data: str, commits_review: int) -> List[str]:
    """解析 Git 提交记录数据。"""
    commits: List[str] = []
    if not commits_data:
        return commits
    
    for item in commits_data.split(";"):
        if "|" in item:
            try:
                author, date, msg = item.split("|", 2)
                dt = datetime.fromisoformat(date.replace("Z", "")) + timedelta(hours=8)
                commits.append(f"- [ {dt.strftime('%Y-%m-%d %H:%M:%S')}  **{author}**: {msg}")
                if len(commits) >= commits_review:
                    break
            except (ValueError, IndexError):
                continue
    return commits
                               

def main() -> None:
    """程序主入口，负责解析环境数据、生成文档内容并更新 VERSION.md。"""
    commits_review = load_config()

    # 获取环境变量 FILES，处理反斜杠并按逗号分割
    files_env = os.getenv("FILES", "")
    file_list = [f.replace('\\', '').strip() for f in files_env.split(',') if f.strip()]
    
    f_count, fi_count, size_str = get_file_stats(file_list)

    # 解析 commits
    commits_data = os.getenv("COMMITS_DATA", "")
    commits = parse_commits(commits_data, commits_review)

    # 生成内容
    content = f"""# MMKB

## 项目版本信息

### 最后一次 Release

- **标签**：{os.getenv("LAST_RELEASE_TAG", "暂无 Release")}
- **时间**：{os.getenv("LAST_RELEASE_TIME", "N/A")} (UTC)

### 最后一次 Commit

> 最多显示最近 {commits_review} 人的 Commit

{"\n".join(commits)}

### 仓库内容

> 已按配置规则排除

- **总计文件夹数量**：{f_count}
- **总计文件数量**：{fi_count}
- **总计文件大小**：{size_str}

---

> 最后生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)
"""

    # 检查变更
    version_file = Path("VERSION.md")
    old_content = version_file.read_text(encoding="utf-8") if Path("VERSION.md").exists() else ""
    has_changes = content.strip() != old_content.strip()

    if has_changes:
        version_file.write_text(content, encoding="utf-8")

    # 输出环境变量
    if output_file := os.getenv("GITHUB_OUTPUT"):
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"has_changes={str(has_changes).lower()}\n")
            if has_changes:
                f.write(f"folder_count={f_count}\nfile_count={fi_count}\nsize_hr={size_str}\n")

if __name__ == "__main__":
    main()