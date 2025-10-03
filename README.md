# 📦 Excel ZIP Unlocker

一個強大的批次處理工具，專門用於自動解壓縮和解密受密碼保護的 Excel 和壓縮檔案。

## 🎯 專案特色

- **自動解壓縮**：支援 ZIP 與 RAR 檔案，處理受密碼保護的壓縮檔
- **自動移除 Excel 密碼**：透過 msoffcrypto-tool 解密受保護的 Excel 檔案
- **批次處理**：自動處理 input/ 資料夾內的所有檔案
- **多組密碼管理**：支援 config.yaml 中設定多組密碼，逐一嘗試解鎖
- **三種處理模式**：
  - 自動檢測：處理所有支援的檔案類型
  - 批次密碼解壓縮：只處理 ZIP/RAR 檔案
  - 批次密碼移除 Excel：只處理 Excel 檔案
- **完整日誌記錄**：所有執行細節輸出到 logs/，具備保留策略
- **詳細報表**：每次執行產生處理結果摘要報表
- **互動式選單**：提供友善的命令行介面
- **跨平臺支援**：主要支援 Windows，可打包成 EXE 檔案

## 📁 專案結構

```
excel_zip_unlocker/
├── 📄 main.py                    # 主程式 (命令行版本)
├── 📄 run.ps1                    # PowerShell 執行腳本
├── 📄 setup_git.ps1              # Git 初始化腳本 (PowerShell)
├── 📋 requirements.txt           # Python 依賴套件
├── 📄 .gitignore                 # Git 忽略規則
├── 📄 .gitattributes             # Git 檔案屬性
├── 📄 env.example                # 環境變數範例
├── 📁 src/                       # 核心模組和腳本
│   ├── 📄 logger_manager.py     # 日誌管理系統
│   ├── 📄 file_processor.py      # 檔案處理核心
│   ├── 📄 report_generator.py   # 報表生成系統
│   ├── 📄 build.py              # 打包腳本
│   ├── 📄 check_git_security.py # Git 安全檢查腳本
│   └── 📄 setup_git.py          # Git 初始化腳本 (Python)
├── 📁 input/                     # 待處理檔案
├── 📁 output/                    # 處理結果
├── 📁 logs/                      # 執行日誌 (自動產生)
├── 📁 report/                    # 處理報表
├── 📁 config/                    # 設定檔
│   ├── 📄 config.yaml           # 主設定檔 (包含密碼)
│   └── 📄 config.example.yaml   # 設定檔範例
└── 📁 tools/                     # 外部工具 (unrar.exe, 7z.exe)
```

## 🚀 快速開始

### 1. 環境需求

- Python 3.8 或更高版本
- Windows 10/11 (主要支援平台)
- Git (可選，用於版本控制)

### 2. Git 初始化設定 (可選)

如果您要使用 Git 進行版本控制，可以執行以下步驟：

#### 使用自動化腳本 (推薦)
```bash
# PowerShell 版本
.\setup_git.ps1

# Python 版本 (在 src 資料夾中)
python src/setup_git.py

# 設定遠端倉庫
.\setup_git.ps1 -RemoteUrl "https://github.com/your-username/excel_zip_unlocker.git"
```

#### 手動設定
```bash
# 初始化 Git 倉庫
git init

# 設定使用者資訊
git config user.name "您的姓名"
git config user.email "您的郵箱"

# 添加檔案並提交
git add .
git commit -m "初始提交"
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 4. 準備檔案

將需要處理的檔案放入 `input/` 資料夾中。

### 5. 執行程式

#### 使用 PowerShell 腳本 (推薦)
```bash
# 雙擊執行
run.ps1

# 或使用 PowerShell
.\run.ps1
```

#### 使用 Python 直接執行
```bash
# 命令行版本
python main.py

