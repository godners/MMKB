#!/usr/bin/env python3
import os
from pathlib import Path

def should_skip(path: Path) -> bool:
    """跳过以 . 开头的任何文件夹或文件"""
    return any(part.startswith('.') for part in path.parts)

def get_level(relative_parts: tuple) -> int:
    """计算当前目录的 Markdown 标题级别（根目录为 1）"""
    return len([p for p in relative_parts if p]) + 1

def generate_readme_for_dir(dir_path: Path, repo: str, ref: str):
    if should_skip(dir_path):
        return
    
    readme_path = dir_path / "README.md"
    rel_path = dir_path.relative_to(Path.cwd())

    level = get_level(rel_path.parts)
    heading = "#" * level + " " + (dir_path.name if dir_path.name != "." else "项目根目录")

    lines = [heading, "", "此目录下的文件和子目录清单：", ""]

    items = []
    for item in sorted(dir_path.iterdir()):
        if should_skip(item):
            continue
        
        item_rel = item.relative_to(Path.cwd())
                
        if item.is_dir():
            # 文件夹 → 链接到该目录的 README.md（使用相对路径）
            folder_readme_link = f"{item_rel.as_posix()}/README.md"
            items.append(f"- [{item.name}]({folder_readme_link})")
        elif item.is_file():
            # 文件：排除 README.md，不显示扩展名
            if item.name.lower() == "readme.md":
                continue
            name_no_ext = item.stem
            file_link = f"{item_rel.as_posix()}"
            items.append(f"- [{name_no_ext}]({file_link})")
    
    if items:
        lines.extend(items)
    else:
        lines.append("（此目录为空）")
    
    lines.append("")
    lines.append("> **注意**：本文件由 GitHub Actions 每日自动生成，请勿手动修改。")

    content = "\n".join(lines)
    readme_path.write_text(content, encoding="utf-8")
    print(f"生成/更新: {readme_path.relative_to(Path.cwd())}")

if __name__ == "__main__":
    repo = os.getenv("GITHUB_REPOSITORY")
    ref = os.getenv("GITHUB_REF_NAME", "main")

    if not repo:
        print("错误：未检测到 GITHUB_REPOSITORY 环境变量")
        exit(1)
    
    root = Path(".")
    print(f"开始遍历仓库 {repo}（分支：{ref}）...")

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        current = Path(dirpath)
        if not should_skip(current):
            generate_readme_for_dir(current, repo, ref)
    
    print("所有 README.md 生成完成！")


