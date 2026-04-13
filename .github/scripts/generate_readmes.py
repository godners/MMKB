#!/usr/bin/env python3
import os
from pathlib import Path

ignore_filenames = [
    "readme.md", 
    "license.md",
    "code_of_conduct.md",
    "contributing.md",
    "security.md"
    ]

def should_skip(path: Path) -> bool:
    """跳过以 . 开头的任何文件夹或文件"""
    return any(part.startswith('.') for part in path.parts)

def get_level(relative_parts: tuple) -> int:
    """计算 Markdown 标题级别，根目录为 #"""
    return len([p for p in relative_parts if p]) + 1

def build_tree(dir_path: Path, root: Path, current_level: int) -> list:
    """递归构建内容：文件按名称排序，文件夹也按名称排序"""
    lines = []
    
    try:
        contents = list(dir_path.iterdir())
    except Exception:
        return lines

    # 分离文件和文件夹
    files = []
    folders = []
    for item in contents:
        if should_skip(item):
            continue
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            folders.append(item)

    # 1. 先处理文件（按名称排序）
    for item in sorted(files, key=lambda x: x.name.lower()):
        try:
            item_rel = item.resolve().relative_to(root.resolve())
        except ValueError:
            item_rel = Path(item.name)

        if item.name.lower() in ignore_filenames:
            continue

        name_no_ext = item.stem
        file_link = f"{item_rel.as_posix()}"
        lines.append(f"- [{name_no_ext}]({file_link})")

    # 2. 再处理文件夹（按名称排序）
    for item in sorted(folders, key=lambda x: x.name.lower()):
        try:
            item_rel = item.resolve().relative_to(root.resolve())
        except ValueError:
            item_rel = Path(item.name)

        # 文件夹：标题 + 链接
        folder_link = f"{item_rel.as_posix()}/README.md"
        heading = "#" * (current_level + 1) + f" [{item.name}]({folder_link})"
        lines.append("")
        lines.append(heading)
        lines.append("")

        # 递归展开子内容
        sub_lines = build_tree(item, root, current_level + 1)
        lines.extend(sub_lines)

    return lines


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

    lines = [heading, "", "此目录下的文件和子目录清单（自动生成，递归展开）：", ""]

    # 构建内容
    tree_lines = build_tree(dir_path, root, level)
    if tree_lines:
        lines.extend(tree_lines)
    else:
        lines.append("（此目录为空）")

    lines.append("")
    lines.append("> 注意：本文件由 GitHub Actions 每日自动生成，请勿手动修改。")

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