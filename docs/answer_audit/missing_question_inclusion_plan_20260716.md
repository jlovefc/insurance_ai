# 2 題漏題候選補入 ID mapping 草案

## 一、目的

本文件只規劃 `MISS-20260716-0004`／P.90 Q19 與 `MISS-20260716-0001`／P.89 Q12 的補入 ID mapping 及擬補入內容，不是正式補題執行結果。本次不修改 `all_questions.json`、SQLite、output JSON、platform 或 correction ledger，不建立補題腳本，也不將任何案例改列 `ready_to_fix`。

## 二、前置審核結論

- 14 題漏題候選中，目前只有 2 題經人工審核允許進入補題計畫。
- `MISS-20260716-0004`：可進入補題計畫；正式題庫未見同題或等價題。
- `MISS-20260716-0001`：可有條件進入補題計畫；相同純保費公式但數值情境不同，可視為不同計算題並存。
- `MISS-20260716-0001` 在正式補入前，仍須確認正式題庫不存在數值、保額、死亡率及選項均完全相同的版本。
- 其餘 12 題依 `docs/answer_audit/missing_question_equivalence_review_decision_20260716.md` 暫緩或不補入，不得納入本 mapping。

## 三、本次唯讀檢查結果與 ID 分配規則

### 3.1 唯讀檢查結果

| 檢查項目 | 結果 |
|---|---:|
| `all_questions.json` 題數 | 4,122 |
| `all_questions.json` 最大 ID | 4135 |
| SQLite `questions` 題數 | 4,135 |
| SQLite `questions` 最大 ID | 4135 |
| SQLite `PRAGMA integrity_check` | `ok` |
| Q19 完整題幹＋選項完全相同記錄 | JSON 0；SQLite 0 |
| Q12 完整題幹＋選項完全相同記錄 | JSON 0；SQLite 0 |
| ID 4136、4137 衝突 | JSON 無；SQLite 無 |

檢查結論：兩題在本次檢查時仍未存在完全相同題幹與選項；建議 ID 4136、4137 在兩個正式來源均未被占用，未見當下 ID 衝突。正式執行前仍須重新查詢最大 ID 與占用狀態，避免本草案核准期間出現新資料造成競爭。

### 3.2 ID 分配規則

1. 新題 ID 從 `all_questions.json` 本次最大 ID 4135 的下一號開始，即 `max(id) + 1`。
2. 不重用缺號，不插入既有 ID。
3. 依本計畫表順序連續分配 ID 4136、4137。
4. SQLite 必須與 `all_questions.json` 使用同一組新 ID。
5. 正式補入前必須重新唯讀檢查兩來源的最大 ID；若最大 ID 或占用狀態改變，本 mapping 作廢，須重新產生草案並交由使用者核准。

## 四、建議 ID mapping 表

