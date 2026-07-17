# JY unit03 Q47 補題 ID mapping 草案

## 一、目的與限制

本文件只規劃 `MISS-20260716-0013`／P.91 Q47 的補題 ID mapping 與擬補入內容，不正式補題，不修改 `all_questions.json`、SQLite、output JSON、platform 或 correction ledger。

本文件是待審草案，不代表 Q47 已取得新 ID 或已寫入正式題庫。正式補入前仍須取得 ChatGPT 明確核准。

## 二、前置裁定

- 裁定文件：`docs/answer_audit/jy_unit03_q47_equivalence_decision_20260716.md`
- Q47 是正向完整組合題，測試保單紅利支付方法的完整清單。
- ID107 是反向排除題，且「積存方法」不等同於「存入要保人指定帳戶」；Q47 可與 ID107 並存。
- ID3795、ID3796 只分別測試個別紅利支付方式的名稱或效果，屬部分重疊題，不足以覆蓋 Q47。
- correction ledger 狀態：`confirmed_by_source / pending_inclusion_mapping`。
- 本裁定只允許進入 ID mapping 草案，不等同正式補題核准。

## 三、唯讀前置檢查

| 檢查項目 | 結果 |
|---|---|
| `all_questions.json` 題數 | 4,124 |
| `all_questions.json` 最大 ID | 4,137 |
| SQLite `questions` 題數 | 4,137 |
| SQLite `questions` 最大 ID | 4,137 |
| JSON ID4138 | 不存在 |
| SQLite ID4138 | 不存在 |
| JSON 完全相同題幹 | 未找到 |
| JSON 完全相同題幹與選項 | 未找到 |
| SQLite 完全相同題幹 | 未找到 |

檢查結論：兩個正式來源的最大 ID 均為 4137，ID4138 尚未占用；Q47 完整題幹與完整題幹＋選項組合均未出現。依當下資料，proposed ID 無直接衝突風險。

## 四、ID 分配規則

1. 新題 ID 從 `all_questions.json` 當下 `max(id)+1` 開始。
2. 本次當下最大 ID 為 4137，因此 proposed ID 為 4138。
3. 不重用缺號。
4. 不插入既有 ID。
5. JSON 與 SQLite 必須使用相同 ID。
6. 正式補入前須再次檢查最大 ID 與 ID4138 是否仍未占用；若 repository 或正式 DB 已新增其他題，mapping 必須重新審核，不得強行使用 4138。

## 五、ID mapping 草案

| case_id | source_page | source_question_no | source_answer | proposed_new_id | subject | unit | evidence_file | inclusion_status | notes |
|---|---|---:|---:|---:|---|---|---|---|---|
| `MISS-20260716-0013` | P.91 | 47 | 3 | 4138 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `docs/corrections/p91_q47_jy_missing_candidate_20260716.md` | `planned_only_not_applied` | 已裁定可與 ID107 並存；ID3795、ID3796 僅部分重疊。本 ID 尚未正式分配。 |

Mapping：`MISS-20260716-0013` → proposed ID `4138`。

## 六、擬補入題目內容草案

- proposed_new_id：4138
- subject：B 保險實務-分類
- unit：03 保險費架構、解約金、準備金、保單紅利
- content：保單紅利支付的方法有？
- options：`["BCD", "ACD", "ABCD", "ABC"]`
- correct_answer：`"3"`
- explanation：保單紅利支付方法包括購買增額繳清金額、積存方法、抵繳保費及現金支付方法，因此答案為ABCD。

正式資料格式原則：

- `all_questions.json` 應維持現有 schema，只包含既有正式欄位，不任意加入 explanation 或來源 metadata。
- SQLite `questions` 應使用相同 id、subject、unit、content、options、correct_answer，並保存上述 explanation。
- 原稿來源與裁定鏈保留於 evidence、decision、plan 及後續 closeout 文件。

## 七、正式補入前必要條件

1. ChatGPT 核准 proposed ID4138 與上述完整題目內容。
2. 再次唯讀確認 JSON／SQLite 最大 ID、ID4138 空缺及完全相同題幹不存在。
3. 備份當下 `all_questions.json`。
4. 備份當下 `platform/instance/insurance_exam.db`，並確認備份 `integrity_check = ok`。
5. 記錄正式檔與備份檔大小及 SHA-256。
6. 建立只允許新增 ID4138 的受控補題腳本；預設 dry-run，只有明確 `--apply` 才可寫入。
7. dry-run 驗證不修改 JSON／SQLite，且正式檔 SHA-256 前後一致。
8. 取得正式 apply 核准後，同步新增 JSON 與 SQLite。
9. 驗證 JSON 題數增加 1、SQLite 題數增加 1、非目標題未變及 SQLite `integrity_check = ok`。
10. 驗證 Web 題幹、選項、答案、解析、subject 與 unit。
11. 建立 apply closeout、更新 ledger，並依核准範圍 commit／push tracked files。

## 八、禁止事項

1. 本文件不是補題執行結果，不得視為 ID4138 已正式分配或已補入。
2. 不得未經 ChatGPT 核准修改 `all_questions.json` 或 SQLite。
3. 不得只改 SQLite、不改 JSON，或只改 JSON、不改 SQLite。
4. 不得未備份、未 dry-run 或未驗證 ID 衝突便執行補題。
5. 不得修改 output JSON、platform、既有證據文件或其他題目。
6. 本階段不得建立或執行補題腳本。

## 九、下一步

將本 mapping 草案交由 ChatGPT 審核。若核准 proposed ID4138 與題目內容，下一個安全階段才是建立「只支援 dry-run、尚不 apply」的受控補題腳本。
