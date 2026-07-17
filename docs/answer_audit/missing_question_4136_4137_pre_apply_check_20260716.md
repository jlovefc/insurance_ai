# ID 4136、4137 正式補題前安全檢查

## 一、檢查目的與限制

本文件記錄 ID 4136、4137 正式補題前的備份與最終 dry-run 結果。本次只建立正式來源的當下備份、執行 `tools/apply_missing_questions_4136_4137.py` 預設 dry-run 並驗證未寫入；未執行 `--apply`，正式題庫尚未修改。

## 二、執行前狀態

- Git branch：`main`
- 執行前 `git status -sb`：`## main...origin/main`
- 基準 commit：`1d8f6aa Add dry-run script for missing question inclusion`
- `all_questions.json` 題數：4,122
- `all_questions.json` 最大 ID：4135
- SQLite `questions` 題數：4,135
- SQLite `questions` 最大 ID：4135
- ID 4136、4137：兩個正式來源均不存在

## 三、備份檔案

| 類型 | 備份路徑 | 大小（bytes） | SHA-256 |
|---|---|---:|---|
| JSON | `backups/all_questions_before_missing_questions_4136_4137_20260716.json` | 2,090,189 | `711608c98eab03ea325f01c644d8a8bd3a6f16f04e5fed69e1526d03d6bd7f06` |
| SQLite | `backups/insurance_exam_before_missing_questions_4136_4137_20260716.db` | 3,190,784 | `6b180a1e9b2c40034451ec15fb394c057fe453dfa691c0766a5c50bf057d1e17` |

備份使用不覆蓋方式由當下正式來源複製。JSON 備份 SHA-256 與正式 `all_questions.json` 相同；DB 備份 SHA-256 與正式 `platform/instance/insurance_exam.db` 相同。

## 四、備份完整性檢查

- 備份 DB `PRAGMA integrity_check`：`ok`
- 備份 DB `questions` 題數：4,135
- 備份 DB 最大 ID：4135
- 結論：備份 DB 可讀、完整，且與當下正式 DB 逐位元相同。

## 五、最終 dry-run

執行命令：

```text
python tools/apply_missing_questions_4136_4137.py
```

未執行：

```text
python tools/apply_missing_questions_4136_4137.py --apply
```

Dry-run 結果：成功。

- 腳本確認 JSON 題數 4,122、最大 ID 4135。
- 腳本確認 SQLite 題數 4,135、最大 ID 4135。
- 腳本確認 ID 4136、4137 在兩來源均未被占用。
- 腳本確認兩個擬補入題幹在兩來源均無完全相同題幹。
- 腳本只列印將新增的兩題，沒有執行任何寫入。
- 腳本回報 `all_questions.json hash unchanged: true`。
- 腳本回報 `SQLite hash unchanged: true`。

## 六、Dry-run 後獨立驗證

| 驗證項目 | 結果 |
|---|---|
| 正式 JSON SHA-256 | `711608c98eab03ea325f01c644d8a8bd3a6f16f04e5fed69e1526d03d6bd7f06`，與執行前及備份相同 |
| 正式 SQLite SHA-256 | `6b180a1e9b2c40034451ec15fb394c057fe453dfa691c0766a5c50bf057d1e17`，與執行前及備份相同 |
| JSON 題數 | 4,122，未變 |
| SQLite `questions` 題數 | 4,135，未變 |
| JSON ID 4136、4137 | 不存在 |
| SQLite ID 4136、4137 | 不存在 |
| 正式 SQLite `integrity_check` | `ok` |

結論：dry-run 未修改 `all_questions.json` 或正式 SQLite；ID 4136、4137 尚未正式補入。

## 七、Git 收錄範圍

- JSON 備份可加入版本控制。
- DB 備份受 `.gitignore` 的 `*.db` 規則排除，不得強制加入版本控制。
- 本批次建議提交範圍僅包含：
  1. `backups/all_questions_before_missing_questions_4136_4137_20260716.json`
  2. `docs/answer_audit/missing_question_4136_4137_pre_apply_check_20260716.md`

## 八、下一步與正式 Apply 限制

1. 下一步必須由使用者明確核准後，才可執行 `--apply`。
2. 正式執行前須再次確認工作樹、兩來源 hash、題數、最大 ID、ID 占用及完全相同題幹。
3. 本次備份檔名含日期；正式執行時必須明確將下列備份路徑傳給腳本：

```text
--json-backup backups/all_questions_before_missing_questions_4136_4137_20260716.json
--database-backup backups/insurance_exam_before_missing_questions_4136_4137_20260716.db
```

4. 腳本會要求備份與執行當下正式來源逐位元相同；若 hash 不同即拒絕執行，必須重新備份及重新審核。
5. 未取得核准前不得執行 `--apply`、不得啟動 Flask、不得修改正式題庫。
