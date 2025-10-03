#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: src/report_generator.py
用途: 報表生成系統
說明: 負責生成處理結果的報表
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging


class ReportGenerator:
    """報表生成器"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化報表生成器
        
        Args:
            config: 設定檔字典
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.report_dir = Path("report")
        self.report_dir.mkdir(exist_ok=True)
        
        self.report_settings = config.get('report_settings', {})
    
    def generate_report(self, results: Dict[str, Any], start_time: datetime, end_time: datetime) -> str:
        """
        生成處理結果報表
        
        Args:
            results: 處理結果
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            str: 報表檔案路徑
        """
        # 準備報表資料
        report_data = self._prepare_report_data(results, start_time, end_time)
        
        # 根據設定選擇格式
        format_type = self.report_settings.get('format', 'yaml').lower()
        
        if format_type == 'json':
            return self._generate_json_report(report_data)
        elif format_type == 'csv':
            return self._generate_csv_report(report_data)
        else:  # 預設為 yaml
            return self._generate_yaml_report(report_data)
    
    def _prepare_report_data(self, results: Dict[str, Any], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """準備報表資料"""
        duration = (end_time - start_time).total_seconds()
        
        report_data = {
            'report_info': {
                'generated_at': end_time.isoformat(),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'duration_formatted': self._format_duration(duration)
            },
            'summary': {
                'total_files': results['total'],
                'successful': results['success'],
                'failed': results['failed'],
                'skipped': results['skipped'],
                'success_rate': (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
            },
            'details': results['details']
        }
        
        # 添加統計資訊
        if self.report_settings.get('include_statistics', True):
            report_data['statistics'] = self._generate_statistics(results['details'])
        
        return report_data
    
    def _generate_yaml_report(self, report_data: Dict[str, Any]) -> str:
        """生成 YAML 格式報表"""
        try:
            import yaml
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.report_dir / f"report_{timestamp}.yaml"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                yaml.dump(report_data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            self.logger.info(f"YAML 報表已生成: {report_file}")
            return str(report_file)
            
        except ImportError:
            self.logger.error("PyYAML 套件未安裝，無法生成 YAML 報表")
            return self._generate_json_report(report_data)
        except Exception as e:
            self.logger.error(f"生成 YAML 報表時發生錯誤: {e}")
            return self._generate_json_report(report_data)
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """生成 JSON 格式報表"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"JSON 報表已生成: {report_file}")
        return str(report_file)
    
    def _generate_csv_report(self, report_data: Dict[str, Any]) -> str:
        """生成 CSV 格式報表"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"report_{timestamp}.csv"
        
        with open(report_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 寫入標題
            writer.writerow(['檔案路徑', '狀態', '訊息', '輸出路徑', '處理時間'])
            
            # 寫入詳細資料
            for detail in report_data['details']:
                writer.writerow([
                    detail.get('file', ''),
                    detail.get('status', ''),
                    detail.get('message', ''),
                    detail.get('output_path', ''),
                    report_data['report_info']['generated_at']
                ])
        
        self.logger.info(f"CSV 報表已生成: {report_file}")
        return str(report_file)
    
    def _generate_statistics(self, details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成統計資訊"""
        stats = {
            'by_status': {},
            'by_file_type': {},
            'by_error_type': {}
        }
        
        # 按狀態統計
        for detail in details:
            status = detail.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # 按檔案類型統計
        for detail in details:
            file_path = detail.get('file', '')
            if file_path:
                file_ext = Path(file_path).suffix.lower()
                stats['by_file_type'][file_ext] = stats['by_file_type'].get(file_ext, 0) + 1
        
        # 按錯誤類型統計
        for detail in details:
            if detail.get('status') == 'failed':
                message = detail.get('message', '')
                # 提取錯誤類型（簡化處理）
                if '密碼' in message:
                    error_type = '密碼錯誤'
                elif '檔案' in message:
                    error_type = '檔案錯誤'
                elif '權限' in message:
                    error_type = '權限錯誤'
                else:
                    error_type = '其他錯誤'
                
                stats['by_error_type'][error_type] = stats['by_error_type'].get(error_type, 0) + 1
        
        return stats
    
    def _format_duration(self, seconds: float) -> str:
        """格式化時間長度"""
        if seconds < 60:
            return f"{seconds:.1f} 秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} 分鐘"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} 小時"
    
    def cleanup_old_reports(self, keep_days: int = 30):
        """清理舊報表"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            report_files = list(self.report_dir.glob("report_*"))
            
            deleted_count = 0
            for report_file in report_files:
                try:
                    # 從檔案名稱提取時間戳
                    timestamp_str = report_file.stem.split('_', 1)[1]
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if file_date < cutoff_date:
                        report_file.unlink()
                        deleted_count += 1
                except (ValueError, IndexError):
                    continue
            
            if deleted_count > 0:
                self.logger.info(f"已清理 {deleted_count} 個舊報表檔案")
                
        except Exception as e:
            self.logger.error(f"清理報表檔案時發生錯誤: {e}")
