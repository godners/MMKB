#!/usr/bin/env python3
import os, json5, traceback
from pathlib import Path

print("[PYTHON] Auto License")
print(".github/actions/auto-license/worker.py")

CONFIG_FILE = Path(os.getenv("ACTION_PATH")) / "configs.jsonc"

# 加载配置文件
def load_config():
    """读取并解析 JSON5 格式的配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f:
            data = json5.load(f)
            return {
                "license_file": data.get("license_file"),
                "check_keyword": data.get("check_keyword")
            }
    print(f"警告：配置文件 {CONFIG_FILE} 不存在")
    return {}

def set_github_env_var(key, value):
    """将指定键值对写入 GitHub Actions 环境变量文件"""
    env_file = os.getenv("GITHUB_ENV")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")

def has_license(content, check_keyword):
    """检查文本内容中是否包含指定的许可关键字"""
    return check_keyword in content

def apply_license_to_file(md_file, license_text, check_keyword):
    """读取文件并根据条件追加许可声明，返回是否成功修改"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()        
        if has_license(content, check_keyword):
            return False
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"{content.rstrip()}{license_text}")
        print(f"已添加声明: {md_file}")
        return True
    except Exception as e:
        print(f"处理失败 {md_file} : {e}")
        traceback.print_exc()
        return False

def run_license_update(config):
    """执行文件列表扫描与许可声明的更新逻辑"""
    license_path = Path(os.getenv("ACTION_PATH")) / config["license_file"]
    if not license_path.exists():
        print(f"错误：许可文件 {license_path} 不存在")
        return 0,0
    
    with open(license_path, 'r', encoding='utf-8') as f:
        license_text = f"\n\n{f.read().strip()}\n"

#    root = Path(".")
    raw_files = os.getenv("FILES", "").replace('\\', '')
    md_files = [f.strip() for f in raw_files.split(',') if f.strip()]
    #md_files = [str(p) for p in root.rglob("*.md") if p.is_file()]
    
    total_folders = 0
    total_updates = 0
    
    for md_file in md_files:
        if os.path.exists(md_file):
            total_folders += 1
            if apply_license_to_file(md_file, license_text, config["check_keyword"]):
                total_updates += 1
            
    return total_folders, total_updates


def main():
    """程序入口函数，控制执行流程"""
    config = load_config()
    if not config:
        return

    total_folders, total_updates = run_license_update(config)

    set_github_env_var("TOTAL_FOLDERS", total_folders)
    set_github_env_var("TOTAL_UPDATES", total_updates)

    print(f"\n完成！本次共扫描 {total_folders} 个有效 .md 文件，其中新增声明 {total_updates} 个")

if __name__ == "__main__":
    main()