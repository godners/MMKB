#!/usr/bin/env python3
import os
import json
from pathlib import Path

# ====================== 配置 ======================
CONFIG_FILE = Path(".github/configs/generate_readmes.json")

# 默认忽略项（可被 json 中的 ignore_objects 覆盖或补充）
DEFAULT_IGNORE = {
    "file": ["README.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md"],
    "dir": [".git", ".github", ".vscode", "__pycache__"]
}

def load_config():
    if not CONFIG_FILE.exists():
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用默认忽略规则。")
        return {"ignore_objects": [], "name_mapping": [], "head_additional": []}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        data = json.load(f)
    print(f"""配置文件加载成功，包含：
   ignore_objects 配置: {len(data.get("ignore_objects", []))} 条
   name_mapping 配置: {len(data.get("name_mapping", []))} 条
   head_additional 配置 {len(data.get("head_additional", []))} 条""")

    return data
    
config = load_config()
ignore_objects = config.get("ignore_objects", [])
name_mapping = {item["name"]: item["new_name"] for item in config.get("name_mapping", [])}
# head_additional = {item["name"]: item["header"] for item in config.get("head_additional", [])}


def should_ignore(item: Path) -> bool:
    """根据 generate_readmes.json 中的 ignore_objects 判断是否忽略"""
    name = item.name
    item_type = "dir" if item.is_dir() else "file"

    for obj in ignore_objects:
        if obj.get("name") == name and obj.get("type") in (item_type, "both"):            
            return True
    return False


def get_display_name(item: Path) -> str:
    """获取显示名称：优先使用 name_mapping，否则去掉扩展名"""
    if item.is_file():
        # 优先精确匹配带扩展名的文件名
        if item.name in name_mapping:
            return name_mapping[item.name]
        # 备选：只匹配 stem（不带扩展名）
        elif item.stem in name_mapping:
            return name_mapping[item.stem]
        else:
            return item.stem
    # 文件夹直接用文件夹名
    return item.name


def get_rel_path_str(item: Path, root: Path) -> str:
    """返回标准化的相对路径（使用 / 分隔符）"""
    try:
        rel = item.resolve().relative_to(root.resolve())
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(item.name) 


def read_header_content(dir_path: Path, root: Path) -> str:
    """读取 .README_HEADER 并返回要插入的内容"""
    header_file = dir_path / ".README_HEADER"
    if not header_file.exists() or not header_file.is_file():
        return ""
    
    try:
        with open(header_file, encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return ""
        
        # 检查是否为单行 <readme_header>xxx</readme_header> 格式
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        if len(lines) == 1:
            line = lines[0]
            if line.startswith("<readme_header>") and line.endswith("</readme_header>"):
                target_name = line[len("<readme_header>"): -len("</readme_header>")].strip()
                if target_name:
                    target_path = dir_path / target_name
                    if target_path.exists() and target_path.is_file():
                        with open(target_path, encoding="utf-8") as tf:
                            return tf.read().strip()
                    else:
                        print(f"警告：.README_HEADER 指向的文件不存在: {target_path}")
                        return ""
        # 否则直接返回 .README_HEADER 自身的内容
        return content
    
    except Exception as e:
        print(f"读取 .README_HEADER 时出错: {dir_path} -> {e}")
        return ""


def build_tree(dir_path: Path, root: Path, current_level: int) -> list[str]:
    """递归构建目录树：先文件 → 再子目录（增加分隔）"""
    lines = []
    try:
        contents = list(dir_path.iterdir())
    except Exception as e:
        return lines
    
    # 分离文件和文件夹
    files = [item for item in contents 
             if item.is_file() 
             and not item.name.startswith('.') 
             and not should_ignore(item)]

    folders = [item for item in contents 
               if item.is_dir() 
               and not item.name.startswith('.') 
               and not should_ignore(item)]

    # 1. 先列出所有文件
    for item in sorted(files, key=lambda x: x.name.lower()):
        display_name = get_display_name(item)
        rel_path = get_rel_path_str(item, root)
        lines.append(f"- [{display_name}]({rel_path})")

    # 2. 再列出子文件夹（增加清晰分隔）
    if folders:
        if files:  # 如果前面有文件，则加空行分隔
            lines.append("")
        lines.append("**子目录：**")
        lines.append("")

        for item in sorted(folders, key=lambda x: x.name.lower()):
            display_name = get_display_name(item)
            folder_link = (get_rel_path_str(item, root) + "/README.md")
            heading = "#" * (current_level + 1) + f" [{display_name}]({folder_link})"
            lines.append(heading)
            lines.append("")

            # 递归
            sub_lines = build_tree(item, root, current_level + 1)
            lines.extend(sub_lines)

    return lines


def generate_readme_for_dir(dir_path: Path, root: Path):
    """为单个目录生成 README.md"""
    if dir_path.name.startswith('.'):
        return
    
    readme_path = dir_path / "README.md"

    # 计算相对路径和目录名称
    try:
        rel_path = dir_path.resolve().relative_to(root.resolve())
        rel_str = str(rel_path).replace("\\", "/")
    except ValueError:
        rel_str = "."

    dir_name = dir_path.name if dir_path.name not in (".", "") else "项目根目录"
    level = len([p for p in rel_path.parts if p]) + 1
    heading = "#" * level + " " + dir_name

    lines = [heading, "", "仓库文件与子目录结构（由 GitHub Actions 自动生成，请勿手动修改）", ""]

    tree_lines = build_tree(dir_path, root, level)
    lines.extend(tree_lines if tree_lines else ["（此目录为空）"])

    # 处理 .README_HEADER 
    extra_content = read_header_content(dir_path, root)
    if extra_content:
        lines.append("")
        lines.append(extra_content)

    # # 添加 head_additional 内容
    # header_file = head_additional.get(rel_str) or head_additional.get(dir_path.name)
  
    # if header_file:
    #     header_path = root / header_file
    #     if header_path.exists() and header_path.is_file():
    #         try:
    #             with open(header_path, encoding="utf-8") as f:
    #                 extra_content = f.read().strip()
    #             if extra_content:
    #                 lines.append("")
    #                 lines.append(extra_content)
    #         except Exception as e:
    #             pass

    lines.append("")
    lines.append("> 注意：本文件由 GitHub Actions 自动生成，请勿手动修改。")

    # content = "\n".join(lines)
    # readme_path.write_text(content, encoding="utf-8")
    # print(f"生成/更新: {rel_path or '根目录'}")
    new_content = "\n".join(lines)
    if readme_path.exists():
        try:
            with readme_path.read_text(encoding="utf-8") as f:
                old_content = f.read()
            if old_content == new_content:
                print(f"内容未变化，跳过写入: {rel_str or '根目录'}")
                return            
        except Exception as e:
            pass
    readme_path.write_text(new_content, encoding="utf-8")
    print(f"生成/更新: {rel_str or '根目录'}")

if __name__ == "__main__":
    root = Path.cwd().resolve()
    repo = os.getenv("GITHUB_REPOSITORY", "godners/MMKB")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    print(f"开始生成 READMEs，仓库：{repo}，分支：{ref}，根路径：{root}")

    # 遍历所有目录（含根目录）
    for dirpath, dirnames, _ in os.walk(root):
        # 排除以 . 开头的目录
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        current = Path(dirpath)
        if not current.name.startswith('.'):
            generate_readme_for_dir(current, root)
    
    print("所有 README.md 生成完成！")