# ID3840 電子保單題修正 Web 驗證紀錄

## 一、驗證範圍與結論

- 驗證題目：ID3840。
- 驗證網址：`http://127.0.0.1:5000`。
- 驗證結論：Web 驗證通過。
- 題幹、選項、答案、解析、subject 與 unit 均符合核准修正內容。
- 未發現亂碼、題幹截斷或選項污染。
- 驗證完成後已停止 Flask，並確認網址不再回應。

## 二、啟動環境

- 使用既有 repo 外臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`。
- 本次未重新安裝套件，未修改 `requirements.txt`。
- 以關閉 debug mode 與 reloader 的方式啟動 Flask：

  ```text
  C:\insurance_ai_runtime\web_validation_venv\Scripts\python.exe -c "import app; app.app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)"
  ```

- 未執行 `platform/app.py` 的 `__main__` 初始化區塊。

## 三、驗證方式

1. 啟動 Flask development server，確認 `http://127.0.0.1:5000` 可連線。
2. 使用既有快速登入帳號 Humble 建立 HTTP session；此操作只建立 session cookie。
3. 呼叫唯讀端點 `GET /api/explanation/3840`，回應 HTTP 200。
4. 將 Web 回傳的 question、options、correct_answer、explanation、unit 與受控腳本中的核准常數逐欄比較。
5. Web 端點未回傳 subject，另以 SQLite 唯讀查詢確認 subject。
6. 未進入 `/api/quiz/start`、`/api/quiz/submit` 或其他會寫入測驗紀錄的流程。
7. 停止 Flask 後，比對所有 SQLite 資料表與修正前備份；除 `questions.id=3840` 的核准修正外，其餘資料完全一致。

首次測試時，PowerShell 將內嵌中文預期值轉成問號，導致測試端預期字串失真；API 實際回傳資料正常。正式驗證改為直接載入受控腳本 `tools/apply_id3840_electronic_policy_correction.py` 的核准 Unicode 常數重新比對，所有欄位均通過。此現象不涉及正式資料或 Web 顯示內容變更。

## 四、ID3840 驗證結果

| 欄位 | 預期／Web 回傳內容 | 結果 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 唯讀交叉確認） |
| unit | 04 人身保險意義、功能、分類 | 通過 |
| 題幹 | 目前人身保險業所簽發的保單為 | 通過 |
| 選項1 | 僅提供紙本保單 | 通過 |
| 選項2 | 可利用網路投保來簽發電子保單 | 通過 |
| 選項3 | 不限紙本保單 | 通過 |
| 選項4 | 僅選項2、3為真 | 通過 |
| 正確答案 | `4` | 通過 |
| 解析 | 依保險業辦理電子商務相關規範，保險業可辦理符合規定之網路投保，並得依要保人指定方式交付紙本或電子保單。因此保單不限於紙本，且符合規範時可透過網路投保簽發電子保單，第2、3項為真，答案為第4項。電子保單仍須符合適用商品、身分驗證、要保人同意及其他相關規範。 | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 五、驗證後安全檢查

- `all_questions.json` SHA-256：`a3fcd9873de0c4545c203f7d610076b1da15d0bef282c708fcd989bf7ed9fd7f`。
- `platform/instance/insurance_exam.db` SHA-256：`de366c6d248a0aadf9f5c9e6475ae5ef8f4b1c5b2b3977835ebbb4391b500cf0`。
- `all_questions.json` 題數：4,128，最大 ID：4,141。
- SQLite `questions` 題數：4,141，最大 ID：4,141。
- SQLite `integrity_check`：`ok`。
- 與修正前備份比較，JSON 與 SQLite `questions` 的差異 ID 均僅為 3840。
- `quiz_sessions`、`user_answers`、`user_explanations`、`user_question_marks`、`users`、`weak_areas` 均與修正前備份一致。
- Flask 已停止，`http://127.0.0.1:5000` 已確認無法連線。
- 未修改 output JSON、platform 程式或其他未授權檔案。

## 六、結論

ID3840 已完成正式資料修正、JSON／SQLite 同步檢查及 Web 唯讀顯示驗證。題幹、四個選項、答案、解析、subject 與 unit 均正確，未發現亂碼、截斷或選項污染；Web 驗證通過。
