# 保險題庫專案資料夾關聯盤點收版文件

- 盤點日期：2026-07-16
- 正式主專案：`C:\insurance_ai`
- 關聯資料夾：`D:\insurance-quiz`

## 收版結論

1. `C:\insurance_ai` 是保險題庫的正式主專案，包含題庫處理流程、Flask 平台、SQLite 資料庫、templates、static 與相關工具。
2. `D:\insurance-quiz` 是 React/Vite 前端原型或舊版前端，採用 React、Vite、Tailwind CSS 與 Dexie（IndexedDB）。
3. 兩者目前沒有直接程式引用；未發現 C 槽啟動或整合 D 槽，也未發現 D 槽呼叫 C 槽 API、讀取 C 槽路徑或正式題庫檔案。
4. `D:\insurance-quiz` 目前只有 10 題內建範例資料，來源為 `src/data/sampleQuestions.js`，未連接 `C:\insurance_ai` 的正式題庫、`output/question_bank.json` 或 Flask/SQLite 資料來源。
5. 目前不建議刪除 `D:\insurance-quiz`，建議先封存；在封存或後續處置前，仍應檢查瀏覽器 IndexedDB 是否留有重要資料。
6. 後續 Codex 工作目錄預設使用 `C:\insurance_ai`，並以該目錄作為正式程式、題庫資料與文件維護的唯一主要來源。

## 實際使用系統確認

使用者已確認以下事實：

1. 瀏覽器歷史紀錄搜尋到的題庫系統網址是 `http://localhost:5000`。
2. 平常使用的啟動命令是：

   ```powershell
   cd C:\insurance_ai\platform
   python app.py
   ```

3. 因此，目前實際使用的題庫系統可確認為 `C:\insurance_ai\platform` 的 Flask 系統。
4. `D:\insurance-quiz` 的 Vite 預設網址為 `http://localhost:5173`，且目前未連接正式題庫或 Flask API，因此可確認不是目前實際使用的系統。
5. 先前提到的 `localhost:5001` 僅屬可能記憶，不列為已確認事實，也不作為本次角色判斷依據。

## D 槽值得保留的設計概念

- 精熟題自動排除：一般抽題時排除已標記精熟的題目。
- 收藏答對三次自動轉精熟：將重複答對作為學習狀態自動提升的條件。
- 正式題數／配分／時間：依科目設定正式測驗的題數、每題配分與建議或限制時間。
- 離線 IndexedDB 模式：讓題庫與個人進度可在純瀏覽器環境離線保存。

上述項目應保留為產品與需求設計參考，不代表應直接移植現有 React/Dexie 程式碼。

## 後續整合原則

若未來要把 D 槽功能合併至 C 槽，應先將有價值的行為、規則、資料模型與使用情境整理成需求規格，再依 `C:\insurance_ai` 的正式架構重新實作。除非已決定進行完整前端重構，否則不應直接混用 Flask templates/static 與 React/Vite 兩套前端，也不應讓 SQLite 與 IndexedDB 同時成為互不一致的正式資料來源。

建議整合順序：

1. 確認需求及驗收條件。
2. 確認正式資料來源及資料同步責任。
3. 在 C 槽現有平台中確認是否已有同等功能。
4. 僅補入確定缺少且仍有價值的功能。
5. 完成驗證後，再評估 D 槽的長期封存或移除時機。

## 工作目錄約定

後續 Codex 處理保險題庫相關工作時，若沒有其他明確指示，預設工作目錄為：

```text
C:\insurance_ai
```

`D:\insurance-quiz` 僅作為前端原型、舊版實作與設計參考來源，不視為正式主專案。

