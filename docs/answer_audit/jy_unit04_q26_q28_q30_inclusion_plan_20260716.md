# JY unit04 Q26／Q28／Q30 補題 ID mapping 草案

## 一、目的與限制

本文件只規劃 JY P.94 Q26、Q28、Q30 的補題內容與 ID mapping，不代表已正式補題。不得以本文件直接修改 `all_questions.json` 或 SQLite，也不得在未經審核前建立或執行補題腳本。

## 二、前置審核

- 三題原稿題幹、四項敘述、作答選項及右側答案欄均已完成視覺確認。
- 三題均有個別 evidence file。
- 全題庫等價題檢查未見完全相同或足以覆蓋的正式題目。
- 等價題審核決策允許三題進入補題前規劃。
- 本次再次唯讀確認：`all_questions.json` 題數4,128、最大 ID 4141；SQLite `questions` 題數4,141、最大 ID 4141，`integrity_check = ok`。
- ID4142、4143、4144 目前均不存在於 SQLite；正式補入前仍須由受控腳本再次檢查 JSON 與 SQLite。

## 三、ID 分配規則

- 新題 ID 自 `all_questions.json` 目前 `max(id)+1` 開始。
- 不重用缺號，不插入既有 ID。
- JSON 與 SQLite 使用同一組新 ID。
- 實際補入前若最大 ID 已改變，本 mapping 失效，必須重新規劃。

## 四、建議 ID mapping

| source | case | proposed_new_id | source_answer | inclusion_status | evidence_file |
|---|---|---:|---:|---|---|
| P.94 Q26 | 個人功能組合題 | 4142 | 4 | `planned_only_not_applied` | `docs/corrections/p94_q26_jy_personal_function_missing_candidate_20260716.md` |
| P.94 Q28 | 社會功能組合題 | 4143 | 4 | `planned_only_not_applied` | `docs/corrections/p94_q28_jy_social_function_missing_candidate_20260716.md` |
| P.94 Q30 | 國家功能組合題 | 4144 | 1 | `planned_only_not_applied` | `docs/corrections/p94_q30_jy_national_function_missing_candidate_20260716.md` |

## 五、擬補入內容

### ID4142／P.94 Q26

- subject：`B 保險實務-分類`
- unit：`04 人身保險意義、功能、分類`
- content：`人身保險對個人的功能有哪些？ A.後顧無憂、晚景可恃；B.安定就業、穩定發展；C.保證信用、有利投資；D.享受優惠、稅捐減免`
- options：`["AB", "BC", "CD", "ABCD"]`
- correct_answer：`"4"`
- explanation：`後顧無憂、晚景可恃，安定就業、穩定發展，保證信用、有利投資，以及享受優惠、稅捐減免，均屬教材列舉之人身保險對個人的功能，因此答案為ABCD。`

### ID4143／P.94 Q28

- subject：`B 保險實務-分類`
- unit：`04 人身保險意義、功能、分類`
- content：`人身保險對社會有那些功能？ A.透過再保、拓展外交；B.互助共濟、社會安寧；C.鼓勵儲蓄、平均財富；D.促進教育、提高素質`
- options：`["AB", "AC", "BC", "BCD"]`
- correct_answer：`"4"`
- explanation：`互助共濟、社會安寧，鼓勵儲蓄、平均財富，以及促進教育、提高素質，均屬教材列舉之人身保險對社會的功能；透過再保、拓展外交屬對國家的功能，因此答案為BCD。`

### ID4144／P.94 Q30

- subject：`B 保險實務-分類`
- unit：`04 人身保險意義、功能、分類`
- content：`人身保險對國家的功能有哪些？ A.形成資本，以增國富；B.穩定經濟，安定政治；C.大眾理財，豐富多元；D.健全經營，整合金融`
- options：`["ABD", "ABC", "ABCD", "ACD"]`
- correct_answer：`"1"`
- explanation：`形成資本、以增國富，穩定經濟、安定政治，以及健全經營、整合金融，均屬教材列舉之人身保險對國家的功能；大眾理財、豐富多元不屬本題列舉的國家功能，因此答案為ABD。`

## 六、正式補入前必要條件

1. ChatGPT 核准三題 content、options、correct_answer、explanation 與 ID mapping。
2. 補題前重新確認 JSON／SQLite 最大 ID 仍為4141，且4142-4144均不存在。
3. 再次檢查三題完整題幹與選項不存在完全相同版本。
4. 建立受控補題腳本，預設 dry-run，只有 `--apply` 才可寫入。
5. dry-run 通過並確認正式檔 SHA-256 不變。
6. 建立 JSON 與 SQLite 備份，驗證檔案大小、SHA-256 及 DB `integrity_check`。
7. 取得明確 `--apply` 核准後，才可同步新增 JSON 與 SQLite。
8. 驗證題數各增加3題、其他題目未變、SQLite `integrity_check = ok`。
9. 建立 apply closeout、更新 ledger、進行 Web 驗證。

## 七、禁止事項

- 本文件不是正式補題結果。
- 不得未經核准執行 ID4142-4144 補入。
- 不得只修改 SQLite 或只修改 JSON。
- 不得未備份就執行補題。
- 不得把 `planned_only_not_applied` 誤記為 `applied` 或 `ready_to_fix`。
