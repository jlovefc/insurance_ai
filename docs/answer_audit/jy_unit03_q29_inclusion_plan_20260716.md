# JY unit03 Q29 補題 ID mapping 計畫

## 一、目的與限制

本文件只規劃 `MISS-20260716-0008`（JY P.90 Q29）版本化題目的補入 ID mapping，不代表已正式補題。

本階段未修改 `all_questions.json`、SQLite、output JSON、platform 程式或 correction ledger，亦未建立補題腳本。

## 二、前置審核結論

- Q29 已完成官方法規與版本時點佐證。
- 原稿答案 `1` 的核心概念獲官方規範支持。
- 原稿未標示法源與時點，且混合分紅／不分紅商品規範，因此不逐字補入。
- 版本化題目草案已核准進入 ID mapping。
- 核准版將考點限定為金管會民國113年7月16日發布、同年11月1日生效之不分紅人壽保險商品銷售文件規範。

## 三、唯讀檢查結果

| 檢查項目 | 結果 |
|---|---:|
| `all_questions.json` 題數 | 4,127 |
| `all_questions.json` 最大 ID | 4140 |
| SQLite `questions` 題數 | 4,140 |
| SQLite `questions` 最大 ID | 4140 |
| 核准版題幹與選項完全相同的 JSON 題目 | 0 |
| 核准版題幹完全相同的 SQLite 題目 | 0 |
| ID4141 是否已存在 | 否 |
| SQLite `integrity_check` | `ok` |

因此目前未見 ID 衝突，也未發現完全相同題幹與選項。

## 四、ID 分配規則

- 新題 ID 從目前 `max(id) + 1` 開始。
- 不重用缺號，不插入既有 ID。
- `all_questions.json` 與 SQLite 使用同一個新 ID。
- 正式套用前須再次檢查最大 ID、題數、題幹重複及 ID 是否仍未被占用。

## 五、ID mapping

| case_id | source_page | source_question_no | proposed_new_id | subject | unit | evidence_file | inclusion_status |
|---|---|---:|---:|---|---|---|---|
| `MISS-20260716-0008` | P.90 | 29 | 4141 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `docs/corrections/p90_q29_jy_missing_candidate_20260716.md` | `planned_only_not_applied` |

## 六、擬補入題目內容

- proposed_new_id：`4141`
- case_id：`MISS-20260716-0008`
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：`依金融監督管理委員會民國113年7月16日發布、同年11月1日生效之金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務時，下列有關銷售文件之敘述何者正確？`
- options：`["不得單獨強調保費預定利率", "得以保單報酬率與銀行存款報酬率比較作為主要招攬訴求", "無須說明本保險不參加紅利分配及無紅利給付項目", "得將保費預定利率作為唯一銷售重點"]`
- correct_answer：`"1"`
- explanation：`依金融監督管理委員會民國113年7月16日金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務，其銷售文件不得單獨強調保費預定利率，亦不得以保單報酬率與其他金融商品比較等方式誤導保戶；銷售文件、保險單面頁及保險單條款並應明確說明本保險為不分紅保險單、不參加紅利分配且無紅利給付項目。該令自民國113年11月1日生效，因此答案為第1項。`
- evidence_file：`docs/corrections/p90_q29_jy_missing_candidate_20260716.md`
- law_support_file：`docs/answer_audit/jy_unit03_q29_official_law_support_20260716.md`
- draft_file：`docs/answer_audit/jy_unit03_q29_versioned_question_draft_20260716.md`

## 七、正式補入前必要條件

1. 明確核准本 ID mapping 與擬補入內容。
2. 建立預設 dry-run、僅 `--apply` 才寫入的受控補題腳本。
3. dry-run 檢查 ID4141 不存在、題幹與選項未重複，並確認正式題庫雜湊不變。
4. 備份當下的 `all_questions.json` 與 `platform/instance/insurance_exam.db`。
5. 核對備份大小、SHA-256 與 SQLite `integrity_check`。
6. 再次執行最終 dry-run。
7. 取得明確 `--apply` 核准後，才同步新增 JSON 與 SQLite。
8. 驗證 JSON 題數增加 1、SQLite 題數增加 1，既有題目不變且 SQLite `integrity_check = ok`。
9. 建立 apply closeout、更新 correction ledger 並提交。
10. 使用既有臨時 venv 完成 Web 顯示驗證與收版。

## 八、禁止事項

- 本文件不是正式補題結果。
- 不得以本文件視為 ID4141 已存在。
- 不得未經明確核准修改 `all_questions.json` 或 SQLite。
- 不得只修改 SQLite 而不同步 `all_questions.json`。
- 不得未備份、未 dry-run 或未驗證便執行正式補題。
