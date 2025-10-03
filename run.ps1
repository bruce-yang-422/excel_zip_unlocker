# Excel ZIP Unlocker 執行腳本
# 用途: 提供便捷的執行方式
# 版本: 1.0 (2025-10-03)

param(
    [switch]$Help,
    [string]$Input = "input",
    [string]$Output = "output",
    [string]$Config = "config/config.yaml"
)

if ($Help) {
    Write-Host "Excel ZIP Unlocker 執行腳本" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方式:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1                    # 執行互動式選單"
    Write-Host "  .\run.ps1 -Input custom_input -Output custom_output"
    Write-Host ""
    Write-Host "功能選項:" -ForegroundColor Yellow
    Write-Host "  1. 自動檢測 - 處理所有支援的檔案"
    Write-Host "  2. 批次密碼解壓縮 - 只處理 ZIP/RAR 檔案"
    Write-Host "  3. 批次密碼移除 Excel - 只處理 Excel 檔案"
    Write-Host ""
    Write-Host "參數說明:" -ForegroundColor Yellow
    Write-Host "  -Input   指定輸入資料夾 (預設: input)"
    Write-Host "  -Output  指定輸出資料夾 (預設: output)"
    Write-Host "  -Config  指定設定檔路徑 (預設: config/config.yaml)"
    Write-Host "  -Help    顯示此說明"
    Write-Host ""
    exit 0
}

# 檢查 Python 是否已安裝
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 已安裝: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 未安裝或不在 PATH 中" -ForegroundColor Red
    Write-Host "請先安裝 Python 3.8 或更高版本" -ForegroundColor Red
    exit 1
}

# 檢查必要套件
Write-Host "檢查依賴套件..." -ForegroundColor Yellow
try {
    python -c "import msoffcrypto, pyzipper, rarfile, tqdm, yaml" 2>$null
    Write-Host "✓ 所有必要套件已安裝" -ForegroundColor Green
} catch {
    Write-Host "✗ 缺少必要套件" -ForegroundColor Red
    Write-Host "請執行: pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

# 檢查資料夾結構
$requiredDirs = @("input", "output", "logs", "report", "config", "tools")
foreach ($dir in $requiredDirs) {
    if (!(Test-Path $dir)) {
        Write-Host "建立資料夾: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# 檢查設定檔
if (!(Test-Path $Config)) {
    Write-Host "✗ 設定檔不存在: $Config" -ForegroundColor Red
    Write-Host "請確保設定檔存在" -ForegroundColor Red
    exit 1
}

# 執行主程式
Write-Host ""
Write-Host "啟動 Excel ZIP Unlocker..." -ForegroundColor Green
Write-Host "輸入資料夾: $Input" -ForegroundColor Cyan
Write-Host "輸出資料夾: $Output" -ForegroundColor Cyan
Write-Host "設定檔: $Config" -ForegroundColor Cyan
Write-Host ""

# 顯示功能選單
Write-Host "請選擇處理模式:" -ForegroundColor Yellow
Write-Host "1. 自動檢測 (處理所有支援的檔案)" -ForegroundColor White
Write-Host "2. 批次密碼解壓縮 (只處理 ZIP/RAR 檔案)" -ForegroundColor White
Write-Host "3. 批次密碼移除 Excel (只處理 Excel 檔案)" -ForegroundColor White
Write-Host "4. 檢查依賴套件" -ForegroundColor White
Write-Host "5. 退出" -ForegroundColor White
Write-Host ""

do {
    $choice = Read-Host "請輸入選項 (1-5)"
    switch ($choice) {
        "1" {
            Write-Host "啟動自動檢測模式..." -ForegroundColor Yellow
            python main.py -i $Input -o $Output -c $Config -m auto
            break
        }
        "2" {
            Write-Host "啟動批次密碼解壓縮模式..." -ForegroundColor Yellow
            python main.py -i $Input -o $Output -c $Config -m extract
            break
        }
        "3" {
            Write-Host "啟動批次密碼移除 Excel 模式..." -ForegroundColor Yellow
            python main.py -i $Input -o $Output -c $Config -m excel
            break
        }
        "4" {
            Write-Host "檢查依賴套件..." -ForegroundColor Yellow
            python main.py --check-deps
            Write-Host ""
            continue
        }
        "5" {
            Write-Host "退出程式" -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Host "無效選項，請重新選擇" -ForegroundColor Red
            continue
        }
    }
} while ($choice -notin @("1", "2", "3", "4", "5"))

Write-Host ""
Write-Host "程式執行完成" -ForegroundColor Green
Write-Host "按任意鍵退出..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
