# Excel ZIP Unlocker - Git 初始化設定腳本 (PowerShell)
# 版本: 1.0
# 說明: 自動設定 Git 倉庫和相關配置

param(
    [switch]$Help,
    [string]$RemoteUrl = "",
    [switch]$SkipRemote
)

if ($Help) {
    Write-Host "Excel ZIP Unlocker - Git 初始化設定腳本" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方式:" -ForegroundColor Yellow
    Write-Host "  .\setup_git.ps1                    # 基本設定"
    Write-Host "  .\setup_git.ps1 -RemoteUrl <URL>  # 設定遠端倉庫"
    Write-Host "  .\setup_git.ps1 -SkipRemote       # 跳過遠端倉庫設定"
    Write-Host ""
    Write-Host "參數說明:" -ForegroundColor Yellow
    Write-Host "  -RemoteUrl  遠端倉庫 URL"
    Write-Host "  -SkipRemote 跳過遠端倉庫設定"
    Write-Host "  -Help       顯示此說明"
    Write-Host ""
    exit 0
}

Write-Host "Excel ZIP Unlocker - Git 初始化設定" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 檢查 Git 是否已安裝
Write-Host "檢查 Git 安裝狀態..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>$null
    Write-Host "✓ Git 已安裝: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git 未安裝或不在 PATH 中" -ForegroundColor Red
    Write-Host "請先安裝 Git: https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}

# 初始化 Git 倉庫
Write-Host "`n初始化 Git 倉庫..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git 倉庫已存在" -ForegroundColor Green
} else {
    try {
        git init
        Write-Host "✓ Git 倉庫初始化完成" -ForegroundColor Green
    } catch {
        Write-Host "✗ Git 倉庫初始化失敗" -ForegroundColor Red
        exit 1
    }
}

# 設定 Git 配置
Write-Host "`n設定 Git 配置..." -ForegroundColor Yellow

# 檢查使用者名稱
try {
    git config user.name | Out-Null
    Write-Host "✓ Git 使用者名稱已設定" -ForegroundColor Green
} catch {
    $name = Read-Host "請輸入 Git 使用者名稱"
    if ($name) {
        git config user.name $name
        Write-Host "✓ 使用者名稱已設定" -ForegroundColor Green
    }
}

# 檢查使用者郵箱
try {
    git config user.email | Out-Null
    Write-Host "✓ Git 使用者郵箱已設定" -ForegroundColor Green
} catch {
    $email = Read-Host "請輸入 Git 使用者郵箱"
    if ($email) {
        git config user.email $email
        Write-Host "✓ 使用者郵箱已設定" -ForegroundColor Green
    }
}

# 設定其他配置
git config core.autocrlf true
git config core.safecrlf true
git config pull.rebase false
Write-Host "✓ Git 基本配置已設定" -ForegroundColor Green

# 建立 .gitkeep 檔案
Write-Host "`n建立 .gitkeep 檔案..." -ForegroundColor Yellow
$directories = @('input', 'output', 'logs', 'report', 'tools')

foreach ($dir in $directories) {
    $gitkeepPath = Join-Path $dir ".gitkeep"
    if (!(Test-Path $gitkeepPath)) {
        "# 保持此資料夾在 Git 中" | Out-File -FilePath $gitkeepPath -Encoding UTF8
        Write-Host "✓ 已建立 $gitkeepPath" -ForegroundColor Green
    }
}

# 建立資料夾說明檔案
Write-Host "`n建立資料夾說明檔案..." -ForegroundColor Yellow
$folderDescriptions = @{
    'input' = '待處理的 Excel 和壓縮檔案'
    'output' = '處理完成後的解密檔案'
    'logs' = '程式執行日誌檔案'
    'report' = '處理結果報表檔案'
    'tools' = '外部工具執行檔 (如 unrar.exe)'
}

foreach ($folder in $folderDescriptions.Keys) {
    $readmePath = Join-Path $folder "README.md"
    if (!(Test-Path $readmePath)) {
        $content = @"
# 資料夾說明

此資料夾用於存放 $folder 相關檔案。

## 注意事項

- 請勿將敏感檔案提交到版本控制
- 定期清理不需要的檔案
- 遵守公司安全政策

## 檔案類型

$($folderDescriptions[$folder])
"@
        $content | Out-File -FilePath $readmePath -Encoding UTF8
        Write-Host "✓ 已建立 $readmePath" -ForegroundColor Green
    }
}

