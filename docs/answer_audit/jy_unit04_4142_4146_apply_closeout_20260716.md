# JY unit04 ID4142–4146 正式補題收版

## 一、執行摘要

本批次使用受控腳本正式補入 JY unit04 五題，並同步寫入 `all_questions.json` 與本機 SQLite `questions` 表。

| source | new_question_id | correct_answer |
|---|---:|---:|
| P.94 Q26 | 4142 | 4 |
| P.94 Q28 | 4143 | 4 |
| P.94 Q30 | 4144 | 1 |
| P.95 Q36 | 4145 | 3 |
| P.95 Q38 | 4146 | 2 |

## 二、依據文件與工具

- `docs/answer_audit/jy_unit04_q26_q28_q30_inclusion_plan_20260716.md`
- `docs/answer_audit/jy_unit04_q36_q38_versioned_question_draft_20260716.md`
- `docs/answer_audit/jy_unit04_q36_q38_inclusion_plan_20260716.md`
- `docs/answer_audit/jy_unit04_q26_q28_q30_q36_q38_inclusion_decision_20260716.md`
- `docs/answer_audit/jy_unit04_4142_4146_pre_apply_check_20260716.md`
- `tools/apply_missing_questions_4142_4146.py`

## 三、備份

- JSON：`backups/all_questions_before_unit04_4142_4146_inclusion_20260716.json`
- SQLite：`backups/insurance_exam_before_unit04_4142_4146_inclusion_20260716.db`
- SQLite 備份受 `.gitignore` 的 `*.db` 規則排除，不納入 Git。
- 補題前兩組備份均與正式檔 SHA-256 一致，備份 DB `integrity_check = ok`。

## 四、正式補題結果

- `all_questions.json` 題數：4,128 → 4,133；最大 ID：4141 → 4146。
- SQLite `questions` 題數：4,141 → 4,146；最大 ID：4141 → 4146。
- SQLite `integrity_check = ok`。
- JSON 與 SQLite 新增 ID 僅4142、4143、4144、4145、4146。
- JSON 與 SQLite 既有題均未變更。

## 五、新增題目摘要

- ID4142／P.94 Q26：個人功能組合題；選項 `["AB", "BC", "CD", "ABCD"]`；答案 `"4"`。
- ID4143／P.94 Q28：社會功能組合題；選項 `["AB", "AC", "BC", "BCD"]`；答案 `"4"`。
- ID4144／P.94 Q30：國家功能組合題；選項 `["ABD", "ABC", "ABCD", "ACD"]`；答案 `"1"`。
- ID4145／P.95 Q36：《保險法》第13條人身保險四類版本化題；答案 `"3"`。
- ID4146／P.95 Q38：人身保險市場商品型態版本化題；選項 `["AB", "ABC", "BC", "BCD"]`；答案 `"2"`。

五題完整 content、options 與 explanation 以核准的 inclusion plan 及正式 JSON／SQLite 記錄為準。

## 六、Git 策略

- `all_questions.json` 為 tracked file，本批次提交。
- SQLite 正式 DB 已同步修改，但受 `.gitignore` 排除，不強制提交。
- output JSON 與 platform 程式均未修改。

## 七、後續驗證

正式資料驗證已通過；後續使用既有臨時 venv 啟動本機 Web 系統，逐題檢查 ID4142–4146 的題幹、選項、答案、解析、subject 與 unit，並另建 Web 驗證文件。
