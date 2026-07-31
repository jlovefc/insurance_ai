# Q35／Q36（ID4139／4140）正式補題前安全檢查

## 一、目的與限制

本文件記錄 JY unit03 Q35／Q36 版本化題目在正式補入前的備份、完整性檢查與最終 dry-run 結果。

本階段未執行 `--apply`，未修改 `all_questions.json` 或正式 SQLite 題庫。正式補題仍須另行取得明確核准。

## 二、依據

- `docs/answer_audit/jy_unit03_q35_q36_official_law_support_20260716.md`
- `docs/answer_audit/jy_unit03_q35_q36_versioned_question_draft_20260716.md`
- `docs/answer_audit/jy_unit03_q35_q36_inclusion_plan_20260716.md`
- `tools/apply_missing_questions_4139_4140.py`
- `docs/corrections/p91_q35_jy_missing_candidate_20260716.md`
- `docs/corrections/p91_q36_jy_missing_candidate_20260716.md`

## 三、備份資訊

| 類型 | 備份路徑 | 檔案大小 | SHA-256 |
|---|---|---:|---|
| JSON | `backups/all_questions_before_missing_questions_4139_4140_20260716.json` | 2,091,298 bytes | `D63619FDF5719CE0F478B8F6E7970082335D0E479DFF92A5BBBA883B45F84AF6` |
| SQLite | `backups/insurance_exam_before_missing_questions_4139_4140_20260716.db` | 3,194,880 bytes | `9EF0B450087C7733C1A0333BD9470EF5AE4E52B88299BDD6E957862235DC9188` |

- JSON 備份與當下正式 `all_questions.json` 的 SHA-256 相同。
- SQLite 備份與當下正式 `platform/instance/insurance_exam.db` 的 SHA-256 相同。
- SQLite 備份 `PRAGMA integrity_check` 結果：`ok`。
- SQLite `.db` 備份受 `.gitignore` 排除，不強制加入 Git。

## 四、最終 dry-run

執行命令：

```text
python tools/apply_missing_questions_4139_4140.py
```

未執行：

```text
python tools/apply_missing_questions_4139_4140.py --apply
```

結果：

- dry-run 成功。
- `all_questions.json` 執行前後 SHA-256 均為
  `D63619FDF5719CE0F478B8F6E7970082335D0E479DFF92A5BBBA883B45F84AF6`。
- 正式 SQLite 執行前後 SHA-256 均為
  `9EF0B450087C7733C1A0333BD9470EF5AE4E52B88299BDD6E957862235DC9188`。
- `all_questions.json` 題數維持 4,125，最大 ID 維持 4138。
- SQLite `questions` 題數維持 4,138，最大 ID 維持 4138。
- ID4139、ID4140 仍不存在於 `all_questions.json`。
- ID4139、ID4140 仍不存在於 SQLite。
- 正式 SQLite `PRAGMA integrity_check` 結果：`ok`。

## 五、預計補入摘要

| case_id | 來源 | proposed_new_id | 答案 | 狀態 |
|---|---|---:|---:|---|
| `MISS-20260716-0010` | JY P.91 Q35 | 4139 | 2 | 僅規劃，尚未補入 |
| `MISS-20260716-0011` | JY P.91 Q36 | 4140 | 3 | 僅規劃，尚未補入 |

兩題均採 ChatGPT 核准的版本化題幹，明示「依當時《保險業各種準備金提存辦法》規定」、契約日期、保險期間及純保險費門檻。

## 六、結論與下一步

備份、雜湊比對、SQLite 完整性檢查及最終 dry-run 均通過，正式題庫尚未修改。

下一步必須取得明確正式補題核准後，才可使用指定備份執行：

```text
python tools/apply_missing_questions_4139_4140.py --apply --json-backup backups/all_questions_before_missing_questions_4139_4140_20260716.json --database-backup backups/insurance_exam_before_missing_questions_4139_4140_20260716.db
```

本文件不代表已補題，也不得用來跳過正式核准、套用後驗證、Web 驗證與收版流程。
