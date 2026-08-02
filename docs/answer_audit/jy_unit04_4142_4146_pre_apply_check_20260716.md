# JY unit04 ID4142–4146 正式補題前安全檢查

## 一、檢查目的

本文件記錄 JY unit04 Q26、Q28、Q30、Q36、Q38 在正式補入 ID4142–4146 前的備份、完整性檢查及最終 dry-run 結果。本階段未執行 `--apply`，正式題庫尚未修改。

## 二、預計補入摘要

| source | proposed_new_id | correct_answer |
|---|---:|---:|
| P.94 Q26 | 4142 | 4 |
| P.94 Q28 | 4143 | 4 |
| P.94 Q30 | 4144 | 1 |
| P.95 Q36 | 4145 | 3 |
| P.95 Q38 | 4146 | 2 |

受控腳本：`tools/apply_missing_questions_4142_4146.py`

## 三、備份

| 類型 | 備份路徑 | 大小 |
|---|---|---:|
| JSON | `backups/all_questions_before_unit04_4142_4146_inclusion_20260716.json` | 2,041,013 bytes |
| SQLite | `backups/insurance_exam_before_unit04_4142_4146_inclusion_20260716.db` | 3,198,976 bytes |

SQLite 備份受 `.gitignore` 的 `*.db` 規則排除，不強制納入 Git。

## 四、SHA-256 與完整性

- 正式 JSON：`3fa735f358d24e86fab86348d12d54ca17f8be53b902bbfc5763df07f5907c56`
- 備份 JSON：`3fa735f358d24e86fab86348d12d54ca17f8be53b902bbfc5763df07f5907c56`
- 正式 SQLite：`57488a8fb4f638dc36f5aa7eeaee9dce423dff692b3c1497b8238d1acac7c5a7`
- 備份 SQLite：`57488a8fb4f638dc36f5aa7eeaee9dce423dff692b3c1497b8238d1acac7c5a7`
- JSON 正式檔與備份逐位元一致。
- SQLite 正式檔與備份逐位元一致。
- 備份 SQLite `integrity_check = ok`。
- 備份 SQLite 題數4,141、最大 ID4141。

## 五、最終 dry-run

執行：

`python tools/apply_missing_questions_4142_4146.py`

結果：

- dry-run 成功。
- `all_questions.json` SHA-256 前後一致。
- SQLite 正式檔 SHA-256 前後一致。
- ID4142至4146仍不存在於 JSON。
- ID4142至4146仍不存在於 SQLite。
- `all_questions.json` 題數維持4,128、最大 ID維持4141。
- SQLite `questions` 題數維持4,141、最大 ID維持4141。
- SQLite 正式檔 `integrity_check = ok`。

## 六、正式題庫狀態

- 尚未執行 `--apply`。
- `all_questions.json` 未修改。
- SQLite 正式檔未修改。
- output JSON、platform 程式與 correction ledger 均未修改。

## 七、下一步

必須取得明確核准後，才可使用下列受控命令正式補入：

`python tools/apply_missing_questions_4142_4146.py --apply --json-backup backups/all_questions_before_unit04_4142_4146_inclusion_20260716.json --database-backup backups/insurance_exam_before_unit04_4142_4146_inclusion_20260716.db`

在取得明確核准前，不得執行上述命令。
