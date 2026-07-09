# 保險考試線上練習系統

一個強大的 Flask Web 應用，用於保險考試題目練習、OCR 識別和 AI 生成題目。

## 功能特性

✨ **Web 練習系統** - 線上做題、記錄進度  
🤖 **AI 題目生成** - 使用 Google Gemini API 自動生成題目  
📄 **OCR 識別** - 自動提取 PDF/圖片中的文本  
📊 **數據分析** - 統計答題情況和薄弱章節  

## 快速開始

### Windows

```bash
# 1. 進入項目
cd C:\insurance_ai

# 2. 激活虛擬環境
venv\Scripts\activate

# 3. 進入 platform
cd platform

# 4. 啟動應用
python app.py

# 5. 打開瀏覽器
# http://localhost:5000
```

### Mac

```bash
# 1. 進入項目
cd ~/insurance_ai

# 2. 創建虛擬環境（首次）
python3 -m venv venv

# 3. 激活虛擬環境
source venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 進入 platform
cd platform

# 6. 啟動應用
python app.py

# 7. 打開瀏覽器
# http://localhost:5000
```

## 環境配置

1. 複製 `.env.example` 為 `.env`
2. 填入你的 **Gemini API Key**
3. 配置 `INPUT_FOLDER` 和 `OUTPUT_FOLDER` 路徑

## 項目結構