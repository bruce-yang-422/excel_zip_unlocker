#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: build.py
用途: PyInstaller 打包腳本
說明: 將 Python 程式打包成 Windows EXE 檔案
Authors: AI Assistant
版本: 1.0 (2025-10-03)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """檢查 PyInstaller 是否已安裝"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安裝 (版本: {PyInstaller.__version__})")
        return True
    except ImportError:
        print("✗ PyInstaller 未安裝")
        print("請執行: pip install pyinstaller")
        return False


def create_spec_file():
    """建立 PyInstaller spec 檔案"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'msoffcrypto',
        'pyzipper',
        'rarfile',
        'tqdm',
        'yaml',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='excel_zip_unlocker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# GUI 版本
exe_gui = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='excel_zip_unlocker_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('excel_zip_unlocker.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 已建立 PyInstaller spec 檔案")


def build_executable():
    """建立可執行檔案"""
    print("開始打包...")
    
    try:
        # 執行 PyInstaller
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'excel_zip_unlocker.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✓ 打包完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False


def copy_additional_files():
    """複製額外的檔案到 dist 目錄"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        return
    
    # 複製必要的資料夾
    folders_to_copy = ['input', 'output', 'logs', 'report', 'tools']
    
    for folder in folders_to_copy:
        src = Path(folder)
        if src.exists():
            dst = dist_dir / folder
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✓ 已複製資料夾: {folder}")
    
    # 複製 README 檔案
    readme_files = ['README.md', 'README.txt']
    for readme in readme_files:
        src = Path(readme)
        if src.exists():
            dst = dist_dir / readme
            shutil.copy2(src, dst)
            print(f"✓ 已複製檔案: {readme}")


def create_batch_files():
    """建立批次執行檔案"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        return
    
    # 建立命令行版本批次檔
    cmd_batch = '''@echo off
echo Excel ZIP Unlocker - 命令行版本
echo.
excel_zip_unlocker.exe
pause
'''
    
    with open(dist_dir / 'run_cmd.bat', 'w', encoding='utf-8') as f:
        f.write(cmd_batch)
    
    # 建立 GUI 版本批次檔
    gui_batch = '''@echo off
echo Excel ZIP Unlocker - GUI 版本
echo.
excel_zip_unlocker_gui.exe
'''
    
    with open(dist_dir / 'run_gui.bat', 'w', encoding='utf-8') as f:
        f.write(gui_batch)
    
    print("✓ 已建立批次執行檔案")


def main():
    """主程式"""
    print("Excel ZIP Unlocker 打包腳本")
    print("=" * 40)
    
    # 檢查 PyInstaller
    if not check_pyinstaller():
        return
    
    # 建立 spec 檔案
    create_spec_file()
    
    # 打包
    if not build_executable():
        return
    
    # 複製額外檔案
    copy_additional_files()
    
    # 建立批次檔案
    create_batch_files()
    
    print("\n" + "=" * 40)
    print("打包完成！")
    print("可執行檔案位於 dist/ 目錄中")
    print("- excel_zip_unlocker.exe (命令行版本)")
    print("- excel_zip_unlocker_gui.exe (GUI 版本)")
    print("- run_cmd.bat (執行命令行版本)")
    print("- run_gui.bat (執行 GUI 版本)")


if __name__ == "__main__":
    main()
