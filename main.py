#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
用途: Excel ZIP Unlocker 主程式
說明: 批次處理受保護的 Excel 和壓縮檔案的命令行介面
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logger_manager import LoggerManager
from file_processor import FileProcessor
from report_generator import ReportGenerator


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    載入設定檔
    
    Args:
        config_path: 設定檔路徑
        
    Returns:
        Dict: 設定檔內容
    """
    try:
        import yaml
        
        if not os.path.exists(config_path):
            print(f"錯誤：設定檔 {config_path} 不存在")
            sys.exit(1)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
        
    except ImportError:
        print("錯誤：PyYAML 套件未安裝")
        sys.exit(1)
    except Exception as e:
        print(f"錯誤：載入設定檔時發生錯誤: {e}")
        sys.exit(1)


def check_dependencies():
    """檢查必要的套件是否已安裝"""
    required_packages = [
        'msoffcrypto',
        'pyzipper',
        'rarfile',
        'tqdm',
        'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            elif package == 'msoffcrypto':
                import msoffcrypto
            elif package == 'pyzipper':
                import pyzipper
            elif package == 'rarfile':
                import rarfile
            elif package == 'tqdm':
                import tqdm
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"錯誤：以下套件未安裝: {', '.join(missing_packages)}")
        print("請執行: pip install -r requirements.txt")
        sys.exit(1)


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description='Excel ZIP Unlocker - 批次處理受保護的 Excel 和壓縮檔案',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python main.py                    # 使用預設設定處理檔案
  python main.py -i custom_input    # 指定輸入資料夾
  python main.py -o custom_output   # 指定輸出資料夾
  python main.py -c custom_config.yaml  # 使用自訂設定檔
  python main.py -m extract            # 只處理壓縮檔案
  python main.py -m excel              # 只處理 Excel 檔案
        """
    )
    
    parser.add_argument('-i', '--input', default='input',
                        help='輸入資料夾路徑 (預設: input)')
    parser.add_argument('-o', '--output', default='output',
                        help='輸出資料夾路徑 (預設: output)')
    parser.add_argument('-c', '--config', default='config/config.yaml',
                        help='設定檔路徑 (預設: config/config.yaml)')
    parser.add_argument('-m', '--mode', choices=['auto', 'extract', 'excel'], default='auto',
                        help='處理模式: auto=自動檢測, extract=只解壓縮, excel=只處理Excel (預設: auto)')
    parser.add_argument('--check-deps', action='store_true',
                        help='檢查依賴套件')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='顯示詳細輸出')
    
    args = parser.parse_args()
    
    # 檢查依賴套件
    if args.check_deps:
        check_dependencies()
        print("V 所有依賴套件已正確安裝")
        return
    
    # 啟動 GUI 介面
    if args.gui:
        try:
            from gui import main as gui_main
            gui_main()
            return
        except ImportError:
            print("錯誤：GUI 模組未找到，請確保 gui.py 檔案存在")
            sys.exit(1)
    
    # 檢查依賴套件
    check_dependencies()
    
    # 載入設定檔
    config = load_config(args.config)
    
    # 建立日誌管理器
    logger_manager = LoggerManager(config)
    logger = logger_manager.get_logger('main')
    
    try:
        # 檢查輸入資料夾
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"輸入資料夾不存在: {input_path}")
            sys.exit(1)
        
        # 建立輸出資料夾
        output_path = Path(args.output)
        output_path.mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("Excel ZIP Unlocker 開始執行")
        logger.info("=" * 60)
        logger.info(f"輸入資料夾: {input_path.absolute()}")
        logger.info(f"輸出資料夾: {output_path.absolute()}")
        logger.info(f"設定檔: {args.config}")
        logger.info(f"處理模式: {args.mode}")
        logger.info(f"密碼數量: {len(config.get('passwords', []))}")
        
        # 記錄開始時間
        start_time = datetime.now()
        
        # 建立檔案處理器
        processor = FileProcessor(config, logger)
        
        # 根據模式處理檔案
        if args.mode == 'extract':
            logger.info("模式: 只處理壓縮檔案 (ZIP/RAR)")
            results = processor.process_archive_files(str(input_path), str(output_path))
        elif args.mode == 'excel':
            logger.info("模式: 只處理 Excel 檔案")
            results = processor.process_excel_files(str(input_path), str(output_path))
        else:  # auto
            logger.info("模式: 自動檢測檔案類型")
            results = processor.process_files(str(input_path), str(output_path))
        
        # 記錄結束時間
        end_time = datetime.now()
        
        # 生成報表
        report_generator = ReportGenerator(config, logger)
        report_file = report_generator.generate_report(results, start_time, end_time)
        
        # 輸出結果摘要
        logger.info("=" * 60)
        logger.info("處理結果摘要")
        logger.info("=" * 60)
        logger.info(f"總檔案數: {results['total']}")
        logger.info(f"成功處理: {results['success']}")
        logger.info(f"處理失敗: {results['failed']}")
        logger.info(f"跳過檔案: {results['skipped']}")
        logger.info(f"成功率: {(results['success'] / results['total'] * 100):.1f}%" if results['total'] > 0 else "成功率: 0%")
        logger.info(f"處理時間: {(end_time - start_time).total_seconds():.2f} 秒")
        logger.info(f"報表檔案: {report_file}")
        
        # 顯示失敗的檔案
        failed_files = [d for d in results['details'] if d['status'] == 'failed']
        if failed_files:
            logger.warning("失敗的檔案:")
            for detail in failed_files:
                logger.warning(f"  - {detail['file']}: {detail['message']}")
        
        logger.info("=" * 60)
        logger.info("處理完成")
        logger.info("=" * 60)
        
        # 清理日誌
        logger_manager.cleanup_on_exit()
        
    except KeyboardInterrupt:
        logger.info("使用者中斷執行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"執行時發生未預期錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
