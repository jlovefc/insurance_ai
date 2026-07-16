# 第一批 ready_to_fix 題庫修正收版紀錄

- 收版日期：2026-07-16
- 文件性質：第一批正式題庫資料修正與驗證之收版紀錄
- 本文件建立時未再次修改 `all_questions.json` 或 SQLite。

## 一、修正批次

- `batch_id`：READY-FIX-BATCH-20260716-001
- 修正題目：ID3815、ID3785
- 依據文件：
  - `docs/corrections/correction_ledger_20260716.md`
  - `docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md`
  - `docs/corrections/id3785_jy_p90_reserve_option_pollution_correction_20260716.md`

## 二、修正內容摘要

### ID3815

- 錯誤類型：`wrong_answer`, `option_pollution`, `ocr_parse_error`
- 修正後 `options = ["B", "C", "AC", "ABC"]`
- 修正後 `correct_answer = "1"`
- SQLite 補入 `explanation`：
  `此題B錯誤。其他因素不變，保險費與利率高低成反比。正式考試也可能換問何者正確，則答案就會是3。`

### ID3785

- 錯誤類型：`option_pollution`, `truncated_question`
- 修正後 `content` 補回「，而有差別。」
- 修正後 `options = ["ABD", "BD", "ABC", "ABCD"]`
- `correct_answer` 維持 `"4"`

## 三、備份

| 備份 | 路徑 | 大小 |
|---|---|---:|
| 正式 JSON 修正前備份 | `backups/all_questions_before_ready_to_fix_batch1_20260716.json` | 2,090,348 bytes |
| SQLite 修正前備份 | `backups/insurance_exam_before_ready_to_fix_batch1_20260716.db` | 3,190,784 bytes |

- SQLite 備份 `integrity_check`：`ok`
- 備份檔於修正前建立，且未覆蓋既有檔案。

## 四、驗證結果

- `all_questions.json` 題數仍為 4,122。
- SQLite `questions` 題數仍為 4,135。
- JSON 差異 ID 僅 3785、3815。
- SQLite 差異 ID 僅 3785、3815。
- ID2670 未修改。
- 當前 SQLite `integrity_check = ok`。
- Web 驗證通過。
- Flask 已停止。
- 為避免寫入 `quiz_sessions`，未進入會建立測驗 session 的正常測驗流程。
- 使用登入後的唯讀 `/api/explanation/<id>` 端點驗證實際 Flask 回應。
- Flask 測試後，`quiz_sessions`、`user_answers`、`user_explanations`、`user_question_marks`、`users`、`weak_areas` 均與修正前備份一致。

## 五、Web 驗證結果

### ID3815

- 題幹正確。
- 選項為 B、C、AC、ABC。
- 正確答案為 1。
- 解析全文正確。
- 第 4 選項未混入解析。

### ID3785

- 題幹包含「D.繳費期間，而有差別。」
- 選項為 ABD、BD、ABC、ABCD。
- 正確答案為 4。
- 第 4 選項未包含「，而有差別。」

## 六、Git 注意事項

- `all_questions.json` 是 tracked file，應提交。
- `platform/instance/insurance_exam.db` 被 `.gitignore` 的 `*.db` 規則忽略。
- 不建議直接強制提交 `.db`。
- 為使 SQLite 修正可重現，本批次提供 `tools/apply_batch1_id3815_id3785_sqlite_fix.py`。
- `backups` 內的 JSON 備份可提交；DB 備份可能因 `.gitignore` 而不會進入版控。

## 七、後續建議 commit 範圍

建議下一個 commit 僅包含：

1. `all_questions.json`
2. `backups/all_questions_before_ready_to_fix_batch1_20260716.json`
3. `docs/corrections/batch1_ready_to_fix_correction_closeout_20260716.md`
4. `tools/apply_batch1_id3815_id3785_sqlite_fix.py`

不包含 `.db` 檔，除非使用者另外明確決定要強制納入資料庫檔。

