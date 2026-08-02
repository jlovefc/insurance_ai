# ID3835 正式修正前安全檢查

## 一、檢查目的

本文件記錄 JY P.93 Q8／既有題 ID3835 正式修正前的備份、完整性檢查與最終 dry-run 結果。此次只建立備份並執行唯讀 dry-run，未執行 `--apply`，未修改正式題庫。

## 二、依據

- 修正證據：`docs/corrections/id3835_jy_p93_q8_option_pollution_correction_20260716.md`
- correction ledger：`docs/corrections/correction_ledger_20260716.md`
- 受控腳本：`tools/apply_id3835_question_structure_correction.py`
- 執行前 HEAD：`0d346b2049b9ab09b2b6c8b090ea65e13edcae12`

## 三、預計修正摘要

- question_id：3835
- current content：`人身保險的意義，就是由？`
- expected content：`人身保險的意義，就是由下列何者出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活？`
- current options：`["許多窮苦的人們", "少數的社會熱心人士", "千千萬萬的人", "保險公司的員工 出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活"]`
- expected options：`["許多窮苦的人們", "少數的社會熱心人士", "千千萬萬的人", "保險公司的員工"]`
- `correct_answer`：維持 `"3"`
- SQLite `explanation`：維持空字串

## 四、備份資訊

| 類型 | 正式檔 | 備份檔 | 備份大小 | SHA-256 比對 |
|---|---|---|---:|---|
| JSON | `all_questions.json` | `backups/all_questions_before_id3835_correction_20260716.json` | 2,041,002 bytes | 一致 |
| SQLite | `platform/instance/insurance_exam.db` | `backups/insurance_exam_before_id3835_correction_20260716.db` | 3,198,976 bytes | 一致 |

SHA-256：

- JSON 正式檔與備份：`a3fcd9873de0c4545c203f7d610076b1da15d0bef282c708fcd989bf7ed9fd7f`
- SQLite 正式檔與備份：`de366c6d248a0aadf9f5c9e6475ae5ef8f4b1c5b2b3977835ebbb4391b500cf0`
- 備份 SQLite `integrity_check`：`ok`
- 備份 SQLite questions 題數：4,141
- 備份 SQLite 最大 ID：4,141

SQLite 備份受 `.gitignore` 的資料庫規則排除，不得使用 `git add -f` 強制納入版控。

## 五、最終 dry-run

執行命令：

```text
python tools/apply_id3835_question_structure_correction.py
```

未執行：

```text
python tools/apply_id3835_question_structure_correction.py --apply
```

結果：

- dry-run：成功
- 腳本確認 JSON 與 SQLite 均存在 ID3835
- 腳本確認兩邊目前題幹與受污染選項符合受控前置值
- 腳本確認兩邊 `correct_answer` 均為 `"3"`
- 腳本確認 SQLite `explanation` 為空字串
- 腳本列印預計題幹與選項變更
- JSON SHA-256 前後一致
- SQLite SHA-256 前後一致
- ID3835 未被寫入或修改

## 六、正式資料狀態

- `all_questions.json` 題數：4,128，未變更
- `all_questions.json` 最大 ID：4,141，未變更
- SQLite questions 題數：4,141，未變更
- SQLite questions 最大 ID：4,141，未變更
- ID3835 `correct_answer`：仍為 `"3"`
- ID3835 第4選項：仍含共同題幹句尾
- output JSON：未修改
- platform 程式：未修改
- correction ledger：未修改

## 七、下一步門檻

正式修正前必須取得明確核准，之後才可執行：

```text
python tools/apply_id3835_question_structure_correction.py --apply \
  --json-backup backups/all_questions_before_id3835_correction_20260716.json \
  --database-backup backups/insurance_exam_before_id3835_correction_20260716.db
```

正式執行後仍須驗證：

1. JSON 與 SQLite 題數均不變。
2. 只修改 ID3835 的 `content` 與 `options`。
3. `correct_answer` 維持 `"3"`，SQLite `explanation` 維持空字串。
4. 非目標題目未變。
5. SQLite `integrity_check = ok`。
6. 建立 apply closeout 並更新 correction ledger。
7. 完成 Web 顯示驗證後才可收版。

## 八、結論

備份、SHA-256、SQLite 完整性及最終 dry-run 均通過。ID3835 尚未正式修正；下一步必須取得明確 `--apply` 核准。
