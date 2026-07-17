# JY unit03 Q47 / ID4138 Web 顯示驗證紀錄

## 一、驗證範圍與結論

- 驗證題目：ID4138（`MISS-20260716-0013` / JY P.91 Q47）。
- 驗證網址：`http://127.0.0.1:5000`。
- 驗證結論：Web 驗證通過。
- 題幹、選項、答案、解析、subject 與 unit 均符合核准補題內容。
- 未發現亂碼、題幹截斷、選項缺漏或選項污染。
- 驗證完成後 Flask 已停止，port 5000 已確認未再監聽。

## 二、啟動環境

- 使用既有且位於 repository 外的臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`。
- 本次未重新安裝或新增任何套件。
- 使用 venv Python 關閉 debug mode 與 reloader 啟動既有 Flask 應用：

  ```text
  C:\insurance_ai_runtime\web_validation_venv\Scripts\python.exe -c "import app; app.app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)"
  ```

- 本次未執行 `platform/app.py` 的 `__main__` 初始化區塊。

## 三、驗證方式

1. 啟動 Flask development server，確認 `http://127.0.0.1:5000` 可連線。
2. 使用既有快速登入帳號 Humble 建立 HTTP session。
3. 呼叫唯讀端點 `GET /api/explanation/4138`，回應 HTTP 200。
4. 將端點回傳的 question、options、correct_answer、explanation 與 unit 逐欄精確比較。
5. 因端點未回傳 subject，另以 SQLite 唯讀查詢交叉確認 subject 與 unit。
6. 未進入 `/api/quiz/start`、`/api/quiz/submit` 或其他會寫入測驗紀錄的流程。
7. 停止 Flask 後，比對 `all_questions.json` 與正式 SQLite 的 SHA-256、題數及完整性。

## 四、ID4138 驗證結果

| 欄位 | 預期／回傳內容 | 結果 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 唯讀交叉確認） |
| unit | 03 保險費架構、解約金、準備金、保單紅利 | 通過 |
| 題幹 | 保單紅利支付的方法有？ | 通過 |
| options | BCD、ACD、ABCD、ABC | 通過 |
| correct_answer | `3` | 通過 |
| explanation | 保單紅利支付方法包括購買增額繳清金額、積存方法、抵繳保費及現金支付方法，因此答案為ABCD。 | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項缺漏、無選項污染 | 通過 |

## 五、驗證後資料安全檢查

- `all_questions.json` SHA-256：`d63619fdf5719ce0f478b8f6e7970082335d0e479dff92a5bbba883b45f84af6`，與啟動前相同。
- `platform/instance/insurance_exam.db` SHA-256：`9ef0b450087c7733c1a0333bd9470ef5ae4e52b88299bdd6e957862235dc9188`，與啟動前相同。
- SQLite `questions` 題數：4,138，未變。
- SQLite `PRAGMA integrity_check`：`ok`。
- Flask 已停止，port 5000 未再監聽。
- 驗證前後 Git 狀態皆為 `## main...origin/main`；除本驗證文件外，未產生 repository 變更。

## 六、收版判定

ID4138 已完成 JSON／SQLite 同步補入、資料一致性驗證及 Web 唯讀顯示驗證。題幹、選項、答案、解析、subject 與 unit 均正確，且無亂碼、截斷或選項污染；Web 驗證通過。
