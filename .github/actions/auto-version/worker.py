#!/usr/bin/env python3
import json5, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

print("[PYTHON] Auto Version")

# CONFIG_FILE = Path(".github/configs/auto-version.json")
CONFIG_FILE = Path(os.getenv("ACTION_PATH")) / "configs.jsonc"

def load_config() -> dict:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json5.load(f)
        return {
            "commits_review": data.get("commits_review", 50),
            "ignore_objects": data.get("ignore_objects", [])
        }
    except Exception as e:
        print(f"读取忽略配置文件失败: {e}，将使用默认忽略列表")
        return {
            "commits_review": 50,
            "ignore_objects": [
                { "name": ".vscode", "type": "dir" },
                { "name": ".gitignore", "type": "file" },
                { "name": ".github", "type": "dir" },
                { "name": ".git", "type": "dir" },
                { "name": "VERSION.md", "type": "file"}
                ]
        }

def build_find_excludes(ignore_objects: list) -> list:
    excludes = []
    for obj in ignore_objects:
        name = obj["name"]
        path = f"./{name}"
        if obj["type"] == "dir":
            excludes.extend(["!", "-path", path])
            excludes.extend(["!", "-path", f"{path}/*"])
        else:
            excludes.extend(["!", "-path", path])
    return excludes

def get_commits_data(commits_data: str, max_count: int) -> list[tuple]:
    if not commits_data:
        return []
    
    commits = []
    seen = set()
    for item in commits_data.split(";"):
        if not item.strip():
            continue
        parts = item.split("|", 2)
        if len(parts) != 3:
            continue
        author, isodate, msg = parts
        if author not in seen:
            seen.add(author)
            commits.append((author, isodate, msg))
            if len(commits) >= max_count:
                break
    return commits

def size_hr(total_size: int) -> str:
    if total_size >= 1073741824:
        return f"{total_size / 1073741824:.2f} GiB"
    elif total_size >= 1048576:
        return f"{total_size / 1048576:.2f} MiB"
    elif total_size >= 1024:
        return f"{total_size / 1024:.2f} KiB"
    else:
        return f"{total_size} Byte"

def calc_repo_stats(ignore_objects: list) -> dict:
    ignore_objs = set()
    ignore_dirs = set()
    for obj in ignore_objects:
        name = obj.get("name")
        if not name:
            continue
        if obj.get("type") == "dir":
            ignore_objs.add(name)
            ignore_dirs.add(name)
        else:
            ignore_objs.add(name)
    
    folder_count = 0
    file_count = 0
    total_size = 0

    for root, dirs, files in os.walk(".", topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        rel_root = os.path.relpath(root, ".")
        if rel_root == ".":
            rel_root = ""
        
        current_dir = os.path.basename(root) if root != "." else ""
        if current_dir in ignore_dirs and rel_root != "":
            continue

        folder_count += 1

        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, ".")

            if f in ignore_objs or any(rel_path.startswith(d + "/") or rel_path == d for d in ignore_dirs):
                continue
            
            file_count += 1
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass

    return {
        "folder_count": folder_count,
        "file_count": file_count,
        "size_hr": size_hr(total_size)
    }
        
def write_version_md(tag: str, release_time: str, commits: list, stats: dict, commits_review: int):
    with open("VERSION.md", "w", encoding="utf-8") as f:
        f.write("## 项目版本信息\n\n")
        f.write("### 最后一次 Release\n\n")
        f.write(f"- **标签**：{tag}\n")
        f.write(f"- **时间**：{release_time}\n\n")
        f.write("### 最后一次 Commit\n\n")
        f.write(f"> 最多显示 {commits_review} 人的最后一次 Commit\n\n")
        for author, isodate, msg in commits:
            try:
                if isodate.endswith("Z"):
                    isodate = isodate[:-1] + "+00:00"
                dt = datetime.fromisoformat(isodate)
                dt_tz = dt + timedelta(hours=8)
                localtime = dt_tz.strftime("%Y-%m-%d %H:%M:%S +08:00")
                f.write(f"- [ {localtime} ] **{author}**：{msg}\n")
            except Exception:
                f.write(f"- [ **N/A** ] {author}：{msg}\n")
        f.write("\n### 仓库内容\n\n")
        f.write("> 已按配置规则排除）\n\n")
        f.write(f"- **总计文件夹数量**：{stats['folder_count']}\n")
        f.write(f"- **总计文件数量**：{stats['file_count']}\n")
        f.write(f"- **总计文件大小**：{stats['size_hr']}\n\n")
        f.write("---\n\n")
        utc_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S $z")
        f.write(f"> 最后生成时间：{utc_now}\n")

def main():
    config =load_config()
    commits_review = config["commits_review"]
    ignore_objects = config["ignore_objects"]

    tag = os.getenv("LAST_RELEASE_TAG", "暂无 Release")
    release_time = os.getenv("LAST_RELEASE_TIME", "N/A")
    commits_data = os.getenv("COMMITS_DATA", "")

    commits = get_commits_data(commits_data, commits_review)
    stats = calc_repo_stats(ignore_objects)

    write_version_md(tag, release_time, commits, stats, commits_review)

if __name__ == "__main__":
    main()
    