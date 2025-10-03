# Git 使用指南 - Excel ZIP Unlocker

## 📋 目錄
1. [Git 初始化](#git-初始化)
2. [安全設定](#安全設定)
3. [日常使用](#日常使用)
4. [安全檢查](#安全檢查)
5. [故障排除](#故障排除)

## 🚀 Git 初始化

### 自動化初始化 (推薦)

```bash
# 使用 Python 腳本
python setup_git.py

# 使用 PowerShell 腳本
.\setup_git.ps1

# 設定遠端倉庫
.\setup_git.ps1 -RemoteUrl "https://github.com/your-username/excel_zip_unlocker.git"
```

### 手動初始化

```bash
# 1. 初始化 Git 倉庫
git init

# 2. 設定使用者資訊
git config user.name "您的姓名"
git config user.email "您的郵箱"

# 3. 設定行尾符號處理
git config core.autocrlf true
git config core.safecrlf true

# 4. 添加檔案並提交
git add .
git commit -m "初始提交: Excel ZIP Unlocker 專案"

# 5. 設定遠端倉庫 (可選)
git remote add origin https://github.com/your-username/excel_zip_unlocker.git
git push -u origin main
```

## 🔒 安全設定

### 重要安全原則

⚠️ **絕對不要將以下檔案提交到版本控制：**

- **密碼檔案**: `config/config.yaml`
- **環境變數**: `.env`, `.env.*`
- **處理檔案**: `*.xlsx`, `*.xls`, `*.zip`, `*.rar`
- **日誌檔案**: `logs/*.log`
- **報表檔案**: `report/*.yaml`, `report/*.json`

### 設定範例檔案

```bash
# 複製範例檔案
copy config\config.example.yaml config\config.yaml
copy env.example .env

# 編輯實際設定
notepad config\config.yaml
notepad .env
```

### 驗證忽略規則

```bash
# 檢查 Git 狀態
git status

# 確認敏感檔案不會出現在待提交清單中
git ls-files | findstr /i "config.yaml .env *.xlsx *.zip"
```

## 📝 日常使用

### 基本工作流程

```bash
# 1. 檢查狀態
git status

# 2. 添加檔案 (只會添加非敏感檔案)
git add .

# 3. 提交變更
git commit -m "描述變更內容"

# 4. 推送到遠端 (如果已設定)
git push origin main
```

### 常用命令

```bash
# 查看變更
git diff

# 查看提交歷史
git log --oneline

# 建立分支
git checkout -b feature/new-feature

# 合併分支
git checkout main
git merge feature/new-feature

# 刪除分支
git branch -d feature/new-feature
```

### 提交訊息規範

```bash
# 功能新增
git commit -m "feat: 新增 GUI 介面"

# 錯誤修復
git commit -m "fix: 修復密碼驗證問題"

# 文件更新
git commit -m "docs: 更新 README.md"

# 設定變更
git commit -m "config: 更新預設設定"

# 重構
git commit -m "refactor: 重構檔案處理邏輯"
```

## 🔍 安全檢查

### 使用安全檢查腳本

```bash
# 執行安全檢查
python check_git_security.py
```

### 手動檢查項目

1. **檢查 .gitignore 檔案**
   ```bash
   type .gitignore
   ```

2. **檢查已追蹤檔案**
   ```bash
   git ls-files | findstr /i "config.yaml .env *.xlsx *.zip"
   ```

3. **檢查暫存區檔案**
   ```bash
   git diff --cached --name-only
   ```

4. **檢查工作目錄**
   ```bash
   dir /s *.xlsx *.zip *.rar
   ```

### Git 鉤子檢查

```bash
# 檢查 pre-commit 鉤子
type .git\hooks\pre-commit
```

## 🛠️ 故障排除

### 常見問題

#### 1. 意外提交敏感檔案

```bash
# 從 Git 歷史中移除檔案
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/config.yaml" \
  --prune-empty --tag-name-filter cat -- --all

# 強制推送 (謹慎使用)
git push origin --force --all
```

#### 2. .gitignore 不生效

```bash
# 清除快取並重新添加
git rm -r --cached .
git add .
git commit -m "更新 .gitignore 規則"
```

#### 3. 行尾符號問題

```bash
# 設定行尾符號處理
git config core.autocrlf true
git config core.safecrlf true

# 重新規範化檔案
git add --renormalize .
git commit -m "規範化行尾符號"
```

#### 4. 大檔案問題

```bash
# 安裝 Git LFS
git lfs install

# 追蹤大檔案類型
git lfs track "*.zip"
git lfs track "*.rar"
git lfs track "*.xlsx"

# 提交 .gitattributes
git add .gitattributes
git commit -m "設定 Git LFS"
```

### 緊急情況處理

#### 如果敏感檔案已提交

1. **立即處理**:
   ```bash
   # 停止所有 Git 操作
   git reset --hard HEAD~1
   ```

2. **清理歷史**:
   ```bash
   # 使用 BFG Repo-Cleaner (推薦)
   java -jar bfg.jar --delete-files config.yaml
   ```

3. **通知團隊**:
   - 立即通知所有協作者
   - 要求他們重新克隆倉庫
   - 更新所有密碼和敏感資訊

## 📚 最佳實踐

### 1. 定期安全檢查
```bash
# 每週執行安全檢查
python check_git_security.py
```

### 2. 使用分支開發
```bash
# 建立功能分支
git checkout -b feature/new-feature
# 開發完成後合併
git checkout main
git merge feature/new-feature
```

### 3. 定期備份
```bash
# 建立備份分支
git checkout -b backup/$(date +%Y%m%d)
git push origin backup/$(date +%Y%m%d)
```

### 4. 團隊協作
- 使用 Pull Request 進行程式碼審查
- 設定分支保護規則
- 定期更新依賴套件

## 🔗 相關資源

- [Git 官方文件](https://git-scm.com/doc)
- [GitHub 安全最佳實踐](https://docs.github.com/en/code-security)
- [Git LFS 文件](https://git-lfs.github.io/)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

**記住**: 安全第一！永遠不要將敏感資訊提交到版本控制系統。
