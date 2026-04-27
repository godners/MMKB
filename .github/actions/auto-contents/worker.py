#!/usr/bin/env python3
import os, json5
from pathlib import Path

print("[PYTHON] Auto Contents")
print(".github/actions/auto-contents/worker.py")


# 初始化配置与计数器
CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"

def load_config():
    """读取并返回 JSONC 配置文件内容。"""
    if not CONFIG_FILE.exists():
        return {"name_mapping": [], "auto_footer": ""}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json5.load(f)

config = load_config()
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}
AUTO_FOOTER = config.get("auto_footer", "")

# 获取白名单文件集合
raw_files = os.getenv("FILES", "")
# tj-actions/glob 默认以逗号分隔
valid_files = {path(f).resolve() for f in raw_files.split(",") if f.strip()}

def get_display_name(item: Path) -> str:
    """根据映射表获取文件的显示名称。"""
    return name_mapping.get(item.name) or name_mapping.get(item.stem) or item.stem

def get_rel_path_str(item: Path, root: Path) -> str:
    """获取文件相对于仓库根目录的路径字符串。"""
    try:
        return str(item.relative_to(root)).replace("\\", "/")
    except ValueError:
        return item.name

def add_special(lines, content):
    """在内容前后添加必要的空行，确保格式整洁。"""
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(content)
    lines.append("")

def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    """递归构建目录树结构的 Markdown 行列表。"""
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines

    # 筛选当前目录下在白名单中的文件
    files = sorted([i for i in contents if i.is_file() and i.resolve() in valid_files], key=lambda x: x.name.lower())
    # 筛选包含白名单文件的子目录
    folders = sorted([i for i in contents if i.is_dir()], key=lambda x: x.name.lower())

    for item in files:
        lines.append(f"- 文档：[{get_display_name(item)}]({get_rel_path_str(item, root)})")

    if folders:
        # 仅当子目录中存在我们需要的文件时，才将其加入目录树
        subtree = build_tree(item, root, current_level + 1)
        if subtree:
            if files:
                add_special(lines, "---")
            display_name = get_display_name(item)
            bracket_num = current_level - 1
            header_num = current_level + 1
            bracket = f"[{'【' * bracket_num}{display_name}{'】' * bracket_num}]"
            header = f"{'#' * header_num} {bracket}({get_rel_path_str(item, root)}/CONTENTS.md)"
            add_special(line, header)
            lines.extend(subtree)
    
    return lines

def generate_contents_for_dir(dir_path: Path, root: Path):
    """为指定目录生成或删除 CONTENTS.md 文件。"""
    contents_path = dir_path / "CONTENTS.md"

    # 计算层级
    try:
        rel_path = dir_path.relative_to(root)
        level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
    except ValueError:
        level = 1
    
    tree_lines = build_tree(dir_path, root, level)

    # 如果目录下没有任何需要的文件，则删除 CONTENTS.md
    if not tree_lines:
        if contents_path.exists():
            contents_path.unlink()
        return
    
    # 生成内容
    dir_name = dir_path.name if dir_path.name else "/"
    lines = [f"{'#' * (level + 1)} {dir_name}", ""] # , "仓库文件与子目录结构", ""]
    lines.extend(tree_lines)
    add_special(lines, "---")
    lines.append(AUTO_FOOTER)

    # 写入文件
    new_content = "\n".join(lines)
    if contents_path.exists() and contents_path.read_text(encoding="utf-8") == new_content:
        return
    
    contents_path.write_text(new_content, encoding="utf-8")
    print(f"更新: {dir_path.name or '/'}")

# def set_github_env_var(key, value):
#     env_file = os.getenv("GITHUB_ENV")
#     if env_file:
#         with open(env_file, "a", encoding="utf-8") as f:
#             f.write(f"{key}={value}\n")
#     else:
#         print(f"[DEBUG] 本地运行，环境变量 {key}={value} 未写入 GITHUB_ENV")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    for dirpath, _, _ in os.walk(root):
        if ".git" in dirpath: continue
        # dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
        generate_contents_for_dir(Path(dirpath), root)
    
    set_github_env_var("TOTAL_SCANNED", 0)
    set_github_env_var("TOTAL_MODIFIED", 0)
    print(f"扫描结束。共扫描目录: {0}，实际更新文件: {0}")