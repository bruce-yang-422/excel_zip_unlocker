@echo off
chcp 65001 >nul
title Excel ZIP Unlocker

echo.
echo ========================================
echo    Excel ZIP Unlocker 批次執行腳本
echo ========================================
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] Python 未安裝或不在 PATH 中
    echo 請先安裝 Python 3.8 或更高版本
    pause
    exit /b 1
)

REM 檢查必要套件
echo [檢查] 檢查依賴套件...
python -c "import msoffcrypto, pyzipper, rarfile, tqdm, yaml" >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 缺少必要套件
    echo 請執行: pip install -r requirements.txt
    pause
    exit /b 1
)

REM 檢查資料夾結構
echo [檢查] 檢查資料夾結構...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "report" mkdir report
if not exist "config" mkdir config
if not exist "tools" mkdir tools

REM 檢查設定檔
if not exist "config\config.yaml" (
    echo [錯誤] 設定檔不存在: config\config.yaml
    echo 請確保設定檔存在
    pause
    exit /b 1
)

echo [完成] 環境檢查通過
echo.

REM 顯示選單
:menu
echo 請選擇執行模式:
echo 1. 命令行版本
echo 2. GUI 版本
echo 3. 檢查依賴套件
echo 4. 退出
echo.
set /p choice=請輸入選項 (1-4): 

if "%choice%"=="1" goto cmd_mode
if "%choice%"=="2" goto gui_mode
if "%choice%"=="3" goto check_deps
if "%choice%"=="4" goto exit
echo [錯誤] 無效選項，請重新選擇
echo.
goto menu

:cmd_mode
echo.
echo [啟動] 命令行版本...
python main.py
goto end

:gui_mode
echo.
echo [啟動] GUI 版本...
python gui.py
goto end

:check_deps
echo.
echo [檢查] 依賴套件狀態...
python main.py --check-deps
echo.
pause
goto menu

:exit
echo.
echo 感謝使用 Excel ZIP Unlocker！
exit /b 0

:end
echo.
echo 程式執行完成
pause
