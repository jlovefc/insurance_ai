# ID 4136、4137 正式補題收版紀錄

## 一、執行摘要

- 本次正式補入 2 題經審核通過的漏題候選。
- `MISS-20260716-0004` → ID 4136。
- `MISS-20260716-0001` → ID 4137。
- `all_questions.json` 與 SQLite `questions` 已使用相同 ID 同步新增。
- SQLite 正式 DB 已修改，但受 `.gitignore` 的 `*.db` 規則排除，不納入 Git 追蹤，也不強制提交。
- 本收版階段未再次修改 `all_questions.json` 或 SQLite。

## 二、依據文件與工具

1. `docs/answer_audit/missing_question_inclusion_rules_20260716.md`
2. `docs/answer_audit/missing_question_equivalence_check_20260716.md`
3. `docs/answer_audit/missing_question_equivalence_review_decision_20260716.md`
4. `docs/answer_audit/missing_question_inclusion_plan_20260716.md`
5. `docs/answer_audit/missing_question_4136_4137_pre_apply_check_20260716.md`
6. `tools/apply_missing_questions_4136_4137.py`
7. `docs/corrections/p90_q19_jy_missing_candidate_20260716.md`
8. `docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md`

正式補題由受控腳本的 `--apply` 模式執行，並明確指定本批次兩份 dated backup；腳本先驗證備份與當下正式來源逐位元相同，再同步新增 JSON 與 SQLite。

## 三、備份資訊

- JSON 備份：`backups/all_questions_before_missing_questions_4136_4137_20260716.json`
- DB 備份：`backups/insurance_exam_before_missing_questions_4136_4137_20260716.db`
- DB 備份受 `.gitignore` 排除，不提交 Git，也不強制加入版本控制。
- 備份檔案、大小、SHA-256 與 DB 完整性已記錄於 pre-apply check 文件。

## 四、正式補題結果

| 驗證項目 | 補題前 | 補題後 | 結果 |
|---|---:|---:|---|
| `all_questions.json` 題數 | 4,122 | 4,124 | 增加 2 題 |
| SQLite `questions` 題數 | 4,135 | 4,137 | 增加 2 題 |
| SQLite 最大 ID | 4,135 | 4,137 | 符合 mapping |
| SQLite `integrity_check` | `ok` | `ok` | 通過 |

- ID 4136、4137 在 `all_questions.json` 與 SQLite 均各存在一筆。
- 兩來源的 subject、unit、content、options 及 correct_answer 一致。
- SQLite 已保存兩題 explanation。
- Git 差異中的 `all_questions.json` 僅新增 ID 4136、4137，共 26 行。

## 五、新增題目明細

### ID 4136

- case_id：`MISS-20260716-0004`
- source：JY P.90 Q19
- subject：B 保險實務-分類
- unit：03 保險費架構、解約金、準備金、保單紅利
- content：若預定死亡率降低，定期保險的保險費就會？
- options：`["一樣", "不一定", "便宜", "貴"]`
- correct_answer：`"3"`
- explanation：其他條件不變時，預定死亡率降低代表預期死亡給付成本下降，定期保險保費因而降低。

### ID 4137

- case_id：`MISS-20260716-0001`
- source：JY P.89 Q12
- subject：B 保險實務-分類
- unit：03 保險費架構、解約金、準備金、保單紅利
- content：一萬名30歲的男性各投保100萬的死亡保險（保險期間1年），若生命表顯示30歲男性死亡率為千分之二，請問每人該付多少純保費？
- options：`["1仟元", "2仟元", "3仟元", "4仟元"]`
- correct_answer：`"2"`
- explanation：

  ```text
  10000 × 2/1000 = 20人
  20 × 1000000 / 10000 = 2000
  ```

## 六、Git 策略

- `all_questions.json` 是 tracked file，後續應提交。
- SQLite 正式 DB 已修改，但 `.db` 檔受 `.gitignore` 排除，不強制提交。
- 後續 commit 應只包含：
  1. `all_questions.json`
  2. `docs/answer_audit/missing_question_4136_4137_apply_closeout_20260716.md`
  3. `docs/corrections/correction_ledger_20260716.md`
- 不得加入 SQLite DB、output JSON、platform 程式或其他檔案。

## 七、後續仍需執行

- Web 顯示驗證尚未執行。
- 後續需確認 ID 4136、4137 可在 Web 題庫中正常顯示。
- 題幹、選項、答案及解析須在 Web 端再次確認。
- 完成 Web 驗證後，可建立 Web 驗證收版文件。
- Web 驗證完成前，本文件只代表資料層正式補題完成，不代表畫面驗證已收版。
