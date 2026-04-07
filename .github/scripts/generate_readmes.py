#!/usr/bin/env python3
import os
from pathlib import Path

def should_skip(path: Path) -> bool:
    return any(part.startswith('.') for part in path.parts)

def get_level(relative_parts: tuple) -> int:
    return len([p for p in relative_parts if p]) + 1

def generate_readme_for_dir(dir_path: Path, root: Path):
    if should_skip(dir_path):
        return

    # ==================== 临时 Debug 输出 ====================
    print(f"DEBUG: 处理目录 -> {dir_path}")
    print(f"DEBUG:   absolute = {dir_path.absolute()}")
    print(f"DEBUG:   resolved = {dir_path.resolve()}")
    print(f"DEBUG:   root     = {root}")
    # =======================================================

    readme_path = dir_path / "README.md"

    # 关键修复：统一使用 resolved 路径计算 relative_to
    try:
        rel_path = dir_path.resolve().relative_to(root.resolve())
    except ValueError as e:
        print(f"DEBUG: relative_to 失败，使用备用方案: {e}")
        rel_path = dir_path.relative_to(root) if dir_path.is_absolute() else Path(".")

    # Markdown 标题
    dir_name = dir_path.name if dir_path.name not in (".", "") else "项目根目录"
    level = get_level(rel_path.parts)
    heading = "#" * level + " " + dir_name

    lines = [heading, "", "此目录下的文件和子目录清单（自动生成）：", ""]

    items = []
    for item in sorted(dir_path.iterdir()):
        if should_skip(item):
            continue

        try:
            item_rel = item.resolve().relative_to(root.resolve())
        except ValueError:
            item_rel = item.relative_to(root) if item.is_absolute() else Path(item.name)

        if item.is_dir():
            folder_readme_link = f"{item_rel.as_posix()}/README.md"
            items.append(f"- [{item.name}/]({folder_readme_link})")
        elif item.is_file():
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
    print(f"✅ 生成/更新: {rel_path}")


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
    