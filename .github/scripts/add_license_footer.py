import os
import json
import glob

LICENSE_FILE = ".github/resources/add_license_footer.md"
EXCLUDE_FILE = ".github/configs/add_license_footer.json"

def load_ignore_list():
    if os.path.exists(EXCLUDE_FILE):
        with open(EXCLUDE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("ignore_objects", [])
    return []

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

def has_license(content):
    return "> License Added" in content or "CC BY-NC-SA" in content

def main():
    ignore_list = load_ignore_list()
    if not os.path.exists(LICENSE_FILE):
        print(f"错误：许可文件 {LICENSE_FILE} 不存在")
        return
    
    with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
        license_text = "\n\n" + f.read().strip() + "\n"

    # 获取所有 .md 文件
    md_files = glob.glob("**/*.md", recursive=True)

    added_count = 0
    for md_file in md_files:
        if should_ignore(md_file, ignore_list):
            print(f"已忽略: {md_file}")
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if has_license(content):
                print(f"已有声明: {md_file}")
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