# ID3840 電子保單題正式修正收版

## 一、執行摘要

- 本次正式修正 JY P.93 Q13／既有題 ID3840。
- `all_questions.json` 與 SQLite `questions` 已同步修正選項及 `correct_answer`。
- SQLite `explanation` 已補入通過版本審查的核准文字。
- 正式修正由受控腳本執行，差異比對確認僅 ID3840 發生變更。

## 二、依據文件與工具

- `docs/corrections/id3840_jy_p93_q13_electronic_policy_answer_option_correction_20260716.md`
- `docs/answer_audit/id3840_electronic_policy_version_review_20260716.md`
- `docs/answer_audit/id3840_correction_pre_apply_check_20260716.md`
- `docs/corrections/correction_ledger_20260716.md`
- `tools/apply_id3840_electronic_policy_correction.py`

## 三、備份

- JSON 備份：`backups/all_questions_before_id3840_correction_20260716.json`
- SQLite 備份：`backups/insurance_exam_before_id3840_correction_20260716.db`
- 正式修正前兩份備份分別與當時正式檔 SHA-256 相同。
- SQLite 備份 `integrity_check = ok`。
- SQLite 備份受 `.gitignore` 的 `*.db` 規則排除，不納入 Git。

## 四、執行方式

```text
python tools/apply_id3840_electronic_policy_correction.py --apply \
  --json-backup backups/all_questions_before_id3840_correction_20260716.json \
  --database-backup backups/insurance_exam_before_id3840_correction_20260716.db
```

腳本在寫入前驗證目標 ID、現有選項、現有答案、題數、最大 ID、備份雜湊及 SQLite 完整性；寫入後驗證目標資料與非目標題目差異。

## 五、修正結果

- `all_questions.json` 題數維持 4,128。
- SQLite `questions` 題數維持 4,141。
- JSON 最大 ID 維持 4,141。
- SQLite 最大 ID 維持 4,141。
- JSON 差異 ID 僅 3840。
- SQLite `questions` 差異 ID 僅 3840。
- 非目標題目未變。
- SQLite `integrity_check = ok`。

## 六、ID3840 修正明細

- subject：`B 保險實務-分類`（不變）
- unit：`04 人身保險意義、功能、分類`（不變）
- content：`目前人身保險業所簽發的保單為`（不變）
- options 修正前：`["僅提供紙本保單", "可利用網路投保來簽發電子保單", "不限紙本保單", "僅選項"]`
- options 修正後：`["僅提供紙本保單", "可利用網路投保來簽發電子保單", "不限紙本保單", "僅選項2、3為真"]`
- `correct_answer`：`"2"` → `"4"`
- SQLite explanation 修正前：空字串
- SQLite explanation 修正後：

  > 依保險業辦理電子商務相關規範，保險業可辦理符合規定之網路投保，並得依要保人指定方式交付紙本或電子保單。因此保單不限於紙本，且符合規範時可透過網路投保簽發電子保單，第2、3項為真，答案為第4項。電子保單仍須符合適用商品、身分驗證、要保人同意及其他相關規範。

## 七、版本審查界線

- 電子保單適用時點審查已通過。
- 原稿答案第4項獲官方歷史函釋及審查日有效規範支持。
- 解析保留適用商品、身分驗證及要保人同意等限制，不將電子保單描述為無條件適用於所有人身保險商品。

## 八、Git 策略

- `all_questions.json` 是 tracked file，應提交。
- SQLite 正式 DB 已同步修正，但 `.db` 受 `.gitignore` 排除，不強制提交。
- 本批正式修正 commit 應包含：
  1. `all_questions.json`
  2. `docs/corrections/correction_ledger_20260716.md`
  3. `docs/answer_audit/id3840_electronic_policy_correction_apply_closeout_20260716.md`

## 九、後續驗證

- 資料層修正與完整性檢查已完成。
- 後續使用既有 repo 外臨時 venv 啟動 Flask，以唯讀端點驗證 ID3840 的題幹、選項、答案與解析顯示。
- Web 驗證通過後，另建 Web 驗證文件並獨立提交。
