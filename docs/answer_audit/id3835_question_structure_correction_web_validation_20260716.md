# ID3835 題目結構修正 Web 驗證紀錄

## 一、驗證範圍與結論

- 驗證題目：ID3835。
- 驗證網址：`http://127.0.0.1:5000`。
- 驗證結論：Web 驗證通過。
- 題幹、選項、答案、解析顯示、subject 與 unit 均符合核准修正內容。
- 未發現亂碼、題幹截斷或選項污染。
- 驗證完成後已停止 Flask，並確認本次伺服器不再監聽連接埠 5000。

## 二、啟動環境

- 使用既有 repo 外臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`。
- 本次未重新安裝套件，未修改 `requirements.txt`。
- 使用 Flask CLI 啟動既有 app，關閉 debug mode 與 reloader：

  ```text
  C:\insurance_ai_runtime\web_validation_venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
  ```

- 未執行 `platform/app.py` 的 `__main__` 初始化區塊。

## 三、驗證方式

1. 啟動 Flask development server，確認 `http://127.0.0.1:5000/login` 回應 HTTP 200。
2. 使用既有快速登入帳號 Humble 建立 HTTP session；此操作只建立 session cookie。
3. 呼叫唯讀端點 `GET /api/explanation/3835`，回應 HTTP 200。
4. 將 Web 回傳的 question、options、correct_answer、explanation 與 unit 逐欄比對。
5. Web 端點未回傳 subject，另以 SQLite 唯讀查詢交叉確認 subject。
6. 未進入 `/api/quiz/start`、`/api/quiz/submit` 或其他會寫入測驗紀錄的流程。
7. 停止 Flask 後，比對 SQLite 正式檔與修正前備份；除 `questions.id=3835` 的核准修正外，其餘資料完全一致。

首次以 `python -c` 配合 Windows `Start-Process` 啟動時，內嵌程式碼被參數解析拆開而產生 `SyntaxError`；該次 Flask 並未啟動，也未修改任何資料。其後改用同一既有 venv 的 Flask CLI 正常啟動並完成驗證。

## 四、ID3835 驗證結果

| 欄位 | 預期／Web 回傳內容 | 結果 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 唯讀交叉確認） |
| unit | 04 人身保險意義、功能、分類 | 通過 |
| 題幹 | 人身保險的意義，就是由下列何者出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活？ | 通過 |
| 選項1 | 許多窮苦的人們 | 通過 |
| 選項2 | 少數的社會熱心人士 | 通過 |
| 選項3 | 千千萬萬的人 | 通過 |
| 選項4 | 保險公司的員工 | 通過 |
| 正確答案 | `3` | 通過 |
| SQLite 解析 | 空字串 | 通過 |
| Web 解析顯示 | 此題目尚無詳細解說,建議複習相關章節。 | 通過（既有空解析 fallback） |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 五、驗證後安全檢查

- `all_questions.json` SHA-256：`3fa735f358d24e86fab86348d12d54ca17f8be53b902bbfc5763df07f5907c56`。
- `platform/instance/insurance_exam.db` SHA-256：`57488a8fb4f638dc36f5aa7eeaee9dce423dff692b3c1497b8238d1acac7c5a7`。
- `all_questions.json` 題數：4,128，最大 ID：4,141。
- SQLite `questions` 題數：4,141，最大 ID：4,141。
- SQLite `integrity_check`：`ok`。
- 與修正前備份比較，JSON 與 SQLite `questions` 的差異 ID 均僅為 3835。
- `quiz_sessions`、`user_answers`、`user_explanations`、`user_question_marks`、`users`、`weak_areas` 均與修正前備份一致。
- Flask 已停止，本次伺服器不再監聽 `127.0.0.1:5000`。
- 未修改 output JSON、platform 程式或其他未授權檔案。

## 六、結論

ID3835 已完成正式資料修正、JSON／SQLite 同步檢查及 Web 唯讀顯示驗證。題幹、四個選項、答案、解析顯示、subject 與 unit 均正確，未發現亂碼、截斷或選項污染；Web 驗證通過。
