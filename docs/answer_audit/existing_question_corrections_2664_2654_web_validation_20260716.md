# ID2664 / ID2654 既有題修正 Web 驗證紀錄

## 一、驗證範圍與結論

- 驗證題目：ID2664、ID2654。
- 驗證網址：`http://127.0.0.1:5000`。
- 驗證結論：兩題 Web 驗證通過。
- 題幹、選項、答案、解析、subject 與 unit 均符合核准修正內容。
- 未發現亂碼、題幹截斷或選項污染。
- 驗證完成後已停止 Flask，port 5000 已確認未再監聽。

## 二、啟動環境

- 使用既有 repo 外臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`。
- venv 內 Flask 版本：3.1.3。
- 本次未重新安裝套件，未修改 `requirements.txt`。
- 使用以下方式關閉 debug mode 與 reloader 啟動 Flask：

  ```text
  C:\insurance_ai_runtime\web_validation_venv\Scripts\python.exe -c "import app; app.app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)"
  ```

- 未執行 `platform/app.py` 的 `__main__` 初始化區塊。

## 三、驗證方式

1. 啟動 Flask development server，並確認 `http://127.0.0.1:5000` 可連線。
2. 使用既有快速登入帳號 Humble 建立 HTTP session；此操作只建立 session cookie。
3. 呼叫唯讀端點：
   - `GET /api/explanation/2664`
   - `GET /api/explanation/2654`
4. 兩個端點均回應 HTTP 200。
5. 將 Web 回傳的 question、options、correct_answer、explanation、unit 與核准內容逐欄比較。
6. Web 端點未回傳 subject，另以 SQLite 唯讀查詢確認 subject。
7. 未進入 `/api/quiz/start`、`/api/quiz/submit` 或其他會寫入測驗紀錄的流程。
8. 停止 Flask 後再次檢查正式檔 SHA-256、SQLite 題數、完整性及 Git 狀態。

## 四、ID2664 驗證結果

| 欄位 | 預期／Web 回傳內容 | 結果 |
|---|---|---|
| subject | 保險實務 | 通過（SQLite 唯讀交叉確認） |
| unit | 第四章 人身保險的構造 | 通過 |
| 題幹 | 保險公司對於責任準備金之提存方式往往採取較穩健的作法，採比保單價值準備金 A 較低之預定利率；B 較高之預定利率；C 較低之預定死亡率；D 較高之預定死亡率 | 通過 |
| 選項 | BC、BD、AD、AC | 通過 |
| 正確答案 | `3` | 通過 |
| 解析 | 保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率亦使死亡給付成本估計較高，因此答案為AD。 | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 五、ID2654 驗證結果

| 欄位 | 預期／Web 回傳內容 | 結果 |
|---|---|---|
| subject | 保險實務 | 通過（SQLite 唯讀交叉確認） |
| unit | 第四章 人身保險的構造 | 通過 |
| 題幹 | 如要保人選擇以儲存生息之方式給付紅利之後，當被保險人死亡時，保險人所給付之保險金額較原保險金額為 | 通過 |
| 選項 | 高、不一定、一樣、低 | 通過 |
| 正確答案 | `3` | 通過 |
| 解析 | 選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。 | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 六、驗證後安全檢查

- `all_questions.json` SHA-256：`781b400d65ab9a7aeba8d66373219648a6405972b4685dc8137d54645e0376d9`，與啟動前相同。
- `platform/instance/insurance_exam.db` SHA-256：`bee7587e4b89c3347931105d68d6dc57ab03fcb1b81d92a0ccf748d02543870a`，與啟動前相同。
- SQLite `questions` 題數：4,137，未變。
- SQLite `integrity_check`：`ok`。
- 驗證前後 Git 狀態均為 `## main...origin/main`；除本驗證文件外，未產生 repository 變更。
- Flask 已停止，port 5000 未再監聽。

## 七、結論

ID2664、ID2654 已完成正式資料修正、JSON／SQLite 同步檢查及 Web 唯讀顯示驗證。兩題的題幹、選項、答案、解析、subject 與 unit 均正確，未發現亂碼、截斷或選項污染；Web 驗證通過。
