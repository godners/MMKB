#!/usr/bin/env python3
import os
import json
from pathlib import Path

# ====================== 配置 ======================
CONFIG_FILE = Path(".github/configs/generate-contents.json")

def load_config():
    if not CONFIG_FILE.exists():
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用空配置。")
        return {"ignore_objects": [], "name_mapping": [], "head_additional": []}
    
    with open(CONFIG_FILE, encoding="utf-8") as f:
        data = json.load(f)

    print(f"""配置文件加载成功，包含：
    ignore_objects 配置: {len(data.get("ignore_objects", []))} 条
    name_mapping 配置: {len(data.get("name_mapping", []))} 条""")
    
    return data

config = load_config()
ignore_objects = config.get("ignore_objects", [])
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}


def should_ignore(item: Path) -> bool:
    """根据配置判断是否忽略"""
    name = item.name
    item_type = "dir" if item.is_dir() else "file"

    for obj in ignore_objects:
        if obj.get("name") == name and obj.get("type") in (item_type, "both"):
            return True
    return False


def get_display_name(item: Path) -> str:
    """获取显示名称"""
    if item.is_file():
        if item.name in name_mapping:
            return name_mapping[item.name]
        elif item.stem in name_mapping:
            return name_mapping[item.stem]
        else:
            return item.stem
    return item.name


def get_rel_path_str(item: Path, root: Path) -> str:
    """返回标准化的相对路径"""
    try:
        rel = item.resolve().relative_to(root.resolve())
        return str(rel).replace("\\", "/")
    except ValueError:
        return item.name


def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    """递归构建目录树：先文件 → 再子目录"""
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines
    
    # 分离文件和文件夹
    files = [item for item in contents 
             if item.is_file() and not should_ignore(item)]    
    folders = [item for item in contents 
               if item.is_dir() and not should_ignore(item)]

    # 1. 先列出所有文件（这是缺失的核心部分）
    if files:
        for item in sorted(files, key=lambda x: x.name.lower()):
            display_name = get_display_name(item)
            rel_path = get_rel_path_str(item, root)
            lines.append(f"- [{display_name}]({rel_path})")
        lines.append("")   # 文件和子目录之间加空行

    # 2. 再列出子文件夹
    if folders:
        if files: # 如果前面有文件，则加空行分隔
            lines.append("")
            lines.append("---")
            lines.append("")

        for item in sorted(folders, key=lambda x: x.name.lower()):
            display_name = get_display_name(item)
            rel_dir = get_rel_path_str(item, root)
            folder_link = f"{rel_dir}/"CONTENTS.md"

            bracket = "[" * (current_level) + display_name + "]" * (current_level)

            # 使用当前层级 +1 的标题
            heading = "#" * (current_level + 1) + f" {bracket}({folder_link})"
            lines.append(heading)
            lines.append("")

            # 递归生成子目录内容
            sub_lines = build_tree(item, root, current_level + 1)
            lines.extend(sub_lines)

            if item != folders[-1]:
                lines.append("")
                lines.append("---")
                lines.append("")

    return lines

def generate_contents_for_dir(dir_path: Path, root: Path):
    """为单个目录生成 CONTENTS.md"""
    contents_path = dir_path / "CONTENTS.md"

    # 计算相对路径和目录名称
    try:
        rel_path = dir_path.resolve().relative_to(root.resolve())
        rel_str = str(rel_path).replace("\\", "/")
        dir_name = dir_path.name if dir_path.name else "项目根目录"
    except ValueError:
        rel_str = ""
        dir_name = "项目根目录"
    
    level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
    heading = "#" * level + " " + dir_name

    lines = [heading, "", "仓库文件与子目录结构（由 GitHub Actions 自动生成，请勿手动修改）", ""]

    tree_lines = build_tree(dir_path, root, level)
    lines.extend(tree_lines if tree_lines else ["（此目录为空）"])

    lines.append("")
    lines.append("> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。")

    new_content = "\n".join(lines)

    # 如果内容未变化则跳过写入
    if contents_path.exists():
        try:
            old_content = contents_path.read_text(encoding="utf-8")
            if old_content == new_content:
                return
        except Exception as e:
            pass
    
    contents_path.write_text(new_content, encoding="utf-8")
    print(f"生成/更新: {rel_str or '根目录'}")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    repo = os.getenv("GITHUB_REPOSITORY", "godners/MMKB")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    print(f"开始生成 CONTENTS.md，仓库：{repo}，分支：{ref}，根路径：{root}")

    # 遍历所有目录（含根目录）
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
        current = Path(dirpath)
        generate_contents_for_dir(current, root)
    
    print("所有 CONTENTS.md 生成完成！")