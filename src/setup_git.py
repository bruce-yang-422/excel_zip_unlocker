#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: setup_git.py
用途: Git 初始化設定腳本
說明: 自動設定 Git 倉庫和相關配置
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description=""):
    """執行命令並處理錯誤"""
    try:
        print(f"執行: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"輸出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"錯誤: {e}")
        if e.stderr:
            print(f"錯誤訊息: {e.stderr.strip()}")
        return False


def check_git_installed():
    """檢查 Git 是否已安裝"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Git 已安裝: {result.stdout.strip()}")
            return True
        else:
            print("✗ Git 未安裝")
            return False
    except FileNotFoundError:
        print("✗ Git 未安裝或不在 PATH 中")
        return False


def init_git_repo():
    """初始化 Git 倉庫"""
    if os.path.exists('.git'):
        print("✓ Git 倉庫已存在")
        return True
    
    if not run_command('git init', "初始化 Git 倉庫"):
        return False
    
    print("✓ Git 倉庫初始化完成")
    return True


def setup_git_config():
    """設定 Git 配置"""
    print("\n設定 Git 配置...")
    
    # 設定使用者名稱和郵箱 (如果未設定)
    try:
        subprocess.run(['git', 'config', 'user.name'], check=True, capture_output=True)
        print("✓ Git 使用者名稱已設定")
    except subprocess.CalledProcessError:
        print("請設定 Git 使用者名稱:")
        name = input("使用者名稱: ").strip()
        if name:
            run_command(f'git config user.name "{name}"', "設定使用者名稱")
    
    try:
        subprocess.run(['git', 'config', 'user.email'], check=True, capture_output=True)
        print("✓ Git 使用者郵箱已設定")
    except subprocess.CalledProcessError:
        print("請設定 Git 使用者郵箱:")
        email = input("使用者郵箱: ").strip()
        if email:
            run_command(f'git config user.email "{email}"', "設定使用者郵箱")
    
    # 設定其他有用的配置
    run_command('git config core.autocrlf true', "設定行尾符號處理")
    run_command('git config core.safecrlf true', "設定行尾符號安全檢查")
    run_command('git config pull.rebase false', "設定拉取策略")
    
    return True


def create_gitkeep_files():
    """建立 .gitkeep 檔案保持空資料夾"""
    directories = ['input', 'output', 'logs', 'report', 'tools']
    
    for dir_name in directories:
        gitkeep_path = Path(dir_name) / '.gitkeep'
        if not gitkeep_path.exists():
            gitkeep_path.write_text('# 保持此資料夾在 Git 中\n', encoding='utf-8')
            print(f"✓ 已建立 {gitkeep_path}")
    
    return True


def create_readme_files():
    """建立資料夾說明檔案"""
    readme_content = """# 資料夾說明

此資料夾用於存放 {folder_name} 相關檔案。

## 注意事項

- 請勿將敏感檔案提交到版本控制
- 定期清理不需要的檔案
- 遵守公司安全政策

## 檔案類型

{folder_description}
"""
    
    folder_descriptions = {
        'input': '待處理的 Excel 和壓縮檔案',
        'output': '處理完成後的解密檔案',
        'logs': '程式執行日誌檔案',
        'report': '處理結果報表檔案',
        'tools': '外部工具執行檔 (如 unrar.exe)'
    }
    
    for folder_name, description in folder_descriptions.items():
        readme_path = Path(folder_name) / 'README.md'
        if not readme_path.exists():
            content = readme_content.format(
                folder_name=folder_name,
                folder_description=description
            )
            readme_path.write_text(content, encoding='utf-8')
            print(f"✓ 已建立 {readme_path}")
    
    return True


def setup_git_hooks():
    """設定 Git 鉤子"""
    hooks_dir = Path('.git/hooks')
    if not hooks_dir.exists():
        return True
    
    # 建立 pre-commit 鉤子
    pre_commit_hook = """#!/bin/sh
# Pre-commit 鉤子
# 檢查敏感檔案

echo "檢查敏感檔案..."

# 檢查是否包含密碼檔案
if git diff --cached --name-only | grep -E "\\.(passwords|keys|env)$"; then
    echo "錯誤: 檢測到敏感檔案，請移除後再提交"
    exit 1
fi

# 檢查是否包含 Excel 或壓縮檔案
if git diff --cached --name-only | grep -E "\\.(xlsx|xls|zip|rar)$"; then
    echo "錯誤: 檢測到 Excel 或壓縮檔案，請移除後再提交"
    exit 1
fi

echo "檢查通過"
"""
    
    pre_commit_path = hooks_dir / 'pre-commit'
    pre_commit_path.write_text(pre_commit_hook, encoding='utf-8')
    pre_commit_path.chmod(0o755)
    print("✓ 已設定 pre-commit 鉤子")
    
    return True


def initial_commit():
    """進行初始提交"""
    print("\n準備進行初始提交...")
    
    # 添加所有檔案
    if not run_command('git add .', "添加檔案到暫存區"):
        return False
    
    # 檢查暫存區狀態
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not result.stdout.strip():
            print("✓ 沒有檔案需要提交")
            return True
    except subprocess.CalledProcessError:
        pass
    
    # 進行提交
    commit_message = """初始提交

- 建立 Excel ZIP Unlocker 專案
- 設定 Git 忽略規則
- 建立專案結構和文件
- 設定安全配置"""
    
    if not run_command(f'git commit -m "{commit_message}"', "進行初始提交"):
        return False
    
    print("✓ 初始提交完成")
    return True


def setup_remote_repo():
    """設定遠端倉庫"""
    print("\n是否要設定遠端倉庫? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes', '是']:
        remote_url = input("請輸入遠端倉庫 URL: ").strip()
        if remote_url:
            if run_command(f'git remote add origin {remote_url}', "添加遠端倉庫"):
                print("✓ 遠端倉庫設定完成")
                
                # 詢問是否推送
                print("是否要推送到遠端倉庫? (y/n): ", end="")
                push_choice = input().strip().lower()
                if push_choice in ['y', 'yes', '是']:
                    run_command('git push -u origin main', "推送到遠端倉庫")
    
    return True


def main():
    """主程式"""
    print("Excel ZIP Unlocker - Git 初始化設定")
    print("=" * 50)
    
    # 檢查 Git 是否已安裝
    if not check_git_installed():
        print("\n請先安裝 Git:")
        print("1. 下載: https://git-scm.com/downloads")
        print("2. 安裝後重新執行此腳本")
        return False
    
    # 初始化 Git 倉庫
    if not init_git_repo():
        return False
    
    # 設定 Git 配置
    if not setup_git_config():
        return False
    
    # 建立 .gitkeep 檔案
    if not create_gitkeep_files():
        return False
    
    # 建立說明檔案
    if not create_readme_files():
        return False
    
    # 設定 Git 鉤子
    if not setup_git_hooks():
        return False
    
    # 進行初始提交
    if not initial_commit():
        return False
    
    # 設定遠端倉庫
    if not setup_remote_repo():
        return False
    
    print("\n" + "=" * 50)
    print("✓ Git 初始化設定完成！")
    print("\n後續步驟:")
    print("1. 複製 config.example.yaml 為 config.yaml 並填入實際密碼")
    print("2. 複製 env.example 為 .env 並填入實際設定")
    print("3. 將需要處理的檔案放入 input/ 資料夾")
    print("4. 執行 python main.py 開始使用")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
