#!/usr/bin/env python3
import json5, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

print("[PYTHON] Auto Version")
print(".github/actions/auto-version/worker.py")

CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json5.load(f)
        return data.get("commits_review", 50), data.get("ignore_objects", [])
    except:
        return 50, [{"name": n, "type": "dir" if n in [".vscode", ".github", ".git"] else "file"} 
                    for n in [".vscode", ".gitignore", ".github", ".git", "VERSION.md"]]

def size_hr(n):
    for unit in ['Byte', 'KiB', 'MiB', 'GiB']:
        if n < 1024: return f"{n:.2f} {unit}" if unit != 'Byte' else f"{n} Byte"
        n /= 1024
    return f"{n:.2f} TiB"

def get_stats(ignore_objects):
    ignore_names = {obj["name"] for obj in ignore_objects}
    folder_count = file_count = total_size = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_names]
        folder_count += 1
        for f in files:
            if f not in ignore_names:
                file_count += 1
                try: total_size += os.path.getsize(os.path.join(root, f))
                except: pass
    return folder_count, file_count, size_hr(total_size)

def main():
    commits_review, ignore_objects = load_config()
    f_count, fi_count, size_str = get_stats(ignore_objects)
    
    # 解析 commits
    commits = []
    for item in os.getenv("COMMITS_DATA", "").split(";"):
        if "|" in item:
            author, date, msg = item.split("|", 2)
            dt = datetime.fromisoformat(date.replace("Z", "+00:00")) + timedelta(hours=8)
            commits.append(f"- [ {dt.strftime('%Y-%m-%d %H:%M:%S +08:00')} ] **{author}**：{msg}")
            if len(commits) >= commits_review: break

    # 生成内容
    content = f"""## 项目版本信息

### 最后一次 Release

- **标签**：{os.getenv("LAST_RELEASE_TAG", "暂无 Release")}
- **时间**：{os.getenv("LAST_RELEASE_TIME", "N/A")}

### 最后一次 Commit

> 最多显示最近 {commits_review} 人的 Commit

{"\n".join(commits)}

### 仓库内容

> 已按配置规则排除

- **总计文件夹数量**：{f_count}
- **总计文件数量**：{fi_count}
- **总计文件大小**：{size_str}

---

> 最后生成时间：{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 检查变更
    old_content = Path("VERSION.md").read_text(encoding="utf-8") if Path("VERSION.md").exists() else ""
    has_changes = content.strip() != old_content.strip()

    if has_changes:
        Path("VERSION.md").write_text(content, encoding="utf-8")

    # 输出环境变量
    if output_file := os.getenv("GITHUB_OUTPUT"):
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"has_changes={str(has_changes).lower()}\n")
            if has_changes:
                f.write(f"folder_count={f_count}\nfile_count={fi_count}\nsize_hr={size_str}\n")

if __name__ == "__main__":
    main()