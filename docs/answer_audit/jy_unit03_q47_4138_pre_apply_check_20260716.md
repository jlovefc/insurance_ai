# JY unit03 Q47 / ID4138 正式補題前安全檢查

## 一、檢查目的

本文件記錄 MISS-20260716-0013 / JY P.91 Q47 擬以 ID4138 補入正式題庫前的備份與最終 dry-run 結果。本階段未執行 `--apply`，亦未修改 `all_questions.json` 或正式 SQLite 資料庫。

## 二、備份資訊

| 類型 | 備份檔案 | 檔案大小 |
|---|---|---:|
| JSON | `backups/all_questions_before_q47_4138_inclusion_20260716.json` | 2,090,993 bytes |
| SQLite | `backups/insurance_exam_before_q47_4138_inclusion_20260716.db` | 3,194,880 bytes |

SQLite 備份受 `.gitignore` 的資料庫規則排除，不強制加入 Git。

## 三、SHA-256 檢查摘要

| 檔案 | SHA-256 |
|---|---|
| `all_questions.json` | `781b400d65ab9a7aeba8d66373219648a6405972b4685dc8137d54645e0376d9` |
| JSON 備份 | `781b400d65ab9a7aeba8d66373219648a6405972b4685dc8137d54645e0376d9` |
| `platform/instance/insurance_exam.db` | `bee7587e4b89c3347931105d68d6dc57ab03fcb1b81d92a0ccf748d02543870a` |
| SQLite 備份 | `bee7587e4b89c3347931105d68d6dc57ab03fcb1b81d92a0ccf748d02543870a` |

正式檔與各自備份的 SHA-256 完全一致。dry-run 前後再次計算正式 JSON 與 SQLite 的 SHA-256，結果均未改變。

## 四、SQLite 完整性檢查

- 備份資料庫 `PRAGMA integrity_check`：`ok`
- 正式資料庫 dry-run 後 `PRAGMA integrity_check`：`ok`

## 五、最終 dry-run 結果

執行命令：

```text
python tools/apply_missing_question_4138_q47.py
```

結果：成功。腳本以預設 dry-run 模式完成所有前置檢查，並明確回報 ID4138 未寫入。

- `all_questions.json` 題數：4,124（不變）
- SQLite `questions` 題數：4,137（不變）
- ID4138 於 `all_questions.json`：不存在
- ID4138 於 SQLite `questions`：不存在
- 未執行 `python tools/apply_missing_question_4138_q47.py --apply`

## 六、ID4138 預計補入摘要

- case_id：`MISS-20260716-0013`
- proposed_new_id：`4138`
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`保單紅利支付的方法有？`
- options：`["BCD", "ACD", "ABCD", "ABC"]`
- correct_answer：`"3"`
- explanation：`保單紅利支付方法包括購買增額繳清金額、積存方法、抵繳保費及現金支付方法，因此答案為ABCD。`
- evidence_file：`docs/corrections/p91_q47_jy_missing_candidate_20260716.md`

## 七、結論與下一步

正式題庫尚未修改，ID4138 尚未正式補入。下一步必須取得 ChatGPT 明確核准後，才可使用已建立且已核對的備份執行 `--apply`；未取得核准前不得修改 `all_questions.json` 或正式 SQLite 資料庫。