# 指定參數
python main.py -i custom_input -o custom_output -c custom_config.yaml
```

## 🔒 Git 安全設定

### 重要安全提醒

⚠️ **請勿將敏感檔案提交到版本控制系統！**

本專案已設定完整的 Git 安全配置，自動排除以下敏感檔案：

- **密碼檔案**：`config/config.yaml`、`*.passwords`、`*.keys`
- **環境變數**：`.env`、`.env.*`
- **處理檔案**：`*.xlsx`、`*.xls`、`*.zip`、`*.rar`
- **日誌檔案**：`logs/*.log`
- **報表檔案**：`report/*.yaml`、`report/*.json`

### Git 忽略規則

專案包含以下 Git 設定檔案：

- **`.gitignore`**：排除敏感檔案和不需要版本控制的檔案
- **`.gitattributes`**：設定檔案屬性和處理方式
- **`env.example`**：環境變數範例檔案
- **`config/config.example.yaml`**：設定檔範例

### 安全使用步驟

1. **複製範例檔案**：
   ```bash
   copy env.example .env
   copy config\config.example.yaml config\config.yaml
   ```

2. **填入實際設定**：
   - 編輯 `config/config.yaml` 填入真實密碼
   - 編輯 `.env` 填入實際環境變數

3. **驗證忽略規則**：
   ```bash
   git status
   # 確認敏感檔案不會出現在待提交清單中
   ```

4. **使用 Git 鉤子**：
   - 專案已設定 `pre-commit` 鉤子
   - 自動檢查並阻止提交敏感檔案

### Git 工作流程

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

## ⚙️ 設定說明

### config/config.yaml 設定檔

```yaml
# 日誌管理策略
log_policy:
  keep_days: 7          # 日誌最多保留 7 天
  keep_files: 20        # 或最多保留 20 個檔案
  clean_on_start: true # 啟動時清理舊日誌
  log_level: "INFO"     # 日誌等級

# 密碼清單 - 程式會依序嘗試這些密碼
passwords:
  - "123456"
  - "password123"
  - "company2025"
  - "admin"

# 檔案處理設定
file_settings:
  supported_extensions:
    excel: [".xlsx", ".xls", ".xlsm", ".xlsb"]
    zip: [".zip"]
    rar: [".rar"]
  max_file_size: 500    # 檔案大小限制 (MB)
  timeout: 300         # 處理超時時間 (秒)

# 報表設定
report_settings:
  format: "yaml"       # yaml, json, csv
  include_details: true
  include_statistics: true
```

## 📖 使用方式

### 命令行版本

```bash
# 基本使用
python main.py

# 指定處理模式
python main.py -m extract    # 只處理壓縮檔案
python main.py -m excel      # 只處理 Excel 檔案
python main.py -m auto       # 自動檢測 (預設)

# 指定輸入輸出資料夾
python main.py -i my_input -o my_output

# 使用自訂設定檔
python main.py -c my_config.yaml

# 檢查依賴套件
python main.py --check-deps

# 顯示詳細輸出
python main.py -v
```

### 互動式選單

使用 `run.ps1` 腳本會提供友善的互動式選單：

1. **自動檢測** - 處理所有支援的檔案類型
2. **批次密碼解壓縮** - 只處理 ZIP/RAR 檔案
3. **批次密碼移除 Excel** - 只處理 Excel 檔案
4. **檢查依賴套件** - 驗證環境設定
5. **退出** - 結束程式

### 處理流程

1. 執行 `python main.py` 或使用 `run.ps1`
2. 選擇處理模式
3. 程式會自動處理 `input/` 資料夾中的檔案
4. 處理結果會輸出到 `output/` 資料夾
5. 查看 `logs/` 和 `report/` 資料夾了解處理詳情

## 🔧 支援的檔案類型

### Excel 檔案
- `.xlsx` - Excel 2007+ 格式
- `.xls` - Excel 97-2003 格式
- `.xlsm` - 包含巨集的 Excel 檔案
- `.xlsb` - Excel 二進位格式

### 壓縮檔案
- `.zip` - ZIP 壓縮格式
- `.rar` - RAR 壓縮格式

## 📊 輸出說明

### 處理結果
- **成功檔案**：解密/解壓後的檔案會儲存在 `output/` 資料夾
- **失敗檔案**：會在日誌中記錄失敗原因
- **跳過檔案**：不支援的檔案類型會被跳過

### 日誌檔案
- 位置：`logs/` 資料夾
- 格式：`unlocker_YYYYMMDD_HHMMSS.log`
- 內容：詳細的處理過程和錯誤資訊

### 報表檔案
- 位置：`report/` 資料夾
- 格式：YAML/JSON/CSV (可設定)
- 內容：處理結果統計和詳細資訊

## 🛠️ 進階功能

### 外部工具設定

在 `tools/` 資料夾中放置：
- `unrar.exe` - RAR 解壓工具
- `7z.exe` - 7-Zip 工具 (備用)

### 自訂密碼清單

在 `config/config.yaml` 中修改 `passwords` 區段：

```yaml
passwords:
  - "your_password1"
  - "your_password2"
  - "common_passwords"
```

### 報表格式選擇

支援三種報表格式：
- **YAML**：人類可讀，結構清晰
- **JSON**：機器可讀，便於程式處理
- **CSV**：表格格式，便於 Excel 開啟

## 📦 打包成 EXE

### 使用打包腳本

```bash
python src/build.py
```

打包完成後，可執行檔案會位於 `dist/` 目錄中：
- `excel_zip_unlocker.exe` - 命令行版本

### 手動打包

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包命令行版本
pyinstaller --onefile --console main.py
```

## 🔍 故障排除

### 常見問題

1. **密碼錯誤**
   - 檢查 `config/config.yaml` 中的密碼設定
   - 確認密碼大小寫正確

2. **檔案無法處理**
   - 檢查檔案是否損壞
   - 確認檔案格式是否支援
   - 檢查檔案大小是否超過限制

3. **RAR 檔案無法解壓**
   - 確認 `tools/unrar.exe` 存在
   - 檢查 RAR 檔案版本是否支援

4. **權限問題**
   - 以管理員身份執行
   - 檢查資料夾讀寫權限

### 日誌分析

查看 `logs/` 資料夾中的日誌檔案，尋找錯誤訊息：
- `ERROR` - 嚴重錯誤
- `WARNING` - 警告訊息
- `INFO` - 一般資訊

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設定

```bash
# 複製專案
git clone <repository-url>
cd excel_zip_unlocker

# 建立虛擬環境
python -m venv venv
venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 執行測試
python main.py --check-deps
```

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 LICENSE 檔案。

## 📞 支援與聯絡

如有問題或建議，請透過以下方式聯絡：

- 提交 GitHub Issue
- 發送電子郵件至專案維護者

---

**Excel ZIP Unlocker** - 讓檔案解密變得簡單高效！ 🚀
# excel_zip_unlocker
