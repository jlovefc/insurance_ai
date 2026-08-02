# JY unit04 Q36／Q38 補題 ID mapping 計畫

## 一、目的與限制

本文件依已核准的版本化草案，規劃 P.95 Q36、Q38 的補題內容與 ID mapping。本文件不代表正式補題，不修改 `all_questions.json`、SQLite 或 correction ledger。

## 二、前置裁定

- Q36 已核准以《保險法》第13條及審查時點限定題意，並可與 ID81、2596、2402 並存。
- Q38 已核准以市場商品型態及主管機關商品分類限定題意。
- Q38 已核准將「意外險」改為正式用語「傷害保險」。
- Q26、Q28、Q30 已先規劃 ID4142、4143、4144，因此 Q36、Q38 接續使用4145、4146。

## 三、ID 分配規則

- 目前 `all_questions.json` 與 SQLite 最大 ID 均為4141。
- ID4142至4144已保留給本批核准的 Q26、Q28、Q30。
- Q36、Q38依序規劃 ID4145、4146。
- 不重用缺號，不插入既有 ID；JSON 與 SQLite 必須使用相同 ID。
- 正式補入前若最大 ID 或占用狀態改變，本計畫失效並須重新 mapping。

## 四、ID mapping

| source | proposed_new_id | source_answer | inclusion_status | evidence／draft |
|---|---:|---:|---|---|
| P.95 Q36 | 4145 | 3 | `planned_only_not_applied` | `docs/answer_audit/jy_unit04_q36_q38_versioned_question_draft_20260716.md` |
| P.95 Q38 | 4146 | 2 | `planned_only_not_applied` | `docs/answer_audit/jy_unit04_q36_q38_versioned_question_draft_20260716.md` |

## 五、擬補入內容

### ID4145／P.95 Q36

- subject：`B 保險實務-分類`
- unit：`04 人身保險意義、功能、分類`
- content：`依審查日有效之《保險法》第13條規定，人身保險包括下列哪四類？`
- options：`["生存保險、死亡保險、生死合險、傷害保險", "人壽保險、傷害保險、健康保險、投資型保險", "人壽保險、健康保險、傷害保險、年金保險", "生存保險、死亡保險、生死合險、年金保險"]`
- correct_answer：`"3"`
- explanation：`依審查日有效之《保險法》第13條規定，人身保險包括人壽保險、健康保險、傷害保險及年金保險，因此答案為第3項。投資型保險依商品性質分為投資型人壽保險或投資型年金保險，並非第13條之外的獨立第五類。`

### ID4146／P.95 Q38

- subject：`B 保險實務-分類`
- unit：`04 人身保險意義、功能、分類`
- content：`依人身保險市場的商品型態及主管機關商品分類，下列哪些屬於人身保險商品？ A.傷害保險；B.健康保險；C.投資型保險商品；D.責任保險`
- options：`["AB", "ABC", "BC", "BCD"]`
- correct_answer：`"2"`
- explanation：`傷害保險與健康保險均屬《保險法》第13條所列人身保險類別；投資型保險亦屬人身保險商品，依商品性質分為投資型人壽保險或投資型年金保險。責任保險則屬財產保險，因此答案為ABC。投資型保險並不是第13條之外的獨立第五類。`

## 六、正式補入前必要條件

1. 建立涵蓋 ID4142至4146的受控補題腳本。
2. 腳本檢查 JSON／SQLite 最大 ID 仍為4141，且五個目標 ID 均不存在。
3. 再次檢查完整題幹與選項不存在完全相同版本。
4. dry-run 後確認 JSON 與 SQLite SHA-256 不變。
5. 建立 JSON 與 SQLite 備份並驗證 hash、大小及 DB完整性。
6. 取得明確 `--apply` 核准後才可同步補入。
7. 補入後驗證題數、內容、其他題目不變及 SQLite `integrity_check = ok`。
8. 建立 closeout、更新 ledger並完成 Web 驗證。

## 七、禁止事項

- 不得將本文件視為已補入。
- 不得未經 dry-run 與備份直接執行補題。
- 不得僅更新單一正式資料來源。
- 不得在 `--apply` 明確核准前修改正式題庫。
