#!/usr/bin/env python3
import os
from pathlib import Path

def should_skip(path: Path) -> bool:
    """跳过以 . 开头的任何文件夹或文件"""
    return any(part.startswith('.') for part in path.parts)

def get_level(relative_parts: tuple) -> int:
    """计算 Markdown 标题级别，根目录为 #"""
    return len([p for p in relative_parts if p]) + 1

def build_tree(dir_path: Path, root: Path, indent: str = "") -> list:
    """递归构建目录树列表（返回 Markdown 行列表）"""
    items = []
    try:
        contents = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return items

    for item in contents:
        if should_skip(item):
            continue

        try:
            item_rel = item.resolve().relative_to(root.resolve())
        except ValueError:
            item_rel = Path(item.name)

        if item.is_dir():
            # 文件夹：不带 /，并递归展开
            folder_name = item.name
            folder_link = f"{item_rel.as_posix()}/README.md"
            items.append(f"{indent}- [{folder_name}]({folder_link})")
            # 递归展开子内容（增加缩进）
            items.extend(build_tree(item, root, indent + "  "))

        elif item.is_file():
            # 文件：排除 README.md 和 LICENSE
            if item.name.lower() in ["readme.md", "license", "license.txt", "license.md"]:
                continue
            name_no_ext = item.stem
            file_link = f"{item_rel.as_posix()}"
            items.append(f"{indent}- [{name_no_ext}]({file_link})")

    return items

def generate_readme_for_dir(dir_path: Path, root: Path):
    if should_skip(dir_path):
        return

    readme_path = dir_path / "README.md"

    try:
        rel_path = dir_path.resolve().relative_to(root.resolve())
    except ValueError:
        rel_path = Path(".")

    dir_name = dir_path.name if dir_path.name not in (".", "") else "项目根目录"
    level = get_level(rel_path.parts)
    heading = "#" * level + " " + dir_name

    lines = [heading, "", "此目录下的文件和子目录结构（自动生成，递归展开）：", ""]

    # 递归构建树
    tree_lines = build_tree(dir_path, root)
    if tree_lines:
        lines.extend(tree_lines)
    else:
        lines.append("（此目录为空）")

    lines.append("")
    lines.append("> **注意**：本文件由 GitHub Actions 每日自动生成，请勿手动修改。")

    content = "\n".join(lines)
    readme_path.write_text(content, encoding="utf-8")
    print(f"生成/更新: {rel_path}")


if __name__ == "__main__":
    repo = os.getenv("GITHUB_REPOSITORY", "unknown")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    root = Path.cwd().resolve()
    print(f"开始遍历仓库 {repo}（分支：{ref}），根目录：{root}")

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        current = Path(dirpath)
        if not should_skip(current):
            generate_readme_for_dir(current, root)

    print("所有 README.md 生成完成！")