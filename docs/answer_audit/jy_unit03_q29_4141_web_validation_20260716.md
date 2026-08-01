# JY unit03 Q29／ID4141 Web 驗證

## 一、驗證對象

- question_id：`4141`
- case_id：`MISS-20260716-0008`
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`

## 二、驗證環境與方式

- 專案：`C:\insurance_ai`
- 既有臨時 venv：`C:\insurance_ai_runtime\web_validation_venv`
- Flask 應用：`platform/app.py`
- 驗證端點：`GET /api/explanation/4141`
- 驗證方法：使用 Flask test client 經實際應用路由讀取本機正式 SQLite，未啟動測驗流程，未寫入 quiz sessions 或其他資料表。
- 核准內容比較來源：`tools/apply_missing_question_4141_q29.py` 內的受控 `QUESTION` 定義，避免 Windows 終端字元編碼影響人工字串比較。

## 三、Web 顯示驗證結果

| 檢查項目 | 結果 |
|---|---|
| HTTP 狀態 | `200` |
| 題幹 | 與核准內容精確一致 |
| options | 與核准四個選項精確一致 |
| correct_answer | `"1"`，正確 |
| explanation | 與核准文字精確一致 |
| subject | `B 保險實務-分類`，正確 |
| unit | `03 保險費架構、解約金、準備金、保單紅利`，正確 |
| 亂碼 | 無資料亂碼；獨立逐欄比較全部通過 |
| 題幹截斷 | 無 |
| 選項污染 | 無 |

## 四、資料完整性與無寫入確認

- Web 驗證前 SQLite SHA-256：`72591D08AF68E1AEF2DF1EF27B97A317FC6F44F3C748B11C0848FE32D9F3AE15`
- Web 驗證後 SQLite SHA-256：`72591D08AF68E1AEF2DF1EF27B97A317FC6F44F3C748B11C0848FE32D9F3AE15`
- 比對結果：一致，Web 驗證未修改 SQLite。
- 未修改 `all_questions.json`、output JSON 或 platform 程式。

## 五、結論

ID4141 Web 驗證通過。題幹、選項、答案、解析、subject 與 unit 均能由 Flask 應用正常讀取並與核准內容精確一致，未發現亂碼、截斷或選項污染。
