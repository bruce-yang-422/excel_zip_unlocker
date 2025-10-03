#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: gui.py
用途: Excel ZIP Unlocker GUI 介面
說明: 提供圖形化使用者介面
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logger_manager import LoggerManager
from file_processor import FileProcessor
from report_generator import ReportGenerator


class ExcelZipUnlockerGUI:
    """Excel ZIP Unlocker GUI 主類別"""
    
    def __init__(self):
        """初始化 GUI"""
        self.root = tk.Tk()
        self.setup_window()
        
        # 載入設定
        self.config = self.load_config()
        
        # 建立日誌管理器
        self.logger_manager = LoggerManager(self.config)
        self.logger = self.logger_manager.get_logger('gui')
        
        # 處理狀態
        self.is_processing = False
        self.processing_thread = None
        
        # 建立 GUI 元件
        self.create_widgets()
        
        # 設定變數
        self.input_var = tk.StringVar(value="input")
        self.output_var = tk.StringVar(value="output")
        self.config_var = tk.StringVar(value="config/config.yaml")
        
    def setup_window(self):
        """設定視窗"""
        self.root.title("Excel ZIP Unlocker")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 設定圖示（如果有的話）
        try:
            # 可以在這裡設定應用程式圖示
            pass
        except:
            pass
    
    def load_config(self) -> Dict[str, Any]:
        """載入設定檔"""
        try:
            import yaml
            
            config_path = "config/config.yaml"
            if not os.path.exists(config_path):
                # 建立預設設定
                return self.create_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            return config
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入設定檔時發生錯誤: {e}")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict[str, Any]:
        """建立預設設定"""
        return {
            'log_policy': {
                'keep_days': 7,
                'keep_files': 20,
                'clean_on_start': True,
                'clean_on_exit': False,
                'log_level': 'INFO'
            },
            'passwords': ['123456', 'password123', 'company2025'],
            'file_settings': {
                'supported_extensions': {
                    'excel': ['.xlsx', '.xls', '.xlsm', '.xlsb'],
                    'zip': ['.zip'],
                    'rar': ['.rar']
                },
                'max_file_size': 500,
                'timeout': 300,
                'preserve_structure': True
            },
            'report_settings': {
                'format': 'yaml',
                'include_details': True,
                'include_statistics': True,
                'auto_open': False
            }
        }
    
    def create_widgets(self):
        """建立 GUI 元件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="Excel ZIP Unlocker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 輸入資料夾選擇
        ttk.Label(main_frame, text="輸入資料夾:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="瀏覽", command=self.browse_input_folder).grid(row=1, column=2, padx=(5, 0))
        
        # 輸出資料夾選擇
        ttk.Label(main_frame, text="輸出資料夾:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="瀏覽", command=self.browse_output_folder).grid(row=2, column=2, padx=(5, 0))
        
        # 設定檔選擇
        ttk.Label(main_frame, text="設定檔:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.config_var, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="瀏覽", command=self.browse_config_file).grid(row=3, column=2, padx=(5, 0))
        
        # 密碼設定區域
        password_frame = ttk.LabelFrame(main_frame, text="密碼設定", padding="10")
        password_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        password_frame.columnconfigure(0, weight=1)
        
        # 密碼清單
        self.password_text = scrolledtext.ScrolledText(password_frame, height=6, width=60)
        self.password_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 載入預設密碼
        default_passwords = '\n'.join(self.config.get('passwords', []))
        self.password_text.insert(tk.END, default_passwords)
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="開始處理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止處理", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="開啟輸出資料夾", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看日誌", command=self.view_logs).pack(side=tk.LEFT, padx=5)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 狀態標籤
        self.status_var = tk.StringVar(value="就緒")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # 日誌顯示區域
        log_frame = ttk.LabelFrame(main_frame, text="處理日誌", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 清除日誌按鈕
        ttk.Button(log_frame, text="清除日誌", command=self.clear_log).grid(row=1, column=0, pady=5)
    
    def browse_input_folder(self):
        """瀏覽輸入資料夾"""
        folder = filedialog.askdirectory(title="選擇輸入資料夾")
        if folder:
            self.input_var.set(folder)
    
    def browse_output_folder(self):
        """瀏覽輸出資料夾"""
        folder = filedialog.askdirectory(title="選擇輸出資料夾")
        if folder:
            self.output_var.set(folder)
    
    def browse_config_file(self):
        """瀏覽設定檔"""
        file = filedialog.askopenfilename(
            title="選擇設定檔",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file:
            self.config_var.set(file)
    
    def start_processing(self):
        """開始處理"""
        if self.is_processing:
            return
        
        # 驗證輸入
        input_path = Path(self.input_var.get())
        if not input_path.exists():
            messagebox.showerror("錯誤", f"輸入資料夾不存在: {input_path}")
            return
        
        # 更新密碼設定
        passwords_text = self.password_text.get(1.0, tk.END).strip()
        passwords = [p.strip() for p in passwords_text.split('\n') if p.strip()]
        if not passwords:
            messagebox.showerror("錯誤", "請至少設定一個密碼")
            return
        
        self.config['passwords'] = passwords
        
        # 建立輸出資料夾
        output_path = Path(self.output_var.get())
        output_path.mkdir(exist_ok=True)
        
        # 更新狀態
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("處理中...")
        self.progress_var.set(0)
        
        # 清除日誌
        self.log_text.delete(1.0, tk.END)
        
        # 啟動處理執行緒
        self.processing_thread = threading.Thread(target=self.process_files_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """停止處理"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        self.status_var.set("正在停止...")
        # 注意：實際的停止邏輯需要在處理執行緒中實現
    
    def process_files_thread(self):
        """處理檔案的執行緒"""
        try:
            # 建立檔案處理器
            processor = FileProcessor(self.config, self.logger)
            
            # 處理檔案
            results = processor.process_files(
                str(self.input_var.get()),
                str(self.output_var.get())
            )
            
            # 生成報表
            start_time = datetime.now()
            end_time = datetime.now()
            report_generator = ReportGenerator(self.config, self.logger)
            report_file = report_generator.generate_report(results, start_time, end_time)
            
            # 更新 GUI
            self.root.after(0, self.processing_completed, results, report_file)
            
        except Exception as e:
            self.root.after(0, self.processing_error, str(e))
    
    def processing_completed(self, results, report_file):
        """處理完成回調"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # 更新狀態
        success_rate = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
        self.status_var.set(f"完成 - 成功率: {success_rate:.1f}%")
        
        # 顯示結果
        self.log_text.insert(tk.END, f"處理完成！\n")
        self.log_text.insert(tk.END, f"總檔案數: {results['total']}\n")
        self.log_text.insert(tk.END, f"成功處理: {results['success']}\n")
        self.log_text.insert(tk.END, f"處理失敗: {results['failed']}\n")
        self.log_text.insert(tk.END, f"跳過檔案: {results['skipped']}\n")
        self.log_text.insert(tk.END, f"報表檔案: {report_file}\n")
        
        # 顯示失敗的檔案
        failed_files = [d for d in results['details'] if d['status'] == 'failed']
        if failed_files:
            self.log_text.insert(tk.END, f"\n失敗的檔案:\n")
            for detail in failed_files:
                self.log_text.insert(tk.END, f"  - {detail['file']}: {detail['message']}\n")
        
        self.log_text.see(tk.END)
        
        # 顯示完成訊息
        messagebox.showinfo("完成", f"處理完成！\n成功: {results['success']}, 失敗: {results['failed']}")
    
    def processing_error(self, error_message):
        """處理錯誤回調"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("處理失敗")
        
        self.log_text.insert(tk.END, f"處理時發生錯誤: {error_message}\n")
        self.log_text.see(tk.END)
        
        messagebox.showerror("錯誤", f"處理時發生錯誤:\n{error_message}")
    
    def open_output_folder(self):
        """開啟輸出資料夾"""
        output_path = Path(self.output_var.get())
        if output_path.exists():
            os.startfile(str(output_path))
        else:
            messagebox.showwarning("警告", "輸出資料夾不存在")
    
    def view_logs(self):
        """查看日誌"""
        log_dir = Path("logs")
        if log_dir.exists():
            os.startfile(str(log_dir))
        else:
            messagebox.showwarning("警告", "日誌資料夾不存在")
    
    def clear_log(self):
        """清除日誌顯示"""
        self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """執行 GUI"""
        self.root.mainloop()


def main():
    """GUI 主程式入口"""
    try:
        app = ExcelZipUnlockerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("錯誤", f"啟動 GUI 時發生錯誤: {e}")


if __name__ == "__main__":
    main()
