#!/usr/bin/env python3
import os, json5
from pathlib import Path

print("[PYTHON] Auto Contents")

# ====================== 配置 ======================
CONFIG_FILE = Path(os.getenv("ACTION_PATH", ".")) / "configs.jsonc"
AUTO_FOOTER = "> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。"

def load_config():
    if not CONFIG_FILE.exists():
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用空配置。")
        return {"ignore_objects": [], "name_mapping": [], "head_additional": []}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        data = json5.load(f)
    print(f"配置文件加载成功，ignore={len(data.get('ignore_objects', []))}，name_mapping={len(data.get('name_mapping', []))}")
    return data

config = load_config()
ignore_objects = config.get("ignore_objects", [])
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}

def should_ignore(item: Path) -> bool:
    item_type = "dir" if item.is_dir() else "file"
    return any(obj.get("name") == item.name and obj.get("type") in (item_type, "both") for obj in ignore_objects)

def get_display_name(item: Path) -> str:
    return name_mapping.get(item.name) or name_mapping.get(item.stem) or item.stem

def get_rel_path_str(item: Path, root: Path) -> str:
    try:
        return str(item.relative_to(root)).replace("\\", "/")
    except ValueError:
        return item.name

def ensure_separator(lines: list):
    if lines and lines[-1] != "---":
        lines.append("---")

def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines

    files = sorted([i for i in contents if i.is_file() and not should_ignore(i)], key=lambda x: x.name.lower())
    folders = sorted([i for i in contents if i.is_dir() and not should_ignore(i)], key=lambda x: x.name.lower())

    if files:
        for item in files:
            lines.append(f"- [{get_display_name(item)}]({get_rel_path_str(item, root)})")

    if folders:
        if files:
            ensure_separator(lines)
        
        for idx, item in enumerate(folders):
            if idx > 0:
                ensure_separator(lines)
            
            display_name = get_display_name(item)
            # 根据需求使用方括号装饰
            bracket = "[" * current_level + display_name + "]" * current_level
            lines.append(f"{'#' * (current_level + 1)} {bracket}({get_rel_path_str(item, root)}/CONTENTS.md)")
            lines.extend(build_tree(item, root, current_level + 1))
    
    return lines

def generate_contents_for_dir(dir_path: Path, root: Path):
    contents_path = dir_path / "CONTENTS.md"

    try:
        rel_path = dir_path.relative_to(root)
        level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
    except ValueError:
        level = 1

    dir_name = dir_path.name if dir_path.name else "项目根目录"
    
    lines = [
        f"{'#' * level} {dir_name}", "",
        "仓库文件与子目录结构", "",
        AUTO_FOOTER, ""
    ]

    tree_lines = build_tree(dir_path, root, level)
    lines.extend(tree_lines if tree_lines else ["（此目录为空）"])
    lines.extend(["", AUTO_FOOTER, "", "---", ""])

    new_content = "\n".join(lines)

    if contents_path.exists() and contents_path.read_text(encoding="utf-8") == new_content:
        return
    
    contents_path.write_text(new_content, encoding="utf-8")
    print(f"生成/更新: {dir_path.name or '根目录'}")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    print(f"开始生成 CONTENTS.md，根路径：{root}")

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
        generate_contents_for_dir(Path(dirpath), root)
    
    print("所有 CONTENTS.md 生成完成！")