# 設定 Git 鉤子
Write-Host "`n設定 Git 鉤子..." -ForegroundColor Yellow
$hooksDir = ".git\hooks"
if (Test-Path $hooksDir) {
    $preCommitHook = @"
#!/bin/sh
# Pre-commit 鉤子
# 檢查敏感檔案

echo "檢查敏感檔案..."

# 檢查是否包含密碼檔案
if git diff --cached --name-only | grep -E "\.(passwords|keys|env)$"; then
    echo "錯誤: 檢測到敏感檔案，請移除後再提交"
    exit 1
fi

# 檢查是否包含 Excel 或壓縮檔案
if git diff --cached --name-only | grep -E "\.(xlsx|xls|zip|rar)$"; then
    echo "錯誤: 檢測到 Excel 或壓縮檔案，請移除後再提交"
    exit 1
fi

echo "檢查通過"
"@
    
    $preCommitPath = Join-Path $hooksDir "pre-commit"
    $preCommitHook | Out-File -FilePath $preCommitPath -Encoding UTF8
    Write-Host "✓ 已設定 pre-commit 鉤子" -ForegroundColor Green
}

# 進行初始提交
Write-Host "`n準備進行初始提交..." -ForegroundColor Yellow
try {
    git add .
    Write-Host "✓ 檔案已添加到暫存區" -ForegroundColor Green
    
    # 檢查是否有檔案需要提交
    $status = git status --porcelain
    if (!$status) {
        Write-Host "✓ 沒有檔案需要提交" -ForegroundColor Green
    } else {
        $commitMessage = @"
初始提交

- 建立 Excel ZIP Unlocker 專案
- 設定 Git 忽略規則
- 建立專案結構和文件
- 設定安全配置
"@
        
        git commit -m $commitMessage
        Write-Host "✓ 初始提交完成" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ 提交失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 設定遠端倉庫
if (!$SkipRemote) {
    Write-Host "`n設定遠端倉庫..." -ForegroundColor Yellow
    
    if ($RemoteUrl) {
        try {
            git remote add origin $RemoteUrl
            Write-Host "✓ 遠端倉庫已設定: $RemoteUrl" -ForegroundColor Green
            
            $pushChoice = Read-Host "是否要推送到遠端倉庫? (y/n)"
            if ($pushChoice -eq 'y' -or $pushChoice -eq 'yes') {
                git push -u origin main
                Write-Host "✓ 已推送到遠端倉庫" -ForegroundColor Green
            }
        } catch {
            Write-Host "✗ 遠端倉庫設定失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        $setupRemote = Read-Host "是否要設定遠端倉庫? (y/n)"
        if ($setupRemote -eq 'y' -or $setupRemote -eq 'yes') {
            $remoteUrl = Read-Host "請輸入遠端倉庫 URL"
            if ($remoteUrl) {
                try {
                    git remote add origin $remoteUrl
                    Write-Host "✓ 遠端倉庫已設定" -ForegroundColor Green
                    
                    $pushChoice = Read-Host "是否要推送到遠端倉庫? (y/n)"
                    if ($pushChoice -eq 'y' -or $pushChoice -eq 'yes') {
                        git push -u origin main
                        Write-Host "✓ 已推送到遠端倉庫" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "✗ 遠端倉庫設定失敗: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
    }
}

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "✓ Git 初始化設定完成！" -ForegroundColor Green
Write-Host ""
Write-Host "後續步驟:" -ForegroundColor Yellow
Write-Host "1. 複製 config.example.yaml 為 config.yaml 並填入實際密碼" -ForegroundColor Cyan
Write-Host "2. 複製 env.example 為 .env 並填入實際設定" -ForegroundColor Cyan
Write-Host "3. 將需要處理的檔案放入 input/ 資料夾" -ForegroundColor Cyan
Write-Host "4. 執行 python main.py 開始使用" -ForegroundColor Cyan
Write-Host ""
Write-Host "安全提醒:" -ForegroundColor Red
Write-Host "- 請勿將包含真實密碼的檔案提交到版本控制" -ForegroundColor Red
Write-Host "- 定期更新密碼和敏感資訊" -ForegroundColor Red
Write-Host "- 使用強密碼" -ForegroundColor Red
