# ID2664 / ID2654 正式修正前安全檢查

## 一、檢查目的與範圍

本文件記錄 ID2664、ID2654 正式修正前的備份與最終 dry-run 結果。本次未執行 `--apply`，未修改 `all_questions.json` 或正式 SQLite 資料庫。

依據腳本：`tools/apply_existing_question_corrections_2664_2654.py`

## 二、備份資訊

| 類型 | 備份路徑 | 檔案大小 |
|---|---|---:|
| JSON | `backups/all_questions_before_existing_corrections_2664_2654_20260716.json` | 2,090,993 bytes |
| SQLite | `backups/insurance_exam_before_existing_corrections_2664_2654_20260716.db` | 3,194,880 bytes |

SQLite 備份受 `.gitignore` 的 `.db` 規則排除，不強制加入 Git。

## 三、SHA-256 與完整性檢查

| 檔案 | SHA-256 |
|---|---|
| `all_questions.json` | `96299b21a8fd33f99c722dd8bc3b6ad1241ee558f027083fef1abccf940653a6` |
| JSON 備份 | `96299b21a8fd33f99c722dd8bc3b6ad1241ee558f027083fef1abccf940653a6` |
| `platform/instance/insurance_exam.db` | `482d46b4165c24ec078dd7783ff52a5366cf2b9e43d0f436943523f5c6dc6cc7` |
| SQLite 備份 | `482d46b4165c24ec078dd7783ff52a5366cf2b9e43d0f436943523f5c6dc6cc7` |

- JSON 正式檔與備份檔 SHA-256 相同。
- SQLite 正式檔與備份檔 SHA-256 相同。
- SQLite 備份 `PRAGMA integrity_check`：`ok`。

## 四、最終 dry-run 結果

執行命令：

```text
python tools/apply_existing_question_corrections_2664_2654.py
```

未執行：

```text
python tools/apply_existing_question_corrections_2664_2654.py --apply
```

檢查結果：

- dry-run 成功。
- `all_questions.json` SHA-256 前後一致。
- 正式 SQLite SHA-256 前後一致。
- `all_questions.json` 題數維持 4,124。
- SQLite `questions` 題數維持 4,137。
- JSON 與 SQLite 的 ID2664 `correct_answer` 仍為 `"1"`。
- JSON 與 SQLite 的 ID2654 `correct_answer` 仍為 `"1"`。
- 正式題庫尚未修改。

## 五、ID2664 預計修正摘要

- question_id：2664
- 現行 `correct_answer`：`"1"`（BC）
- 預計 `correct_answer`：`"3"`（AD）
- options：維持 `["BC", "BD", "AD", "AC"]`
- 預計 SQLite explanation：保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率亦使死亡給付成本估計較高，因此答案為AD。

## 六、ID2654 預計修正摘要

- question_id：2654
- 現行 `correct_answer`：`"1"`（高）
- 預計 `correct_answer`：`"3"`（一樣）
- options：維持 `["高", "不一定", "一樣", "低"]`
- 預計 SQLite explanation：選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。

## 七、正式執行注意事項

本次核准的備份檔名與腳本內建預設備份檔名不同。未來若經 ChatGPT 明確核准執行 `--apply`，必須明確傳入本次兩個備份路徑：

```text
python tools/apply_existing_question_corrections_2664_2654.py --apply --json-backup backups/all_questions_before_existing_corrections_2664_2654_20260716.json --database-backup backups/insurance_exam_before_existing_corrections_2664_2654_20260716.db
```

在取得 ChatGPT 明確核准前，不得執行上述命令。正式執行後仍須驗證題數不變、非目標題未變、SQLite `integrity_check = ok`，並另行執行 Web 顯示驗證。
