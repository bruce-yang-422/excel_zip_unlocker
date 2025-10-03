#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: src/file_processor.py
用途: 檔案處理核心模組
說明: 負責處理 Excel 和壓縮檔案的解密功能
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# 第三方套件
import msoffcrypto
import pyzipper
import rarfile
from tqdm import tqdm


class FileProcessor:
    """檔案處理器"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化檔案處理器
        
        Args:
            config: 設定檔字典
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.passwords = config.get('passwords', [])
        self.file_settings = config.get('file_settings', {})
        self.external_tools = config.get('external_tools', {})
        
        # 設定 RAR 工具路徑
        if self.external_tools.get('unrar_path'):
            rarfile.UNRAR_TOOL = self.external_tools['unrar_path']
    
    def process_files(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        批次處理檔案
        
        Args:
            input_dir: 輸入資料夾路徑
            output_dir: 輸出資料夾路徑
            
        Returns:
            Dict: 處理結果統計
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 掃描檔案
        files_to_process = self._scan_files(input_path)
        
        if not files_to_process:
            self.logger.warning("未找到需要處理的檔案")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'details': []
            }
        
        self.logger.info(f"找到 {len(files_to_process)} 個檔案需要處理")
        
        # 處理檔案
        results = {
            'total': len(files_to_process),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for file_path in tqdm(files_to_process, desc="處理檔案"):
            try:
                result = self._process_single_file(file_path, output_path)
                results['details'].append(result)
                
                if result['status'] == 'success':
                    results['success'] += 1
                elif result['status'] == 'failed':
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
                    
            except Exception as e:
                error_result = {
                    'file': str(file_path),
                    'status': 'failed',
                    'message': f"處理時發生未預期錯誤: {str(e)}",
                    'output_path': None
                }
                results['details'].append(error_result)
                results['failed'] += 1
                self.logger.error(f"處理檔案 {file_path} 時發生錯誤: {e}")
        
        return results
    
    def process_archive_files(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        只處理壓縮檔案 (ZIP/RAR)
        
        Args:
            input_dir: 輸入資料夾路徑
            output_dir: 輸出資料夾路徑
            
        Returns:
            Dict: 處理結果統計
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 只掃描壓縮檔案
        archive_extensions = self.file_settings.get('supported_extensions', {}).get('archives', [])
        files = []
        for ext in archive_extensions:
            files.extend(input_path.glob(f"*{ext}"))
            files.extend(input_path.glob(f"**/*{ext}"))
        
        self.logger.info(f"找到 {len(files)} 個壓縮檔案")
        
        results = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        if not files:
            self.logger.warning("沒有找到壓縮檔案")
            return results
        
        # 處理檔案
        for file_path in tqdm(files, desc="處理壓縮檔案"):
            try:
                result = self._process_archive_file(file_path, output_path)
                results['details'].append(result)
                
                if result['status'] == 'success':
                    results['success'] += 1
                elif result['status'] == 'skipped':
                    results['skipped'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                error_result = {
                    'file_path': str(file_path),
                    'file_type': 'archive',
                    'status': 'failed',
                    'message': f"處理時發生未預期錯誤: {str(e)}",
                    'output_path': None
                }
                results['details'].append(error_result)
                results['failed'] += 1
                self.logger.error(f"處理檔案 {file_path} 時發生錯誤: {e}")
        
        return results
    
    def process_excel_files(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        只處理 Excel 檔案
        
        Args:
            input_dir: 輸入資料夾路徑
            output_dir: 輸出資料夾路徑
            
        Returns:
            Dict: 處理結果統計
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 只掃描 Excel 檔案
        excel_extensions = self.file_settings.get('supported_extensions', {}).get('excel', [])
        files = []
        for ext in excel_extensions:
            files.extend(input_path.glob(f"*{ext}"))
            files.extend(input_path.glob(f"**/*{ext}"))
        
        self.logger.info(f"找到 {len(files)} 個 Excel 檔案")
        
        results = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        if not files:
            self.logger.warning("沒有找到 Excel 檔案")
            return results
        
        # 處理檔案
        for file_path in tqdm(files, desc="處理 Excel 檔案"):
            try:
                result = self._process_excel_file(file_path, output_path)
                results['details'].append(result)
                
                if result['status'] == 'success':
                    results['success'] += 1
                elif result['status'] == 'skipped':
                    results['skipped'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                error_result = {
                    'file_path': str(file_path),
                    'file_type': 'excel',
                    'status': 'failed',
                    'message': f"處理時發生未預期錯誤: {str(e)}",
                    'output_path': None
                }
                results['details'].append(error_result)
                results['failed'] += 1
                self.logger.error(f"處理檔案 {file_path} 時發生錯誤: {e}")
        
        return results
    
    def _scan_files(self, input_path: Path) -> List[Path]:
        """掃描需要處理的檔案"""
        supported_extensions = self.file_settings.get('supported_extensions', {})
        all_extensions = []
        
        for ext_list in supported_extensions.values():
            all_extensions.extend(ext_list)
        
        files = []
        for ext in all_extensions:
            files.extend(input_path.glob(f"*{ext}"))
            files.extend(input_path.glob(f"**/*{ext}"))
        
        # 過濾檔案大小
        max_size = self.file_settings.get('max_file_size', 500) * 1024 * 1024  # 轉換為位元組
        filtered_files = []
        
        for file_path in files:
            try:
                if file_path.stat().st_size <= max_size:
                    filtered_files.append(file_path)
                else:
                    self.logger.warning(f"檔案 {file_path} 超過大小限制，已跳過")
            except OSError:
                continue
        
        return filtered_files
    
    def _process_single_file(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        處理單一檔案
        
        Args:
            file_path: 檔案路徑
            output_dir: 輸出資料夾
            
        Returns:
            Dict: 處理結果
        """
        file_ext = file_path.suffix.lower()
        supported_extensions = self.file_settings.get('supported_extensions', {})
        
        # 判斷檔案類型
        if file_ext in supported_extensions.get('excel', []):
            return self._process_excel_file(file_path, output_dir)
        elif file_ext in supported_extensions.get('zip', []):
            return self._process_zip_file(file_path, output_dir)
        elif file_ext in supported_extensions.get('rar', []):
            return self._process_rar_file(file_path, output_dir)
        else:
            return {
                'file': str(file_path),
                'status': 'skipped',
                'message': f"不支援的檔案類型: {file_ext}",
                'output_path': None
            }
    
    def _process_excel_file(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """處理 Excel 檔案"""
        try:
            # 嘗試開啟檔案
            with open(file_path, 'rb') as f:
                office_file = msoffcrypto.OfficeFile(f)
                
                # 檢查是否需要密碼
                if not office_file.is_encrypted():
                    # 不需要密碼，直接複製
                    output_path = output_dir / f"unlocked_{file_path.name}"
                    shutil.copy2(file_path, output_path)
                    
                    return {
                        'file': str(file_path),
                        'status': 'success',
                        'message': '檔案未加密，已直接複製',
                        'output_path': str(output_path)
                    }
                
                # 需要密碼，嘗試解密
                for password in self.passwords:
                    try:
                        office_file.load_key(password=password)
                        
                        # 解密到臨時檔案
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_path.suffix) as temp_file:
                            office_file.decrypt(temp_file)
                            temp_path = Path(temp_file.name)
                        
                        # 移動到輸出資料夾
                        output_path = output_dir / f"unlocked_{file_path.name}"
                        shutil.move(str(temp_path), str(output_path))
                        
                        return {
                            'file': str(file_path),
                            'status': 'success',
                            'message': f'使用密碼解密成功',
                            'output_path': str(output_path)
                        }
                        
                    except Exception:
                        continue
                
                # 所有密碼都失敗
                return {
                    'file': str(file_path),
                    'status': 'failed',
                    'message': '所有密碼都無法解密此檔案',
                    'output_path': None
                }
                
        except Exception as e:
            return {
                'file': str(file_path),
                'status': 'failed',
                'message': f'處理 Excel 檔案時發生錯誤: {str(e)}',
                'output_path': None
            }
    
    def _process_zip_file(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """處理 ZIP 檔案"""
        try:
            # 嘗試開啟 ZIP 檔案
            with pyzipper.AESZipFile(file_path, 'r') as zip_file:
                # 檢查是否需要密碼
                if not zip_file.needs_password():
                    # 不需要密碼，直接解壓
                    output_subdir = output_dir / f"unlocked_{file_path.stem}"
                    output_subdir.mkdir(exist_ok=True)
                    zip_file.extractall(output_subdir)
                    
                    return {
                        'file': str(file_path),
                        'status': 'success',
                        'message': 'ZIP 檔案未加密，已直接解壓',
                        'output_path': str(output_subdir)
                    }
                
                # 需要密碼，嘗試解密
                for password in self.passwords:
                    try:
                        zip_file.setpassword(password.encode('utf-8'))
                        
                        # 測試密碼是否正確
                        zip_file.testzip()
                        
                        # 解壓到輸出資料夾
                        output_subdir = output_dir / f"unlocked_{file_path.stem}"
                        output_subdir.mkdir(exist_ok=True)
                        zip_file.extractall(output_subdir)
                        
                        return {
                            'file': str(file_path),
                            'status': 'success',
                            'message': f'使用密碼解壓成功',
                            'output_path': str(output_subdir)
                        }
                        
                    except Exception:
                        continue
                
                # 所有密碼都失敗
                return {
                    'file': str(file_path),
                    'status': 'failed',
                    'message': '所有密碼都無法解壓此 ZIP 檔案',
                    'output_path': None
                }
                
        except Exception as e:
            return {
                'file': str(file_path),
                'status': 'failed',
                'message': f'處理 ZIP 檔案時發生錯誤: {str(e)}',
                'output_path': None
            }
    
    def _process_rar_file(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """處理 RAR 檔案"""
        try:
            # 嘗試開啟 RAR 檔案
            with rarfile.RarFile(file_path) as rar_file:
                # 檢查是否需要密碼
                if not rar_file.needs_password():
                    # 不需要密碼，直接解壓
                    output_subdir = output_dir / f"unlocked_{file_path.stem}"
                    output_subdir.mkdir(exist_ok=True)
                    rar_file.extractall(output_subdir)
                    
                    return {
                        'file': str(file_path),
                        'status': 'success',
                        'message': 'RAR 檔案未加密，已直接解壓',
                        'output_path': str(output_subdir)
                    }
                
                # 需要密碼，嘗試解密
                for password in self.passwords:
                    try:
                        # 測試密碼是否正確
                        rar_file.setpassword(password)
                        
                        # 解壓到輸出資料夾
                        output_subdir = output_dir / f"unlocked_{file_path.stem}"
                        output_subdir.mkdir(exist_ok=True)
                        rar_file.extractall(output_subdir)
                        
                        return {
                            'file': str(file_path),
                            'status': 'success',
                            'message': f'使用密碼解壓成功',
                            'output_path': str(output_subdir)
                        }
                        
                    except Exception:
                        continue
                
                # 所有密碼都失敗
                return {
                    'file': str(file_path),
                    'status': 'failed',
                    'message': '所有密碼都無法解壓此 RAR 檔案',
                    'output_path': None
                }
                
        except Exception as e:
            return {
                'file': str(file_path),
                'status': 'failed',
                'message': f'處理 RAR 檔案時發生錯誤: {str(e)}',
                'output_path': None
            }
