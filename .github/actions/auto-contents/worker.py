#!/usr/bin/env python3
import os, json5
from fnmatch import fnmatch
from pathlib import Path

print("[PYTHON] Auto Contents")
print(".github/actions/auto-contents/worker.py")


# ====================== 配置 ======================
CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"

patterns_raw = os.getenv("PATTERNS", "")
patterns = [p.strip() for p in patterns_raw.splitlines() if p.strip()]

# 全局计数器
total_scanned = 0
total_modified = 0

def load_config():
    if not CONFIG_FILE.exists():
        return {"name_mapping": [], "auto_footer": []}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        data = json5.load(f)
    return data

config = load_config()
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}
AUTO_FOOTER = config.get("auto_footer", "")

def is_match(item: Path, root: Path) -> bool:
    """检查文件路径是否匹配 patterns"""
    if not patterns:
        return True
            
    try:
        rel_path = str(item.relative_to(root))
        return any(fnmatch(rel_path, p) for p in patterns)
    except ValueError:
        return False


def get_display_name(item: Path) -> str:
    return name_mapping.get(item.name) or name_mapping.get(item.stem) or item.stem

def get_rel_path_str(item: Path, root: Path) -> str:
    try:
        return str(item.relative_to(root)).replace("\\", "/")
    except ValueError:
        return item.name

def add_special(lines, content):
    """通用格式化函数：确保内容前后各仅有1个空行"""
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(content)
    lines.append("")

def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines

    files = sorted([i for i in contents if i.is_file() and is_match(i, root)], key=lambda x: x.name.lower())
    folders = sorted([i for i in contents if i.is_dir()], key=lambda x: x.name.lower())

    for item in files:
        lines.append(f"- 文档：[{get_display_name(item)}]({get_rel_path_str(item, root)})")

    if folders:
        # if files:
        #     add_special(lines, "---")
        
        for item in folders:
            display_name = get_display_name(item)
            bracket = "[" + "【" * (current_level - 1) + display_name + "】" * (current_level - 1) + "]"
            header = f"{'#' * (current_level + 1)}目录：{bracket}({get_rel_path_str(item, root)}/CONTENTS.md)"
            
            add_special(lines, header)
            lines.extend(build_tree(item, root, current_level + 1))
    
    return lines

def generate_contents_for_dir(dir_path: Path, root: Path):
    global total_modified
    contents_path = dir_path / "CONTENTS.md"
    try:
        rel_path = dir_path.relative_to(root)
        level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
    except ValueError:
        level = 1

    dir_name = dir_path.name if dir_path.name else "项目根目录"
    
    tree_lines = build_tree(dir_path, root, level)

    if not tree_lines:
        if contents_path.exists():
            contents_path.unlink()
            total_modified += 1
        return
    
    lines = [f"{'#' * (level + 1)} {dir_name}", ""] # , "仓库文件与子目录结构", ""]
    lines.extend(tree_lines)

    add_special(lines, "---")
    lines.append(AUTO_FOOTER)

    while lines and lines[-1] == "":
        lines.pop()
    lines.append("")

    new_content = "\n".join(lines)
    if contents_path.exists() and contents_path.read_text(encoding="utf-8") == new_content:
        return
    
    contents_path.write_text(new_content, encoding="utf-8")
    total_modified += 1
    print(f"更新: {dir_path.name or '根目录'}")

def set_github_env_var(key, value):
    env_file = os.getenv("GITHUB_ENV")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"[DEBUG] 本地运行，环境变量 {key}={value} 未写入 GITHUB_ENV")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    for dirpath, dirnames, _ in os.walk(root):
        total_scanned += 1
        # dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
        generate_contents_for_dir(Path(dirpath), root)
    
    set_github_env_var("TOTAL_SCANNED", total_scanned)
    set_github_env_var("TOTAL_MODIFIED", total_modified)
    print(f"扫描结束。共扫描目录: {total_scanned}，实际更新文件: {total_modified}")