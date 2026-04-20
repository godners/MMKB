import os
import json
from pathlib import Path

# LICENSE_FILE = ".github/resources/license-footer.md"
CONFIG_FILE = ".github/configs/auto-license.json"
# CHECK_KEYWORD = "> License Added"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "license_footer": data.get("license_footer", ".github/resources/license-footer.md"),
                "check_keyword": data.get("check_keyword", "> License Added"),
                "ignore_objects": data.get("ignore_objects", [])
            }
    else:
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用默认值")
        return {
            "license_footer": ".github/resources/license-footer.md",
            "check_keyword": "> License Added",
            "ignore_objects": []
        }

def should_ignore(file_path, ignore_list):
    # 规范化路径（使用 / 作为分隔符）
    norm_path = file_path.replace('\\', '/')

    for item in ignore_list:
        name = item.get("name", "")
        item_type = item.get("type", "file")
        norm_name = name.replace('\\', '/')

        if item_type == "dir":
            # 忽略整个目录及其子路径
            if norm_path == norm_name or norm_path.startswith(norm_name + '/'):
                return True
        elif item_type == "file":
            if norm_path == norm_name or norm_path.endswith('/' + norm_name):
                return True
    return False

def has_license(content, check_keyword):
    return check_keyword in content

def main():
    config = load_config()

    LICENSE_FILE = config["license_footer"]
    CHECK_KEYWORD = config["check_keyword"]
    ignore_list = config["ignore_objects"]

    if not os.path.exists(LICENSE_FILE):
        print(f"错误：许可文件 {LICENSE_FILE} 不存在")
        return
    
    with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
        license_text = "\n\n" + f.read().strip() + "\n"

    # 获取所有 .md 文件
    root = Path(".")
    md_files = [str(p) for p in root.rglob("*.md") if p.is_file()]

    added_count = 0
    for md_file in md_files:
        if should_ignore(md_file, ignore_list):
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if has_license(content, CHECK_KEYWORD):
                continue
            
            # 添加声明
            if not content.endswith("\n"):
                content += "\n"
            content += license_text

            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"已添加声明: {md_file}")
            added_count += 1

        except Exception as e:
            print(f"处理失败 {md_file} : {e}")

    print(f"\n完成！本次共处理 {len(md_files)} 个 .md 文件，其中新增声明 {added_count} 个")

if __name__ == "__main__":
    main()