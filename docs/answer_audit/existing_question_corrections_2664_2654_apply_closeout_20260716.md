# ID2664 / ID2654 既有題正式修正收版

## 一、執行摘要

- 本次正式修正既有題 ID2664、ID2654。
- `all_questions.json` 與 SQLite `questions` 已同步更新兩題的 `correct_answer`。
- SQLite 兩題的 `explanation` 已更新為核准文字。
- 正式修正由受控腳本執行，差異比對確認僅 ID2664、ID2654 發生變更。

## 二、依據文件與工具

- `docs/answer_audit/existing_question_conflict_triage_2664_2654_20260716.md`
- `docs/corrections/id2664_jy_p90_q28_reserve_assumption_answer_correction_20260716.md`
- `docs/corrections/id2654_jy_p91_q49_dividend_interest_answer_correction_20260716.md`
- `docs/answer_audit/existing_question_corrections_2664_2654_pre_apply_check_20260716.md`
- `tools/apply_existing_question_corrections_2664_2654.py`

## 三、備份

- JSON 備份：`backups/all_questions_before_existing_corrections_2664_2654_20260716.json`
- SQLite 備份：`backups/insurance_exam_before_existing_corrections_2664_2654_20260716.db`
- SQLite 備份受 `.gitignore` 的 `*.db` 規則排除，不納入 Git。
- 正式修正前已確認兩份備份分別與當時正式檔 SHA-256 相同，且 SQLite 備份 `integrity_check = ok`。

## 四、修正結果

- `all_questions.json` 題數維持 4,124。
- SQLite `questions` 題數維持 4,137。
- SQLite `integrity_check = ok`。
- JSON 與 SQLite 的差異 ID 均僅為 2654、2664。
- 非目標題未變。

## 五、ID2664 修正明細

- `correct_answer`：`"1"` → `"3"`
- options 不變：`["BC", "BD", "AD", "AC"]`
- SQLite explanation 已更新為：

  > 保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率亦使死亡給付成本估計較高，因此答案為AD。

## 六、ID2654 修正明細

- `correct_answer`：`"1"` → `"3"`
- options 不變：`["高", "不一定", "一樣", "低"]`
- SQLite explanation 已更新為：

  > 選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。

## 七、Git 策略

- `all_questions.json` 是 tracked file，應提交。
- SQLite 正式 DB 已同步修正，但 `.db` 受 `.gitignore` 排除，不強制提交。
- 本批正式修正 commit 應包含：
  1. `all_questions.json`
  2. `docs/corrections/correction_ledger_20260716.md`
  3. `docs/answer_audit/existing_question_corrections_2664_2654_apply_closeout_20260716.md`

## 八、後續驗證

- 資料層修正與完整性檢查已完成。
- 後續仍需使用既有臨時 venv 啟動 Flask，驗證 ID2664、ID2654 的題幹、選項、答案與解析顯示。
- Web 驗證通過後，應另建 Web 驗證文件並獨立提交。