| case_id | source_page | source_question_no | source_answer | proposed_new_id | subject | unit | evidence_file | inclusion_status | notes |
|---|---|---:|---:|---:|---|---|---|---|---|
| `MISS-20260716-0004` | P.90 | 19 | 3 | **4136** | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `docs/corrections/p90_q19_jy_missing_candidate_20260716.md` | `planned_only_not_applied` | 未見同題或等價題；可進入補題計畫。 |
| `MISS-20260716-0001` | P.89 | 12 | 2 | **4137** | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md` | `planned_only_not_applied` | 同公式但不同數字情境之純保費計算題；可有條件進入補題計畫，正式補入前仍須確認無完全相同數值版本。 |

## 五、擬補入題目內容草案

### 5.1 proposed_new_id 4136／MISS-20260716-0004

```text
proposed_new_id = 4136
subject = "B 保險實務-分類"
unit = "03 保險費架構、解約金、準備金、保單紅利"
content = "若預定死亡率降低，定期保險的保險費就會？"
options = ["一樣", "不一定", "便宜", "貴"]
correct_answer = "3"
explanation = "其他條件不變時，預定死亡率降低代表預期死亡給付成本下降，定期保險保費因而降低。"
```

內容依據：`docs/corrections/p90_q19_jy_missing_candidate_20260716.md`。題幹、選項及答案來自人工目視原稿；`explanation` 取自證據文件的人工校核說明，屬補題計畫草案說明，正式補入前須由使用者核准，不得任意改變題意。

### 5.2 proposed_new_id 4137／MISS-20260716-0001

```text
proposed_new_id = 4137
subject = "B 保險實務-分類"
unit = "03 保險費架構、解約金、準備金、保單紅利"
content = "一萬名30歲的男性各投保100萬的死亡保險（保險期間1年），若生命表顯示30歲男性死亡率為千分之二，請問每人該付多少純保費？"
options = ["1仟元", "2仟元", "3仟元", "4仟元"]
correct_answer = "2"
explanation = "10000 × 2/1000 = 20人\n20 × 1000000 / 10000 = 2000"
```

內容依據：`docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md`。題幹、選項、答案及計算解析均依人工目視原稿記錄。正式補入前須再次檢查是否存在完全相同數值版本。

### 5.3 schema 注意事項

- 現行 `all_questions.json` 題目結構包含 `id`、`subject`、`unit`、`content`、`options`、`correct_answer`，未普遍包含 `explanation`。
- 正式補入時不得擅自改變 JSON schema；如維持現行格式，JSON 僅寫入既有欄位，解析應同步至支援 `explanation` 的 SQLite 欄位，並在 closeout 文件記錄差異。
- 若使用者另行決定擴充 JSON schema，必須另案審核，不屬本計畫授權範圍。

## 六、正式補入前必要條件

1. 使用者明確核准本 ID mapping 與兩題內容草案。
2. 執行前重新查詢 `all_questions.json` 與 SQLite 最大 ID、ID 4136／4137 占用狀態及完全相同題目。
3. 補題前備份 `all_questions.json`，記錄路徑、大小及 hash。
4. 補題前備份 `platform/instance/insurance_exam.db`，記錄路徑、大小並執行完整性檢查。
5. 建立或使用範圍受控的補題腳本，只允許新增本計畫核准的兩題。
6. 先執行 dry-run，驗證 mapping、schema、題數預期與不修改既有題的限制。
7. 正式補入 `all_questions.json`。
8. 以同一組 ID 同步 SQLite。
9. 驗證 JSON 題數由 4,122 增加為 4,124，SQLite `questions` 題數由 4,135 增加為 4,137；若執行前基準已變動，應以重新核准的基準加 2 驗證。
10. 比對補入前後資料，確認除新增 ID 4136、4137 外，所有既有題均未修改。
11. 驗證 SQLite `integrity_check = ok`，並確認 JSON 與 SQLite 的 ID、題幹、選項及答案一致。
12. 啟動 Web 系統進行兩題題幹、選項、答案、解析及單元顯示驗證。
13. 建立補題 closeout 文件，記錄備份、執行、差異、驗證及 rollback 資訊。

## 七、Rollback 規劃要求

正式補題任務必須在執行前定義 rollback：若任一題資料錯誤、題數異常、SQLite 完整性失敗、JSON／SQLite 不一致或 Web 顯示異常，應停止後續提交，使用已記錄的備份還原兩個正式來源，再驗證題數、hash、SQLite 完整性及既有題資料。

## 八、禁止事項

1. 本文件不是補題執行結果，不得視為兩題已補入。
2. 本文件中的 4136、4137 是待審 `proposed_new_id`，不是已分配的正式 ID。
3. 不得未經使用者核准修改正式題庫。
4. 不得只修改 SQLite 而不修改 `all_questions.json`，或使用不同 ID。
5. 不得未備份即執行補題。
6. 不得跳過 dry-run、題數驗證、既有題差異檢查、SQLite 完整性檢查或 Web 驗證。
7. 不得在本計畫加入其餘 12 題候選。
8. 不得將任何漏題候選改列 `ready_to_fix`。
