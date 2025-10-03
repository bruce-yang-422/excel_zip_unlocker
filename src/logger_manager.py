#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: src/logger_manager.py
用途: 日誌管理系統
說明: 負責日誌的建立、清理、輪轉等功能
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import logging
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any


class LoggerManager:
    """日誌管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化日誌管理器
        
        Args:
            config: 設定檔字典
        """
        self.config = config
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 設定日誌等級
        log_level = getattr(logging, config.get('log_level', 'INFO').upper())
        
        # 設定日誌格式
        self.log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 建立主日誌器
        self.logger = logging.getLogger('excel_zip_unlocker')
        self.logger.setLevel(log_level)
        
        # 清除現有的處理器
        self.logger.handlers.clear()
        
        # 建立檔案處理器
        self._setup_file_handler()
        
        # 建立控制台處理器
        self._setup_console_handler()
        
        # 清理舊日誌
        if config.get('clean_on_start', True):
            self.cleanup_old_logs()
    
    def _setup_file_handler(self):
        """設定檔案處理器"""
        # 建立日誌檔案名稱（包含時間戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"unlocker_{timestamp}.log"
        
        # 建立檔案處理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.log_format)
        
        self.logger.addHandler(file_handler)
        
        # 記錄日誌檔案路徑
        self.logger.info(f"日誌檔案已建立: {log_file}")
    
    def _setup_console_handler(self):
        """設定控制台處理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.log_format)
        
        self.logger.addHandler(console_handler)
    
    def cleanup_old_logs(self):
        """清理舊日誌檔案"""
        try:
            log_policy = self.config.get('log_policy', {})
            keep_days = log_policy.get('keep_days', 7)
            keep_files = log_policy.get('keep_files', 20)
            
            # 按時間清理
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            log_files = list(self.log_dir.glob("unlocker_*.log"))
            
            # 過濾掉過舊的檔案
            files_to_delete = []
            for log_file in log_files:
                try:
                    # 從檔案名稱提取時間戳
                    timestamp_str = log_file.stem.split('_', 1)[1]
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if file_date < cutoff_date:
                        files_to_delete.append(log_file)
                except (ValueError, IndexError):
                    # 如果無法解析時間戳，保留檔案
                    continue
            
            # 按檔案數量清理
            remaining_files = [f for f in log_files if f not in files_to_delete]
            remaining_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(remaining_files) > keep_files:
                files_to_delete.extend(remaining_files[keep_files:])
            
            # 刪除檔案
            deleted_count = 0
            for log_file in files_to_delete:
                try:
                    log_file.unlink()
                    deleted_count += 1
                except OSError as e:
                    self.logger.warning(f"無法刪除日誌檔案 {log_file}: {e}")
            
            if deleted_count > 0:
                self.logger.info(f"已清理 {deleted_count} 個舊日誌檔案")
                
        except Exception as e:
            self.logger.error(f"清理日誌檔案時發生錯誤: {e}")
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """
        取得日誌器
        
        Args:
            name: 日誌器名稱
            
        Returns:
            logging.Logger: 日誌器實例
        """
        if name:
            logger = logging.getLogger(f'excel_zip_unlocker.{name}')
        else:
            logger = self.logger
        
        return logger
    
    def log_processing_start(self, file_count: int):
        """記錄處理開始"""
        self.logger.info(f"開始批次處理，共 {file_count} 個檔案")
    
    def log_processing_end(self, success_count: int, failed_count: int, total_time: float):
        """記錄處理結束"""
        self.logger.info(f"批次處理完成 - 成功: {success_count}, 失敗: {failed_count}, 耗時: {total_time:.2f}秒")
    
    def log_file_processing(self, file_path: str, status: str, message: str = ""):
        """記錄單一檔案處理結果"""
        if status == "success":
            self.logger.info(f"✓ {file_path} - {message}")
        elif status == "failed":
            self.logger.error(f"✗ {file_path} - {message}")
        elif status == "skipped":
            self.logger.warning(f"- {file_path} - {message}")
        else:
            self.logger.debug(f"? {file_path} - {message}")
    
    def cleanup_on_exit(self):
        """程式結束時清理"""
        if self.config.get('log_policy', {}).get('clean_on_exit', False):
            self.cleanup_old_logs()
        
        # 關閉所有處理器
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
