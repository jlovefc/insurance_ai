# JY unit03 Q35／Q36（ID4139／4140）Web 驗證收版

## 一、驗證範圍與環境

- 驗證題目：ID4139、ID4140。
- 本機網址：`http://127.0.0.1:5000`。
- Python 環境：`C:\insurance_ai_runtime\web_validation_venv`。
- Flask 以 `debug=False`、`use_reloader=False` 啟動。
- 驗證完成後 Flask 已停止。
- 未重新安裝套件，未修改 platform 程式。

## 二、驗證方式

1. 以本機 Web 畫面登入既有 `Humble` 驗證帳號。
2. Dashboard 顯示題庫題數為 4,140。
3. 使用同一登入 session 對 `GET /api/explanation/4139` 與 `GET /api/explanation/4140` 進行唯讀驗證；兩個回應皆為 HTTP 200。
4. 將 Web 回應中的題幹、選項、答案、解析及 unit 與核准內容逐欄核對。
5. subject 雖未由此 API 回傳，另以正式 SQLite 對應記錄核對。
6. 未進入 `/api/quiz/start` 或 `/api/quiz/submit`，未建立測驗紀錄。

## 三、ID4139 驗證結果

| 欄位 | 預期與實際結果 | 結論 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 對應記錄） |
| unit | 03 保險費架構、解約金、準備金、保單紅利 | 通過 |
| content | 以「依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定」開頭，完整包含保險期間、純保險費門檻及最低責任準備金問句 | 通過 |
| options | 二十年滿期生死合險修正制；二十五年滿期生死合險修正制；二十年繳費終身保險修正制；一年定期修正制 | 通過 |
| correct_answer | `2` | 通過 |
| explanation | 完整說明民國88年適用條件、純保險費門檻、二十五年滿期生死合險修正制及歷史規定語境 | 通過 |
| 顯示品質 | 無亂碼、截斷或選項污染 | 通過 |

## 四、ID4140 驗證結果

| 欄位 | 預期與實際結果 | 結論 |
|---|---|---|
| subject | B 保險實務-分類 | 通過（SQLite 對應記錄） |
| unit | 03 保險費架構、解約金、準備金、保單紅利 | 通過 |
| content | 以「依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定」開頭，完整包含保險期間、純保險費門檻及最低責任準備金問句 | 通過 |
| options | 二十年滿期生死合險修正制；二十五年滿期生死合險修正制；二十年繳費終身保險修正制；一年定期修正制 | 通過 |
| correct_answer | `3` | 通過 |
| explanation | 完整說明民國95年適用條件、純保險費門檻、二十年繳費終身保險修正制及歷史規定語境 | 通過 |
| 顯示品質 | 無亂碼、截斷或選項污染 | 通過 |

## 五、資料完整性與副作用檢查

- `all_questions.json` 在 Web 驗證前後 SHA-256 均為 `90A28FD37B04F896C70611337F4CF5E9E35496700316D948483EF68D260F941F`。
- Web 驗證後 SQLite `questions` 題數為 4,140。
- 與補題前 DB 備份相比，`questions` 僅新增 ID4139、ID4140，既有題目變更為 0。
- `quiz_sessions`、`weak_areas`、`user_answers`、`user_question_marks`、`users`、`user_explanations` 的資料列數均與補題前備份一致。
- SQLite `PRAGMA integrity_check = ok`。
- Web 驗證未修改 output JSON、platform 程式或其他題目。

## 六、結論

ID4139 與 ID4140 的題幹、選項、正確答案、解析、subject 與 unit 均符合核准內容；中文字元正常，未發現亂碼、截斷或選項污染。Web 驗證通過。
