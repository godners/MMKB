#!/usr/bin/env python3
import os
import json5
import traceback
from pathlib import Path

print("[PYTHON] Auto License")
CONFIG_FILE = Path(os.getenv("ACTION_PATH")) / "configs.jsonc"

# 加载配置文件
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json5.load(f)
            try:
                config = {
                    "license_file": data.get("license_file"),
                    "check_keyword": data.get("check_keyword"),
                    "ignore_objects": data.get("ignore_objects")
                    }
                return config
            except:
                print(f"警告：读取配置文件 {CONFIG_FILE} 失败")
                return {}
    else:
        print(f"警告：配置文件 {CONFIG_FILE} 不存在")
        return {}

def should_ignore(file_path, ignore_list):
    norm_path = file_path.replace('\\', '/')
    for item in ignore_list:
        name = item.get("name", "")
        item_type = item.get("type", "file")
        norm_name = name.replace('\\', '/')
        if item_type == "dir":
            if norm_path == norm_name or norm_path.startswith(norm_name + '/'):
                return True
        elif item_type == "file":
            if norm_path == norm_name or norm_path.endswith('/' + norm_name):
                return True
    return False

def has_license(content, check_keyword):
    return check_keyword in content


# 新增：写入 GitHub Actions 环境文件的函数
def set_github_env_var(key, value):
    env_file = os.getenv("GITHUB_ENV")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"[DEBUG] 非 GitHub 环境: {key}={value}")

def apply_license_to_file(md_file, license_text, check_keyword):
    """
    处理单个文件的许可声明添加逻辑
    返回 True 表示修改成功，False 表示无需修改或处理失败
    """
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_license(content, check_keyword):
            return False
        
        # 添加声明
        if not content.endswith("\n"):
            content += "\n"
        content += license_text
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已添加声明: {md_file}")
        return True
    except Exception as e:
        print(f"处理失败 {md_file} : {e}")
        traceback.print_exc()
        return False

def run_license_update(config):
    """
    协调扫描与更新流程，返回统计结果
    """
    LICENSE_FILE = Path(os.getenv("ACTION_PATH")) / config["license_file"]
    CHECK_KEYWORD = config["check_keyword"]
    ignore_list = config["ignore_objects"]

    if not os.path.exists(LICENSE_FILE):
        print(f"错误：许可文件 {LICENSE_FILE} 不存在")
        return 0, 0
    
    with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
        license_text = "\n\n" + f.read().strip() + "\n"

    # 获取所有 .md 文件
    root = Path(".")
    md_files = [str(p) for p in root.rglob("*.md") if p.is_file()]
    
    total_scanned = 0
    added_count = 0
    
    for md_file in md_files:
        if should_ignore(md_file, ignore_list):
            continue
        
        total_scanned += 1
        
        # 调用单文件处理逻辑
        if apply_license_to_file(md_file, license_text, CHECK_KEYWORD):
            added_count += 1
            
    return total_scanned, added_count


def main():
    config = load_config()
    if not config:
        return

    # 执行更新流程
    total_scanned, total_modified = run_license_update(config)

    # 导出结果到环境变量
    set_github_env_var("TOTAL_SCANNED", total_scanned)
    set_github_env_var("TOTAL_MODIFIED", total_modified)

    print(f"\n完成！本次共扫描 {total_scanned} 个有效 .md 文件，其中新增声明 {total_modified} 个")

if __name__ == "__main__":
    main()