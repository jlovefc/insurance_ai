# JY unit03 Q35／Q36（ID4139／4140）正式補題收版

## 一、執行摘要

本次依核准的版本化題目內容，正式補入兩題：

- `MISS-20260716-0010`（JY P.91 Q35）→ ID4139。
- `MISS-20260716-0011`（JY P.91 Q36）→ ID4140。

`all_questions.json` 與本機正式 SQLite `questions` 已同步新增。SQLite 正式資料庫受 `.gitignore` 排除，不納入 Git。

## 二、依據文件與工具

- `docs/answer_audit/jy_unit03_q35_q36_official_law_support_20260716.md`
- `docs/answer_audit/jy_unit03_q35_q36_versioned_question_draft_20260716.md`
- `docs/answer_audit/jy_unit03_q35_q36_inclusion_plan_20260716.md`
- `docs/answer_audit/missing_questions_4139_4140_pre_apply_check_20260716.md`
- `docs/corrections/p91_q35_jy_missing_candidate_20260716.md`
- `docs/corrections/p91_q36_jy_missing_candidate_20260716.md`
- `tools/apply_missing_questions_4139_4140.py`

## 三、備份

- JSON：`backups/all_questions_before_missing_questions_4139_4140_20260716.json`
- SQLite：`backups/insurance_exam_before_missing_questions_4139_4140_20260716.db`

兩份備份已於 pre-apply 階段完成 SHA-256 比對；SQLite 備份 `integrity_check = ok`。DB 備份受 `.gitignore` 排除，不提交 Git。

## 四、正式補題結果

執行命令：

```text
python tools/apply_missing_questions_4139_4140.py --apply --json-backup backups/all_questions_before_missing_questions_4139_4140_20260716.json --database-backup backups/insurance_exam_before_missing_questions_4139_4140_20260716.db
```

驗證結果：

- `all_questions.json`：4,125 → 4,127 題。
- SQLite `questions`：4,138 → 4,140 題。
- JSON 與 SQLite 新增 ID 僅為 4139、4140。
- JSON 與 SQLite 的既有題目均未變更。
- SQLite `PRAGMA integrity_check = ok`。

## 五、新增題目明細

### ID4139

- case_id：`MISS-20260716-0010`
- source：JY P.91 Q35
- subject：B 保險實務-分類
- unit：03 保險費架構、解約金、準備金、保單紅利
- content：依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定之保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費二十五年滿期生死合險為大者，應採用下列何種修正制計算最低責任準備金？
- options：`["二十年滿期生死合險修正制", "二十五年滿期生死合險修正制", "二十年繳費終身保險修正制", "一年定期修正制"]`
- correct_answer：`"2"`
- explanation：依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定、保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費二十五年滿期生死合險為大者，最低責任準備金採二十五年滿期生死合險修正制，因此答案為第2項。此為歷史契約適用規定，不代表未附時點限制的現行法規定。

### ID4140

- case_id：`MISS-20260716-0011`
- source：JY P.91 Q36
- subject：B 保險實務-分類
- unit：03 保險費架構、解約金、準備金、保單紅利
- content：依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定之保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險為大者，應採用下列何種修正制計算最低責任準備金？
- options：`["二十年滿期生死合險修正制", "二十五年滿期生死合險修正制", "二十年繳費終身保險修正制", "一年定期修正制"]`
- correct_answer：`"3"`
- explanation：依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定、保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險為大者，最低責任準備金採二十年繳費終身保險修正制，因此答案為第3項。此為歷史契約適用規定，不代表未附時點限制的現行法規定。

## 六、Git 策略與後續

- `all_questions.json` 為 tracked file，應提交。
- SQLite 正式 DB 已同步新增，但不強制提交。
- 本次收版 commit 應包含 `all_questions.json`、本文件及 `docs/corrections/correction_ledger_20260716.md`。
- 正式補題提交後，仍需以既有臨時 venv 啟動 Web 系統，驗證 ID4139／4140 的題幹、選項、答案、解析、subject、unit 及中文字元顯示。
