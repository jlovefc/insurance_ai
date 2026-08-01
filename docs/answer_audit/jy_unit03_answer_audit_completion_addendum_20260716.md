# JY unit03 答案校驗最終完成補充收版

## 一、文件目的

本文件補充 `docs/answer_audit/jy_unit03_answer_audit_final_closeout_20260716.md` 建立後完成的暫緩題處理結果，作為 JY-人身保險.pdf「三、保險費架構、解約金、準備金、保單紅利」本輪校驗的最終完成紀錄。

## 二、本輪完成狀態

- manual_review：0 題。
- 原暫緩題 Q29、Q35、Q36、Q47：均已完成審查與後續處理。
- 原暫緩題剩餘：0 題。
- 正式題庫補入、既有題修正與 Web 驗證：均已完成。
- 本機 `main` 已與 `origin/main` 同步至 Q29／ID4141 Web 驗證 commit。

## 三、已完成既有題修正

| question_id | 問題類型 | 完成結果 |
|---:|---|---|
| 3815 | `wrong_answer`, `option_pollution`, `ocr_parse_error` | 已修正、收版並完成 Web 驗證 |
| 3785 | `option_pollution`, `truncated_question` | 已修正、收版並完成 Web 驗證 |
| 2664 | `wrong_answer`, `duplicate_conflict`, `explanation_conflict` | 已修正、收版並完成 Web 驗證 |
| 2654 | `wrong_answer`, `duplicate_conflict`, `explanation_conflict` | 已修正、收版並完成 Web 驗證 |

## 四、已完成正式補題

| case_id | source | new_question_id | 處理結果 |
|---|---|---:|---|
| `MISS-20260716-0004` | JY P.90 Q19 | 4136 | 已補入 JSON／SQLite，Web 驗證通過 |
| `MISS-20260716-0001` | JY P.89 Q12 | 4137 | 已補入 JSON／SQLite，Web 驗證通過 |
| `MISS-20260716-0013` | JY P.91 Q47 | 4138 | 完成等價題裁定後補入，Web 驗證通過 |
| `MISS-20260716-0010` | JY P.91 Q35 | 4139 | 完成官方佐證與版本化改寫後補入，Web 驗證通過 |
| `MISS-20260716-0011` | JY P.91 Q36 | 4140 | 完成官方佐證與版本化改寫後補入，Web 驗證通過 |
| `MISS-20260716-0008` | JY P.90 Q29 | 4141 | 完成官方佐證與版本化改寫後補入，Web 驗證通過 |

## 五、原暫緩題最終處理

### Q47／ID4138

- 裁定可與 ID107 並存。
- ID3795、ID3796 僅為部分重疊，不能覆蓋 Q47。
- 已完成 ID mapping、備份、dry-run、正式補入、收版及 Web 驗證。
- 相關 commits：`cd55860`、`4a1f747`。

### Q35／ID4139 與 Q36／ID4140

- 未直接依原稿補入；先完成官方法規與歷史時點佐證。
- 題幹明示當時《保險業各種準備金提存辦法》、契約日期、適用條件及純保險費門檻。
- 已完成版本化改寫、ID mapping、備份、dry-run、正式補入、收版及 Web 驗證。
- 相關 commits：`bb07404`、`b2eb5d7`。

### Q29／ID4141

- 未直接依教材舊題補入；先完成官方法規佐證與版本化改寫。
- 題目明示金管保壽字第11304922511號令之發布日與生效日。
- 已完成 ID mapping、備份、dry-run、正式補入、收版及 Web 驗證。
- 相關 commits：`9db16fb`、`d7c110b`。

## 六、不補入案例

等價題審核判定正式題庫已存在的 C 類案例維持不補入。相關既有題答案衝突已另案處理者，已依原稿及等價題證據完成修正；不得再以漏題方式重複新增。

## 七、最終資料狀態

- `all_questions.json` 題數：4,128。
- 本機 SQLite `questions` 題數：4,141。
- JSON 與 SQLite 最大 ID：4141。
- SQLite `integrity_check`：`ok`。
- `all_questions.json`：已更新並推送。
- SQLite 正式 DB：本機已同步，但依 `.gitignore` 不納入 Git。
- output JSON：本輪未修改。
- platform 程式：本輪未修改。
- ID4138、ID4139、ID4140、ID4141：Web 驗證均通過。

## 八、剩餘風險

- SQLite DB 未納入 Git；未來換機或重建環境時，必須透過已提交的受控腳本或正式匯入流程重建。
- output/JY-人身保險.json 仍含歷史 OCR／解析問題，不是本輪答案正確性的最終依據。
- 涉及法規與歷史時點的題目必須保留版本語境，不得逕以未附時點限制的現行法敘述取代。
- C 類不補入案例仍須保留 evidence 與 ledger 紀錄，以防未來重複匯入。

## 九、下一階段

JY unit03 本輪答案校驗已完成。下一階段建議依既定 source-based workflow，先唯讀盤點 JY-人身保險.pdf 的下一個單元範圍、頁碼、題號、題數及正式題庫對應狀態，再建立下一批逐題校驗計畫；未完成原稿與系統對照前不得修改題庫。
