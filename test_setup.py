#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_setup.py
用途: 測試專案設定是否正確
說明: 檢查所有模組是否能正常匯入和執行
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
from pathlib import Path

def test_imports():
    """測試模組匯入"""
    print("測試模組匯入...")
    
    try:
        # 添加 src 目錄到路徑
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # 測試核心模組
        from logger_manager import LoggerManager
        from file_processor import FileProcessor
        from report_generator import ReportGenerator
        
        print("V 核心模組匯入成功")
        
        # 測試第三方套件
        import msoffcrypto
        import pyzipper
        import rarfile
        import tqdm
        import yaml
        
        print("V 第三方套件匯入成功")
        
        return True
        
    except ImportError as e:
        print(f"X 模組匯入失敗: {e}")
        return False

def test_config():
    """測試設定檔"""
    print("\n測試設定檔...")
    
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        print("X 設定檔不存在")
        return False
    
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 檢查必要設定
        required_keys = ['passwords', 'file_settings', 'log_policy']
        for key in required_keys:
            if key not in config:
                print(f"X 設定檔缺少必要鍵值: {key}")
                return False
        
        print("V 設定檔載入成功")
        return True
        
    except Exception as e:
        print(f"X 設定檔載入失敗: {e}")
        return False

def test_directories():
    """測試資料夾結構"""
    print("\n測試資料夾結構...")
    
    required_dirs = ['input', 'output', 'logs', 'report', 'config', 'tools', 'src']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"X 資料夾不存在: {dir_name}")
            return False
    
    print("V 資料夾結構正確")
    return True

def test_main_modules():
    """測試主程式模組"""
    print("\n測試主程式模組...")
    
    try:
        # 測試主程式
        import main
        print("V main.py 模組正常")
        
        # 測試 GUI
        import gui
        print("V gui.py 模組正常")
        
        return True
        
    except Exception as e:
        print(f"X 主程式模組測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("Excel ZIP Unlocker 專案設定測試")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_directories,
        test_main_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("V 所有測試通過！專案設定正確。")
        print("\n您可以開始使用 Excel ZIP Unlocker：")
        print("- 執行 run.bat 或 run.ps1")
        print("- 或直接執行 python main.py")
    else:
        print("X 部分測試失敗，請檢查設定。")
        print("\n建議：")
        print("- 執行 pip install -r requirements.txt")
        print("- 檢查 config/config.yaml 設定檔")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
