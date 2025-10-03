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
    Write-Host "  .\run.ps1                    # 執行命令行版本"
    Write-Host "  .\run.ps1 -Input custom_input -Output custom_output"
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

Write-Host "啟動命令行版本..." -ForegroundColor Yellow
python main.py -i $Input -o $Output -c $Config

Write-Host ""
Write-Host "程式執行完成" -ForegroundColor Green
Write-Host "按任意鍵退出..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
