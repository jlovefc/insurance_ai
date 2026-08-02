# ID3840 正式修正前安全檢查

## 一、檢查目的

本文件記錄 JY P.93 Q13／既有題 ID3840 正式修正前的備份、完整性檢查與最終 dry-run 結果。此次只建立備份並執行唯讀 dry-run，未執行 `--apply`，未修改正式題庫。

## 二、依據

- 修正證據：`docs/corrections/id3840_jy_p93_q13_electronic_policy_answer_option_correction_20260716.md`
- 版本審查：`docs/answer_audit/id3840_electronic_policy_version_review_20260716.md`
- correction ledger：`docs/corrections/correction_ledger_20260716.md`
- 受控腳本：`tools/apply_id3840_electronic_policy_correction.py`
- 執行前 HEAD：`29624b473e1d66d41c4cb8f23b6d6364f3c9d783`

## 三、預計修正摘要

- question_id：3840
- content：維持「目前人身保險業所簽發的保單為」
- current options：`["僅提供紙本保單", "可利用網路投保來簽發電子保單", "不限紙本保單", "僅選項"]`
- expected options：`["僅提供紙本保單", "可利用網路投保來簽發電子保單", "不限紙本保單", "僅選項2、3為真"]`
- current correct_answer：`"2"`
- expected correct_answer：`"4"`
- current SQLite explanation：空字串
- expected SQLite explanation：`依保險業辦理電子商務相關規範，保險業可辦理符合規定之網路投保，並得依要保人指定方式交付紙本或電子保單。因此保單不限於紙本，且符合規範時可透過網路投保簽發電子保單，第2、3項為真，答案為第4項。電子保單仍須符合適用商品、身分驗證、要保人同意及其他相關規範。`

## 四、備份資訊

| 類型 | 正式檔 | 備份檔 | 備份大小 | SHA-256 比對 |
|---|---|---|---:|---|
| JSON | `all_questions.json` | `backups/all_questions_before_id3840_correction_20260716.json` | 2,040,991 bytes | 一致 |
| SQLite | `platform/instance/insurance_exam.db` | `backups/insurance_exam_before_id3840_correction_20260716.db` | 3,194,880 bytes | 一致 |

SHA-256：

- JSON 正式檔與備份：`3ba98d380cbdbab916fc82471a1a0a2d7243b467d55eed4b4f87e9c71ad36e65`
- SQLite 正式檔與備份：`72591d08af68e1aef2df1ef27b97a317fc6f44f3c748b11c0848fe32d9f3ae15`
- 備份 SQLite `integrity_check`：`ok`
- 備份 SQLite questions 題數：4,141
- 備份 SQLite 最大 ID：4,141

SQLite 備份受 `.gitignore` 的資料庫規則排除，不得使用 `git add -f` 強制納入版控。

## 五、最終 dry-run

執行命令：

```text
python tools/apply_id3840_electronic_policy_correction.py
```

未執行：

```text
python tools/apply_id3840_electronic_policy_correction.py --apply
```

結果：

- dry-run：成功
- 腳本確認 JSON ID3840 存在且目前答案為 `"2"`
- 腳本確認 SQLite ID3840 存在且目前答案為 `"2"`
- 腳本確認兩邊目前選項與受控前置值一致
- 腳本列印預計選項、答案及 SQLite 解析變更
- JSON SHA-256 前後一致
- SQLite SHA-256 前後一致
- ID3840 未被寫入或修改

## 六、正式資料狀態

- `all_questions.json` 題數：4,128，未變更
- `all_questions.json` 最大 ID：4,141，未變更
- SQLite questions 題數：4,141，未變更
- SQLite questions 最大 ID：4,141，未變更
- ID3840 `correct_answer`：仍為 `"2"`
- ID3840 第4選項：仍為「僅選項」
- output JSON：未修改
- platform 程式：未修改
- correction ledger：未修改

## 七、下一步門檻

正式修正前必須取得明確核准，之後才可執行：

```text
python tools/apply_id3840_electronic_policy_correction.py --apply \
  --json-backup backups/all_questions_before_id3840_correction_20260716.json \
  --database-backup backups/insurance_exam_before_id3840_correction_20260716.db
```

正式執行後仍須驗證：

1. JSON 與 SQLite 題數均不變。
2. 只修改 ID3840。
3. 選項、答案與 SQLite 解析符合核准內容。
4. SQLite `integrity_check = ok`。
5. 建立 apply closeout 並更新 correction ledger。
6. 完成 Web 顯示驗證後才可收版。

## 八、結論

備份、SHA-256、SQLite 完整性及最終 dry-run 均通過。ID3840 尚未正式修正；下一步必須取得明確 `--apply` 核准。
