#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: check_git_security.py
用途: Git 安全檢查腳本
說明: 檢查專案中的敏感檔案是否被正確排除
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class GitSecurityChecker:
    """Git 安全檢查器"""
    
    def __init__(self):
        """初始化檢查器"""
        self.sensitive_patterns = [
            # 密碼和設定檔案
            'config/config.yaml',
            'config/*.yaml',
            'config/*.yml',
            '*.passwords',
            '*.keys',
            'passwords.txt',
            'password_list.txt',
            
            # 環境變數檔案
            '.env',
            '.env.*',
            
            # Excel 和壓縮檔案
            '*.xlsx',
            '*.xls',
            '*.xlsm',
            '*.xlsb',
            '*.zip',
            '*.rar',
            '*.7z',
            
            # 日誌和報表檔案
            'logs/*.log',
            'report/*.yaml',
            'report/*.json',
            'report/*.csv',
            
            # 外部工具
            'tools/*.exe',
            'tools/*.dll',
        ]
        
        self.warnings = []
        self.errors = []
    
    def check_git_status(self) -> bool:
        """檢查 Git 狀態"""
        print("檢查 Git 狀態...")
        
        try:
            # 檢查是否在 Git 倉庫中
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("WARNING: 不在 Git 倉庫中")
                return False
            
            print("V Git 倉庫狀態正常")
            return True
            
        except FileNotFoundError:
            print("ERROR: Git 未安裝或不在 PATH 中")
            return False
    
    def check_gitignore(self) -> bool:
        """檢查 .gitignore 檔案"""
        print("\n檢查 .gitignore 檔案...")
        
        gitignore_path = Path('.gitignore')
        if not gitignore_path.exists():
            print("ERROR: .gitignore 檔案不存在")
            self.errors.append("缺少 .gitignore 檔案")
            return False
        
        print("V .gitignore 檔案存在")
        
        # 檢查 .gitignore 內容
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查關鍵的忽略規則
        required_rules = [
            'config/config.yaml',
            '*.xlsx',
            '*.xls',
            '*.zip',
            '*.rar',
            '.env',
            'logs/*',
            'report/*'
        ]
        
        missing_rules = []
        for rule in required_rules:
            if rule not in content:
                missing_rules.append(rule)
        
        if missing_rules:
            print(f"WARNING: 缺少忽略規則: {', '.join(missing_rules)}")
            self.warnings.append(f"缺少忽略規則: {', '.join(missing_rules)}")
        else:
            print("V 關鍵忽略規則完整")
        
        return True
    
    def check_gitattributes(self) -> bool:
        """檢查 .gitattributes 檔案"""
        print("\n檢查 .gitattributes 檔案...")
        
        gitattributes_path = Path('.gitattributes')
        if not gitattributes_path.exists():
            print("WARNING: .gitattributes 檔案不存在")
            self.warnings.append("缺少 .gitattributes 檔案")
            return False
        
        print("V .gitattributes 檔案存在")
        return True
    
    def check_tracked_files(self) -> bool:
        """檢查已追蹤的檔案"""
        print("\n檢查已追蹤的檔案...")
        
        try:
            # 取得已追蹤的檔案清單
            result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
            if result.returncode != 0:
                print("ERROR: 無法取得已追蹤檔案清單")
                return False
            
            tracked_files = result.stdout.strip().split('\n')
            if not tracked_files or tracked_files == ['']:
                print("V 沒有已追蹤的檔案")
                return True
            
            # 檢查敏感檔案
            sensitive_tracked = []
            for file_path in tracked_files:
                for pattern in self.sensitive_patterns:
                    if self._match_pattern(file_path, pattern):
                        sensitive_tracked.append(file_path)
                        break
            
            if sensitive_tracked:
                print(f"ERROR: 發現已追蹤的敏感檔案:")
                for file_path in sensitive_tracked:
                    print(f"  - {file_path}")
                self.errors.append(f"已追蹤敏感檔案: {', '.join(sensitive_tracked)}")
                return False
            else:
                print("V 沒有已追蹤的敏感檔案")
                return True
                
        except Exception as e:
            print(f"ERROR: 檢查已追蹤檔案時發生錯誤: {e}")
            return False
    
    def check_staged_files(self) -> bool:
        """檢查暫存區檔案"""
        print("\n檢查暫存區檔案...")
        
        try:
            # 取得暫存區檔案清單
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("ERROR: 無法取得暫存區檔案清單")
                return False
            
            staged_files = result.stdout.strip().split('\n')
            if not staged_files or staged_files == ['']:
                print("V 暫存區沒有檔案")
                return True
            
            # 檢查敏感檔案
            sensitive_staged = []
            for file_path in staged_files:
                for pattern in self.sensitive_patterns:
                    if self._match_pattern(file_path, pattern):
                        sensitive_staged.append(file_path)
                        break
            
            if sensitive_staged:
                print(f"ERROR: 發現暫存區中的敏感檔案:")
                for file_path in sensitive_staged:
                    print(f"  - {file_path}")
                self.errors.append(f"暫存區敏感檔案: {', '.join(sensitive_staged)}")
                return False
            else:
                print("V 暫存區沒有敏感檔案")
                return True
                
        except Exception as e:
            print(f"ERROR: 檢查暫存區檔案時發生錯誤: {e}")
            return False
    
    def check_working_directory(self) -> bool:
        """檢查工作目錄中的敏感檔案"""
        print("\n檢查工作目錄中的敏感檔案...")
        
        sensitive_files = []
        
        # 檢查特定檔案
        sensitive_paths = [
            'config/config.yaml',
            '.env',
            'passwords.txt',
            'password_list.txt'
        ]
        
        for path in sensitive_paths:
            if Path(path).exists():
                sensitive_files.append(path)
        
        # 檢查資料夾中的敏感檔案
        sensitive_dirs = ['input', 'output', 'logs', 'report', 'tools']
        for dir_name in sensitive_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        ext = file_path.suffix.lower()
                        if ext in ['.xlsx', '.xls', '.zip', '.rar', '.log', '.yaml', '.json']:
                            sensitive_files.append(str(file_path))
        
        if sensitive_files:
            print(f"WARNING: 發現工作目錄中的敏感檔案:")
            for file_path in sensitive_files[:10]:  # 只顯示前10個
                print(f"  - {file_path}")
            if len(sensitive_files) > 10:
                print(f"  ... 還有 {len(sensitive_files) - 10} 個檔案")
            print("  這些檔案應該被 .gitignore 排除")
            self.warnings.append(f"工作目錄中的敏感檔案: {len(sensitive_files)} 個")
        else:
            print("V 工作目錄中沒有敏感檔案")
        
        return True
    
    def check_git_hooks(self) -> bool:
        """檢查 Git 鉤子"""
        print("\n檢查 Git 鉤子...")
        
        hooks_dir = Path('.git/hooks')
        if not hooks_dir.exists():
            print("WARNING: Git 鉤子目錄不存在")
            return True
        
        pre_commit_hook = hooks_dir / 'pre-commit'
        if not pre_commit_hook.exists():
            print("WARNING: pre-commit 鉤子不存在")
            self.warnings.append("缺少 pre-commit 鉤子")
        else:
            print("V pre-commit 鉤子存在")
        
        return True
    
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """檢查檔案路徑是否匹配模式"""
        if '*' not in pattern:
            return file_path == pattern
        
        # 簡單的萬用字元匹配
        if pattern.endswith('/*'):
            prefix = pattern[:-2]
            return file_path.startswith(prefix + '/')
        elif pattern.startswith('*'):
            suffix = pattern[1:]
            return file_path.endswith(suffix)
        elif '*' in pattern:
            # 更複雜的匹配邏輯
            import fnmatch
            return fnmatch.fnmatch(file_path, pattern)
        
        return False
    
    def generate_report(self) -> Dict[str, Any]:
        """生成檢查報告"""
        report = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'PASS' if not self.errors else 'FAIL'
        }
        
        return report
    
    def run_all_checks(self) -> bool:
        """執行所有檢查"""
        print("Excel ZIP Unlocker - Git 安全檢查")
        print("=" * 50)
        
        checks = [
            self.check_git_status,
            self.check_gitignore,
            self.check_gitattributes,
            self.check_tracked_files,
            self.check_staged_files,
            self.check_working_directory,
            self.check_git_hooks
        ]
        
        all_passed = True
        for check in checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                print(f"ERROR: 檢查時發生錯誤: {e}")
                all_passed = False
        
        # 生成報告
        report = self.generate_report()
        
        print("\n" + "=" * 50)
        print("檢查結果摘要:")
        print(f"狀態: {report['status']}")
        print(f"錯誤: {len(report['errors'])}")
        print(f"警告: {len(report['warnings'])}")
        
        if report['errors']:
            print("\n錯誤:")
            for error in report['errors']:
                print(f"  X {error}")
        
        if report['warnings']:
            print("\n警告:")
            for warning in report['warnings']:
                print(f"  W {warning}")
        
        if report['status'] == 'PASS':
            print("\nV Git 安全檢查通過！")
        else:
            print("\nERROR: Git 安全檢查失敗！")
            print("\n建議:")
            print("1. 檢查 .gitignore 檔案是否包含所有敏感檔案類型")
            print("2. 移除已追蹤的敏感檔案: git rm --cached <file>")
            print("3. 設定 pre-commit 鉤子防止未來提交敏感檔案")
        
        return all_passed


def main():
    """主程式"""
    checker = GitSecurityChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
