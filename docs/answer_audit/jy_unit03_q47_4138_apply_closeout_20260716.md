# JY unit03 Q47 / ID4138 正式補題收版

## 一、執行摘要

本次依核准流程正式將 JY P.91 Q47 補入正式題庫，對應 `MISS-20260716-0013` → ID4138。`all_questions.json` 與本機 SQLite `questions` 已同步新增；SQLite 資料庫受 `.gitignore` 排除，不納入 Git。

## 二、依據文件

- `docs/answer_audit/jy_unit03_q47_equivalence_decision_20260716.md`
- `docs/answer_audit/jy_unit03_q47_inclusion_plan_20260716.md`
- `docs/answer_audit/jy_unit03_q47_4138_pre_apply_check_20260716.md`
- `tools/apply_missing_question_4138_q47.py`
- `docs/corrections/p91_q47_jy_missing_candidate_20260716.md`

## 三、備份

- JSON：`backups/all_questions_before_q47_4138_inclusion_20260716.json`
- SQLite：`backups/insurance_exam_before_q47_4138_inclusion_20260716.db`

兩份備份已在 pre-apply 階段核對為與修正前正式檔逐位元一致。SQLite 備份受 `.gitignore` 排除，不強制提交。

## 四、補入結果

- 執行工具：`python tools/apply_missing_question_4138_q47.py --apply --json-backup backups/all_questions_before_q47_4138_inclusion_20260716.json --database-backup backups/insurance_exam_before_q47_4138_inclusion_20260716.db`
- `all_questions.json`：4,124 → 4,125 題
- SQLite `questions`：4,137 → 4,138 題
- SQLite `PRAGMA integrity_check`：`ok`
- JSON 新增 ID：僅 4138
- SQLite 新增 ID：僅 4138
- 既有題目差異：無

## 五、ID4138 題目明細

- case_id：`MISS-20260716-0013`
- source：JY-人身保險.pdf P.91 Q47
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`保單紅利支付的方法有？`
- options：`["BCD", "ACD", "ABCD", "ABC"]`
- correct_answer：`"3"`
- explanation：`保單紅利支付方法包括購買增額繳清金額、積存方法、抵繳保費及現金支付方法，因此答案為ABCD。`

## 六、Git 策略

- `all_questions.json` 為 tracked file，應提交。
- SQLite 正式 DB 已同步新增 ID4138，但 `.db` 受 `.gitignore` 排除，不強制提交。
- 本批次提交範圍為 `all_questions.json`、本收版文件與 `docs/corrections/correction_ledger_20260716.md`。

## 七、後續驗證

正式資料同步與完整性檢查已通過。後續需以既有臨時 venv 啟動 Web 系統，驗證 ID4138 的題幹、選項、答案、解析、subject 與 unit 顯示，並確認無亂碼、截斷或選項污染。
