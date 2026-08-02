# ID3835 題目結構正式修正收版

## 一、執行摘要

- 本次正式修正 JY P.93 Q8／既有題 ID3835。
- `all_questions.json` 與 SQLite `questions` 已同步修正題幹及選項結構。
- `correct_answer` 維持原稿與系統一致的 `"3"`，SQLite `explanation` 維持空字串。
- 正式修正由受控腳本執行，差異比對確認僅 ID3835 發生變更。

## 二、依據文件與工具

- `docs/corrections/id3835_jy_p93_q8_option_pollution_correction_20260716.md`
- `docs/answer_audit/id3835_correction_pre_apply_check_20260716.md`
- `docs/corrections/correction_ledger_20260716.md`
- `tools/apply_id3835_question_structure_correction.py`

## 三、備份

- JSON 備份：`backups/all_questions_before_id3835_correction_20260716.json`
- SQLite 備份：`backups/insurance_exam_before_id3835_correction_20260716.db`
- 正式修正前兩份備份分別與當時正式檔 SHA-256 相同。
- SQLite 備份 `integrity_check = ok`。
- SQLite 備份受 `.gitignore` 的 `*.db` 規則排除，不納入 Git。

## 四、執行方式

```text
python tools/apply_id3835_question_structure_correction.py --apply \
  --json-backup backups/all_questions_before_id3835_correction_20260716.json \
  --database-backup backups/insurance_exam_before_id3835_correction_20260716.db
```

腳本在寫入前驗證目標 ID、現有題幹、現有選項、答案、題數、最大 ID、備份雜湊及 SQLite 完整性；寫入後驗證目標資料及非目標題目差異。

## 五、修正結果

- `all_questions.json` 題數維持 4,128。
- SQLite `questions` 題數維持 4,141。
- JSON 最大 ID 維持 4,141。
- SQLite 最大 ID 維持 4,141。
- JSON 差異 ID 僅 3835。
- SQLite `questions` 差異 ID 僅 3835。
- 非目標題目未變。
- SQLite `integrity_check = ok`。

## 六、ID3835 修正明細

- subject：`B 保險實務-分類`（不變）
- unit：`04 人身保險意義、功能、分類`（不變）
- content 修正前：`人身保險的意義，就是由？`
- content 修正後：`人身保險的意義，就是由下列何者出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活？`
- options 修正前：`["許多窮苦的人們", "少數的社會熱心人士", "千千萬萬的人", "保險公司的員工 出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活"]`
- options 修正後：`["許多窮苦的人們", "少數的社會熱心人士", "千千萬萬的人", "保險公司的員工"]`
- `correct_answer`：維持 `"3"`。
- SQLite `explanation`：維持空字串。

## 七、錯誤處理結論

- 錯誤類型：`option_pollution`、`truncated_question`、`ocr_parse_error`。
- 原稿採「句首＋四個主詞選項＋共同句尾」版面，轉換流程誤將共同句尾併入第4選項。
- 本案不是答案錯誤，不標記為 `wrong_answer`。
- 正式修正只重建題幹與選項邊界，未改變題意及答案。

## 八、Git 策略

- `all_questions.json` 是 tracked file，應提交。
- SQLite 正式 DB 已同步修正，但 `.db` 受 `.gitignore` 排除，不強制提交。
- 本批正式修正 commit 應包含：
  1. `all_questions.json`
  2. `docs/corrections/correction_ledger_20260716.md`
  3. `docs/answer_audit/id3835_question_structure_correction_apply_closeout_20260716.md`

## 九、後續驗證

- 資料層修正與完整性檢查已完成。
- 後續使用既有 repo 外臨時 venv 啟動 Flask，以唯讀端點驗證 ID3835 的題幹、選項、答案、解析、subject 與 unit。
- Web 驗證通過後，另建 Web 驗證文件並獨立提交。
