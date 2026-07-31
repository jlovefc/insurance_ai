# JY unit03 Q35／Q36 版本化補題 ID mapping 計畫

## 一、目的與限制

本文件依已完成的官方法規佐證、版本化草案及 ChatGPT 核准文字，只規劃 `MISS-20260716-0010`（Q35）與 `MISS-20260716-0011`（Q36）的補題 ID mapping。

本文件不是正式補題結果。本階段不修改 `all_questions.json`、SQLite、output JSON、platform 或 correction ledger，不建立補題腳本，也不把兩案標記為已補入。

## 二、前置核准

- Q35、Q36 不直接沿用原稿題幹，而採明示法源、契約訂定日期及純保險費門檻的版本化題目。
- Q35、Q36 的版本化題幹、選項、答案與解析已獲核准進入 ID mapping。
- ID mapping 完成後仍須另行完成受控腳本、dry-run、備份及正式補題核准。

依據文件：

1. `docs/answer_audit/jy_unit03_q35_q36_official_law_support_20260716.md`
2. `docs/answer_audit/jy_unit03_q35_q36_versioned_question_draft_20260716.md`
3. `docs/answer_audit/jy_unit03_q29_q35_q36_version_review_preparation_20260716.md`
4. `docs/corrections/p91_q35_jy_missing_candidate_20260716.md`
5. `docs/corrections/p91_q36_jy_missing_candidate_20260716.md`

## 三、唯讀前置檢查

| 檢查項目 | 結果 |
|---|---:|
| `all_questions.json` 題數 | 4,125 |
| `all_questions.json` 最大 ID | 4138 |
| SQLite `questions` 題數 | 4,138 |
| SQLite `questions` 最大 ID | 4138 |
| Q35 核准版完整題幹是否已存在 | JSON 0 筆；SQLite 0 筆 |
| Q36 核准版完整題幹是否已存在 | JSON 0 筆；SQLite 0 筆 |

目前 JSON 與 SQLite 的最大 ID 均為 4138。ID4139、ID4140 尚未分配，未見 ID 衝突；兩個核准版完整題幹亦尚未存在。

## 四、ID 分配規則

1. 從 `all_questions.json` 目前最大 ID 加一開始連續分配。
2. 不重用缺號，不插入既有 ID。
3. SQLite 與 `all_questions.json` 必須使用相同 ID。
4. 正式執行前須再次唯讀確認最大 ID、目標 ID 與完整題幹，若狀態改變即停止。

## 五、ID mapping

| case_id | source | proposed_new_id | inclusion_status | evidence_file |
|---|---|---:|---|---|
| `MISS-20260716-0010` | JY P.91 Q35 | 4139 | `planned_only_not_applied` | `docs/corrections/p91_q35_jy_missing_candidate_20260716.md` |
| `MISS-20260716-0011` | JY P.91 Q36 | 4140 | `planned_only_not_applied` | `docs/corrections/p91_q36_jy_missing_candidate_20260716.md` |

## 六、ID4139／Q35 核准內容

- case_id：`MISS-20260716-0010`
- proposed_new_id：4139
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定之保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費二十五年滿期生死合險為大者，應採用下列何種修正制計算最低責任準備金？`
- options：`["二十年滿期生死合險修正制", "二十五年滿期生死合險修正制", "二十年繳費終身保險修正制", "一年定期修正制"]`
- correct_answer：`"2"`
- explanation：`依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定、保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費二十五年滿期生死合險為大者，最低責任準備金採二十五年滿期生死合險修正制，因此答案為第2項。此為歷史契約適用規定，不代表未附時點限制的現行法規定。`
- inclusion_status：`planned_only_not_applied`

## 七、ID4140／Q36 核准內容

- case_id：`MISS-20260716-0011`
- proposed_new_id：4140
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定之保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險為大者，應採用下列何種修正制計算最低責任準備金？`
- options：`["二十年滿期生死合險修正制", "二十五年滿期生死合險修正制", "二十年繳費終身保險修正制", "一年定期修正制"]`
- correct_answer：`"3"`
- explanation：`依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定、保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險為大者，最低責任準備金採二十年繳費終身保險修正制，因此答案為第3項。此為歷史契約適用規定，不代表未附時點限制的現行法規定。`
- inclusion_status：`planned_only_not_applied`

## 八、正式補題前必要條件

1. 再次確認 ID4139、ID4140 及兩個完整題幹均不存在。
2. 建立只允許處理 ID4139、ID4140 的受控補題腳本。
3. 腳本預設必須為 dry-run，只有明確 `--apply` 才可寫入。
4. 先執行 dry-run，確認 JSON 與 SQLite SHA-256 不變。
5. 正式補題前備份 `all_questions.json` 與 SQLite。
6. 另行取得正式 `--apply` 核准。
7. 正式補入後，JSON 與 SQLite 題數應各增加兩題，既有題不得變更。
8. 執行 SQLite `integrity_check`。
9. 建立 apply closeout，更新 correction ledger。
10. 執行 Web 顯示驗證並建立驗證文件。

## 九、禁止事項

- 本文件不代表 ID4139、ID4140 已存在或已補入。
- 不得因本 mapping 計畫直接修改正式題庫。
- 不得只修改 SQLite 而不同步 `all_questions.json`。
- 不得未備份、未 dry-run 或未取得 `--apply` 核准即正式補題。
- 不得把兩案提前標記為 `applied`、`included` 或 `ready_to_fix`。
