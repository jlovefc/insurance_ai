# ID 4136、4137 Web 顯示驗證紀錄

## 一、驗證範圍與結論

- 驗證題目：ID 4136、ID 4137。
- 驗證網址：`http://127.0.0.1:5000`。
- 驗證結論：兩題 Web 驗證通過。
- 題幹、選項、答案、解析、subject 及 unit 均符合核准補題內容。
- 未發現亂碼、題幹截斷、選項缺漏或選項污染。
- Flask 驗證完成後已停止，port 5000 已確認未再監聽。

## 二、啟動環境摘要

- 系統既有 Python：Python 3.12。
- 因系統 Python 未安裝 Flask，依使用者授權在 repo 外建立臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`。
- 依 `C:\insurance_ai\requirements.txt` 完整安裝套件，安裝成功；未修改 `requirements.txt`，未安裝清單外套件。
- venv、套件、快取及執行環境均位於 Git 追蹤範圍外，未加入 repository。
- 使用臨時 venv Python 啟動 Flask，關閉 debug mode 與 reloader：

  ```text
  C:\insurance_ai_runtime\web_validation_venv\Scripts\python.exe -c "import app; app.app.run(debug=False, host='127.0.0.1', port=5000)"
  ```

- 本次未執行 `platform/app.py` 的 `__main__` 初始化區塊，避免 `db.create_all()` 或預設帳號初始化造成不必要寫入。

## 三、驗證方式

1. 啟動 Flask development server，確認 `http://127.0.0.1:5000` 可連線。
2. 使用既有快速登入帳號 Humble 建立 HTTP session；此步只建立 session cookie，不修改題庫。
3. 分別呼叫唯讀端點：
   - `GET /api/explanation/4136`
   - `GET /api/explanation/4137`
4. 兩個端點均回應 HTTP 200。
5. 將回傳的 question、options、correct_answer、explanation、unit 與核准內容逐欄精確比較。
6. Web 端點未回傳 subject，因此另以 SQLite 唯讀查詢交叉確認兩題 subject。
7. 未進入 `/api/quiz/start`、`/api/quiz/submit` 或其他會寫入測驗紀錄的流程。
8. 停止 Flask 後，比對 `all_questions.json` 與正式 SQLite 的 SHA-256、題數及完整性。

## 四、ID 4136 驗證結果

| 欄位 | 預期／回傳內容 | 結果 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 唯讀交叉確認） |
| unit | 03 保險費架構、解約金、準備金、保單紅利 | 通過 |
| 題幹 | 若預定死亡率降低，定期保險的保險費就會？ | 通過 |
| 選項 | 一樣、不一定、便宜、貴 | 通過 |
| 正確答案 | `3` | 通過 |
| 解析 | 其他條件不變時，預定死亡率降低代表預期死亡給付成本下降，定期保險保費因而降低。 | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 五、ID 4137 驗證結果

| 欄位 | 預期／回傳內容 | 結果 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 唯讀交叉確認） |
| unit | 03 保險費架構、解約金、準備金、保單紅利 | 通過 |
| 題幹 | 一萬名30歲的男性各投保100萬的死亡保險（保險期間1年），若生命表顯示30歲男性死亡率為千分之二，請問每人該付多少純保費？ | 通過 |
| 選項 | 1仟元、2仟元、3仟元、4仟元 | 通過 |
| 正確答案 | `2` | 通過 |
| 解析 | `10000 × 2/1000 = 20人`；`20 × 1000000 / 10000 = 2000` | 通過 |
| 中文顯示 | 無亂碼 | 通過 |
| 題目結構 | 無截斷、無選項污染 | 通過 |

## 六、驗證後資料安全檢查

- `all_questions.json` SHA-256：`96299b21a8fd33f99c722dd8bc3b6ad1241ee558f027083fef1abccf940653a6`，與啟動前相同。
- `platform/instance/insurance_exam.db` SHA-256：`482d46b4165c24ec078dd7783ff52a5366cf2b9e43d0f436943523f5c6dc6cc7`，與啟動前相同。
- SQLite `questions` 題數：4,137，未變。
- SQLite `integrity_check`：`ok`。
- 未進入會新增 `quiz_sessions` 的測驗流程。
- 驗證前後 Git 狀態皆為 `## main...origin/main`；除本驗證文件外，未產生 repository 變更。

## 七、收版判定

ID 4136、4137 已完成資料層補入、JSON／SQLite 同步驗證及 Web 唯讀顯示驗證。兩題的題幹、選項、答案、解析、subject 與 unit 皆正確，無亂碼、截斷或選項污染；本次 Web 驗證通過。
