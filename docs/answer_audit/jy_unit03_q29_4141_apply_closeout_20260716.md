# JY unit03 Q29／ID4141 正式補題收版

## 一、執行摘要

本次依核准之法規佐證、版本化改寫、ID mapping、備份及受控腳本流程，正式將 `MISS-20260716-0008`（JY P.90 Q29）補入為 ID4141。`all_questions.json` 與本機 SQLite `questions` 已同步新增；SQLite 資料庫受 `.gitignore` 排除，不納入 Git。

## 二、依據文件

- `docs/answer_audit/jy_unit03_q29_official_law_support_20260716.md`
- `docs/answer_audit/jy_unit03_q29_versioned_question_draft_20260716.md`
- `docs/answer_audit/jy_unit03_q29_inclusion_plan_20260716.md`
- `docs/answer_audit/jy_unit03_q29_4141_pre_apply_check_20260716.md`
- `tools/apply_missing_question_4141_q29.py`
- `docs/corrections/p90_q29_jy_missing_candidate_20260716.md`

## 三、備份

- JSON：`backups/all_questions_before_q29_4141_inclusion_20260716.json`
- SQLite：`backups/insurance_exam_before_q29_4141_inclusion_20260716.db`

兩份備份已在 pre-apply 階段核對為與補題前正式檔逐位元一致。SQLite 備份受 `.gitignore` 排除，不強制提交。

## 四、正式補題結果

- 執行工具：`python tools/apply_missing_question_4141_q29.py --apply --json-backup backups/all_questions_before_q29_4141_inclusion_20260716.json --database-backup backups/insurance_exam_before_q29_4141_inclusion_20260716.db`
- `all_questions.json`：4,127 → 4,128 題
- SQLite `questions`：4,140 → 4,141 題
- SQLite `PRAGMA integrity_check`：`ok`
- JSON 新增 ID：僅 4141
- SQLite 新增 ID：僅 4141
- JSON 既有題目差異：無
- SQLite 既有題目差異：無

## 五、ID4141 題目明細

- case_id：`MISS-20260716-0008`
- source：JY-人身保險.pdf P.90 Q29；經官方法規佐證後採版本化題目
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`依金融監督管理委員會民國113年7月16日發布、同年11月1日生效之金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務時，下列有關銷售文件之敘述何者正確？`
- options：`["不得單獨強調保費預定利率", "得以保單報酬率與銀行存款報酬率比較作為主要招攬訴求", "無須說明本保險不參加紅利分配及無紅利給付項目", "得將保費預定利率作為唯一銷售重點"]`
- correct_answer：`"1"`
- explanation：`依金融監督管理委員會民國113年7月16日金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務，其銷售文件不得單獨強調保費預定利率，亦不得以保單報酬率與其他金融商品比較等方式誤導保戶；銷售文件、保險單面頁及保險單條款並應明確說明本保險為不分紅保險單、不參加紅利分配且無紅利給付項目。該令自民國113年11月1日生效，因此答案為第1項。`

## 六、資料與編碼驗證

獨立讀回檢查確認 ID4141 在 JSON 與 SQLite 的 `subject`、`unit`、`content`、`options`、`correct_answer` 及 `explanation` 均逐欄符合受控腳本中的核准內容。命令列曾因 Windows 終端字元編碼呈現 mojibake，但資料逐欄比對結果全部一致，並非題庫內容遭錯誤轉碼。

## 七、Git 策略

- `all_questions.json` 為 tracked file，應提交。
- SQLite 正式 DB 已同步新增 ID4141，但 `.db` 受 `.gitignore` 排除，不強制提交。
- 本批次提交範圍為 `all_questions.json`、本收版文件與 `docs/corrections/correction_ledger_20260716.md`。

## 八、後續驗證

正式資料同步與完整性檢查已通過。後續需使用既有臨時 venv 啟動 Web 系統，驗證 ID4141 的題幹、選項、答案、解析、subject 與 unit 顯示，並確認無亂碼、截斷或選項污染。
