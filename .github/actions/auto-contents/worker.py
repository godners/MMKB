#!/usr/bin/env python3
import os, json5
from pathlib import Path

print("[PYTHON] Auto Contents")

# ====================== 配置 ======================
CONFIG_FILE = Path(os.getenv("ACTION_PATH")) / "configs.jsonc"
AUTO_FOOTER = "> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。"
def load_config():
    if not CONFIG_FILE.exists():
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用空配置。")
        return {"ignore_objects": [], "name_mapping": [], "head_additional": []}    
    with open(CONFIG_FILE, encoding="utf-8") as f:
        data = json5.load(f)
    print(f"""配置文件加载成功，包含：
    ignore_objects 配置: {len(data.get("ignore_objects", []))} 条
    name_mapping 配置: {len(data.get("name_mapping", []))} 条""")
    return data

config = load_config()
ignore_objects = config.get("ignore_objects", [])
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}


def should_ignore(item: Path) -> bool:
    """根据配置判断是否忽略"""
    # name = item.name
    item_type = "dir" if item.is_dir() else "file"
    return any(obj.get("name") == item.name 
        and obj.get("type") in (item_type, "both") for obj in ignore_objects)

    # for obj in ignore_objects:
    #     if obj.get("name") == name and obj.get("type") in (item_type, "both"):
    #         return True
    # return False


def get_display_name(item: Path) -> str:
    """获取显示名称"""
    return name_mapping.get(item.name) or name_mapping.get(item.stem) or item.stem
    # if item.is_file():
    #     if item.name in name_mapping:
    #         return name_mapping[item.name]
    #     elif item.stem in name_mapping:
    #         return name_mapping[item.stem]
    #     else:
    #         return item.stem
    # return item.name


def get_rel_path_str(item: Path, root: Path) -> str:
    """返回标准化的相对路径"""
    try:
        # return str(item.resolve().relative_to(root.resolve())).replace("\\", "/")
        # rel = item.resolve().relative_to(root.resolve())
        # return str(rel).replace("\\", "/")
    except ValueError:
        return item.name

def ensure_separator(lines: list):
    """确保末尾没有重复的分隔线"""
    if lines and lines[-1] != "---":
        lines.append(f"---")

def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    """递归构建目录树：先文件 → 再子目录"""
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines
    
    # 分离文件和文件夹
    files = sorted([i for i in contents if i.is_file() and not should_ignore(i)], key=lambda x: x.name.lower())    
    folders = sorted([i for i in contents if i.is_dir() and not should_ignore(i)], key=lambda x: x.name.lower())
    # files = [item for item in contents 
    #          if item.is_file() and not should_ignore(item)]    
    # folders = [item for item in contents 
    #            if item.is_dir() and not should_ignore(item)]

    # 添加文件
    if files:
        for item in files:
            lines.append(f"- [{get_display_name(item)}]({get_rel_path_str(item, root)})")
        # for item in sorted(files, key=lambda x: x.name.lower()):
        #     display_name = get_display_name(item)
        #     rel_path = get_rel_path_str(item, root)
        #     lines.append(f"- [{display_name}]({rel_path})")
        # lines.append("")   # 文件和子目录之间加空行

    # 添加子文件夹
    if folders:
        if files:
            ensure_separator(lines)
        
        for idx, item in enumerate(folders);
        # 如果不是第一个文件夹，添加分隔线
        if idx > 0:
            ensure_separator(lines);

        display_name = get-display_name(item)
        bracket = "【" * current_level + display_name + "】" * current_level
        lines.append(f"{'#' * (current_level + 1)} {bracket}({get_rel_path_str(item, root)}/CONTENTS.md)")
        lines.append(build_tree(item, root, current_level + 1))
    
    return lines


    # if folders:
    #     if files: # 如果前面有文件，则加空行分隔
    #         lines.append("")
    #         lines.append("---")
    #         lines.append("")

    #     for item in sorted(folders, key=lambda x: x.name.lower()):
    #         display_name = get_display_name(item)
    #         rel_dir = get_rel_path_str(item, root)
    #         folder_link = f"{rel_dir}/CONTENTS.md"

    #         bracket = "[" * (current_level) + display_name + "]" * (current_level)

    #         # 使用当前层级 +1 的标题
    #         heading = "#" * (current_level + 1) + f" {bracket}({folder_link})"
    #         lines.append(heading)
    #         lines.append("")

    #         # 递归生成子目录内容
    #         sub_lines = build_tree(item, root, current_level + 1)
    #         lines.extend(sub_lines)

    #         if item != folders[-1]:
    #             lines.append("")
    #             lines.append("---")
    #             lines.append("")

    # return lines

def generate_contents_for_dir(dir_path: Path, root: Path):
    """为单个目录生成 CONTENTS.md"""
    contents_path = dir_path / "CONTENTS.md"

    # 计算相对路径和目录名称
    try:
        rel_path = dir_path.resolve().relative_to(root.resolve())
        level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
        # rel_str = str(rel_path).replace("\\", "/")
        dir_name = dir_path.name if dir_path.name else "项目根目录"
    except ValueError:
        level, dir_name = 1, "项目根目录"
        # rel_str = ""
        # dir_name = "项目根目录"

    lines = [
        f"{'#' * level} {dir_name}", "", 
        "仓库文件与子目录内容", "", 
        "> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。", ""
        ]
    tree_lines = build_tree(dir_path, root, level)
    lines.extend(tree_lines if tree_lines else ["（此目录为空）"])

    lines.
    
    level = len([p for p in rel_path.parts if p]) + 1 if rel_path != Path(".") else 1
    heading = "#" * level + " " + dir_name

    lines = [
        heading, 
        "", 
        "仓库文件与子目录结构", 
        "",
        AUTO_FOOTER,
        ""
        ]

    tree_lines = build_tree(dir_path, root, level)
    lines.extend(tree_lines if tree_lines else ["（此目录为空）"])
    lines.extend(["", AUTO_FOOTER, "", "---", ""])

    # lines.append("")
    # lines.append("> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。")
    # lines.append("")
    # lines.append("---")
    # lines.append("")
    new_content = "\n".join(lines)

    # 如果内容未变化则跳过写入
    if contents_path.exists() and contents_path.read_text(encoding="utf-8") == new_contents:
        return
    # if contents_path.exists():
    #     try:
    #         old_content = contents_path.read_text(encoding="utf-8")
    #         if old_content == new_content:
    #             return
    #     except Exception as e:
    #         pass
    
    contents_path.write_text(new_content, encoding="utf-8")
    print(f"生成/更新: {dir_path.name or '根目录'}")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    repo = os.getenv("GITHUB_REPOSITORY", "godners/MMKB")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    print(f"开始生成 CONTENTS.md，仓库：{repo}，分支：{ref}，根路径：{root}")

    # 遍历所有目录（含根目录）
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
        # current = Path(dirpath)
        # generate_contents_for_dir(current, root)
        generate_contents_for_dir(Path(dirpath), root)
    
    print("所有 CONTENTS.md 生成完成！")