# 漏題候選補入規則與執行方案

## 一、目的

本文件定義 `MISS-20260716-0001` 至 `MISS-20260716-0014` 是否可補入正式題庫的判斷標準，以及未來新增至 `all_questions.json` 與 SQLite 時必須遵守的執行、驗證、備份及回復規則。

本文件是補題前的治理規格，不是補題核准文件。建立本文件不代表 14 題已獲准收錄，也不得據此將任何案例由 `pending_inclusion_review` 直接改為 `ready_to_fix`。

## 二、目前狀態

- 14 題均已由人工原稿目視或截圖確認題幹、選項及答案。
- 14 題均已有獨立 `evidence_file`，並已登記 correction ledger。
- 目前狀態：`confirmed_by_source`。
- 下一狀態：`pending_inclusion_review`。
- 14 題尚未補入 SQLite 或 `all_questions.json`，也尚未取得正式題庫 ID。
- JY unit03 本輪剩餘 manual_review：0 題。
- 法規或歷史時點風險題仍只依 JY 教材版本登記，尚未完成專門法規審查。

## 三、補入前必要條件

每一題必須逐題通過以下條件，任一項未完成即不得進入正式補入：

1. 已有可追溯的 `evidence_file`，包含原稿檔案、頁碼定位、題號、完整題幹、選項及答案。
2. 已登記 correction ledger，且 `case_id`、來源、答案、證據文件及狀態互相一致。
3. 已完成 SQLite 與 `all_questions.json` 的唯讀等價題檢查，並留下搜尋依據與結果。
4. 已確認該題屬於正式題庫預定收錄範圍，而非僅供教材參考、重複練習或不應納入的歷史題。
5. 已判斷是否屬教材版本語境或具有 `outdated_law` 風險；有風險者須完成獨立版本審查，或明確採教材版本收錄政策。
6. 題幹、選項順序、答案位置及可見解析均已定稿，不得含 OCR 亂碼、截斷或相鄰文字污染。
7. 已制定新題 ID mapping、資料備份、受控同步、驗證與 rollback 方案。
8. 已產出逐題補入計畫，明確列出「補入／排除／延後」決定與理由。
9. 使用者已明確核准實際補入題目清單、ID mapping 與執行範圍。

## 四、不得補入條件

符合下列任一條件時，該題不得補入，應維持 `pending_inclusion_review` 或改列延後審查：

1. 正式題庫已存在同一題，僅有空白、標點、全半形或選項標記差異。
2. 正式題庫已有語意等價的改寫題，且產品需求不需要重複收錄。
3. 題幹、選項、答案欄或解析仍不完整，或版面歸屬仍有疑義。
4. 答案與原稿、教材版本語境或專門法規審查結果存在重大疑義。
5. 尚未定義、核准或驗證新題 ID。
6. 尚未建立 `all_questions.json` 與 SQLite 的同步方法。
7. 尚未建立正式資料備份與可驗證的 rollback 方法。
8. 無法確保新增範圍只包含已核准的漏題候選。
9. 無法驗證新增後題數、ID 唯一性、欄位結構或 Web 顯示。

## 五、等價題檢查規則

### 5.1 查詢來源

等價題檢查必須同時唯讀搜尋：

- `all_questions.json`
- `platform/instance/insurance_exam.db` 的 `questions` 表
- 必要時參考 output JSON 或 raw text 作來源線索，但不得以中間資料直接判定正式題庫不存在同題。

### 5.2 搜尋方法

每題至少執行以下多層搜尋：

1. 題幹完整正規化比對：移除空白、常見標點、全半形差異及選項標記後比較。
2. 題幹關鍵句搜尋：選取能表達核心條件的連續文字，不得只搜尋一般性名詞。
3. 選項關鍵字搜尋：比對關鍵名詞、數值、年份、組合選項及其排列。
4. 答案概念搜尋：確認是否存在換問「何者正確／不正確」、正反命題或不同選項順序的等價題。
5. `unit` 搜尋：先在相同單元查找，再擴大到相同 subject 及全題庫。
6. 題目條件與答案方向比對：不得僅因題幹相似就視為同題，也不得忽略否定詞、年度、保險種類或條件差異。

`source_question_no` 只用於定位原稿，不得作為正式題庫對應或等價判定的唯一依據。

### 5.3 結果分類

每題等價檢查結果應標記為：

- `no_equivalent_found`：未找到同題或等價題，可進入其他補入條件審查。
- `exact_duplicate`：已存在同題，不得新增。
- `equivalent_rewrite`：存在等價改寫題，需使用者決定是否保留兩種版本。
- `similar_but_distinct`：題目相似但條件、問法或答案概念不同，須記錄差異證據。
- `uncertain`：無法可靠判斷，維持 `pending_inclusion_review`。

## 六、新題 ID 分配規則

1. 由 Codex 以唯讀方式查詢 `all_questions.json` 所有有效題目目前最大 `id`。
2. 同時查詢 SQLite `questions.id` 最大值及 ID 衝突情形，確認兩個正式來源的 ID 空間是否一致。
3. 經核准的新題從核准基準的 `max(id) + 1` 開始連續分配。
4. 不重用歷史缺號、刪除題 ID 或未確認用途的空號。
5. 不插入、覆蓋或改動任何既有 ID。
6. 建立並審核 mapping 表：`MISS case_id → new_question_id`。
7. mapping 一經使用者核准，在同一批次內不得任意重排；若有題目退出，須明確決定是否保留未使用 ID，不得暗中改號。
8. 新增前再次檢查所有 mapping ID 在 JSON 與 SQLite 均不存在。

建議 mapping 表欄位：

| 欄位 | 說明 |
|---|---|
| `case_id` | 漏題候選案例 ID |
| `new_question_id` | 預定新題 ID |
| `equivalent_check` | 等價題檢查結果 |
| `inclusion_decision` | 補入／排除／延後 |
| `decision_reason` | 決定理由 |
| `approved_by_user` | 使用者核准狀態 |

## 七、all_questions.json 補入規則

每一筆核准新增題至少須包含並驗證：

- `id`：依核准 mapping 分配的唯一整數 ID。
- `subject`：依正式題庫既有分類格式填寫。
- `unit`：`03 保險費架構、解約金、準備金、保單紅利`，除非補入計畫另有來源證據。
- `content`：完整題幹，不得混入選項、答案或解析。
- `options`：依原稿順序保存完整選項，格式須符合既有 schema。
- `correct_answer`：使用既有題庫答案位置格式，並與原稿選項順序一致。
- `explanation`：若正式 JSON schema 已有此欄位，依原稿填入；原稿無解析時依既有空值規則留空。若目前 schema 沒有該欄位，不得為本批次任意改變全檔 schema。

來源 metadata 處理原則：

1. 先確認正式 JSON 既有 schema 是否支援 `source_file`、`source_page`、`source_question_no` 或其他來源欄位。
2. 若既有格式不支援，不得為單一批次任意新增 schema 欄位。
3. 不支援的來源資訊必須記錄在 correction ledger、mapping 表及補題 closeout 文件，以維持可追溯性。
4. 新增後必須確認 JSON 可完整解析、題數符合預期、ID 唯一且只有核准題目發生新增。

## 八、SQLite 同步規則

1. 不得只手工修改 SQLite，也不得讓 SQLite 與 `all_questions.json` 各自獨立新增。
2. 應使用明確、可重現、可審查且限制在核准 mapping 的腳本或受控流程同步。
3. 同步流程須先驗證所有新 ID 不存在，再以單一交易新增；任一題失敗時整批 rollback。
4. 寫入欄位必須與 `questions` 表實際 schema 相符，並與 JSON 的 ID、subject、unit、content、options、correct_answer 及 explanation 一致。
5. options 若存為 JSON 字串，必須可反序列化且順序與 JSON 快照相同。
6. 同步前後均須記錄 `questions` 題數；新增後題數增量必須等於實際核准新增題數。
7. 新增後逐題依 mapping 查詢完整資料，確認沒有改動既有題目。
8. 執行 `PRAGMA integrity_check`，結果必須為 `ok`。
9. 同步流程應支援 dry-run；只有明確 `--apply` 或等效核准開關才可寫入。

## 九、備份與 rollback 規則

正式補題前必須建立且不得覆蓋既有備份：

- `all_questions.json`
- `platform/instance/insurance_exam.db`

每個備份必須記錄：

- 備份檔案路徑
- 建立時間與批次 ID
- 檔案大小
- SHA-256 或等效 hash
- SQLite 備份的 `PRAGMA integrity_check` 結果
- 對應的補題計畫與 mapping 文件

rollback 規則：

1. 補題前須先驗證備份可讀、JSON 可解析、SQLite integrity check 為 `ok`。
2. 若新增過程失敗，SQLite 交易必須 rollback，不得留下部分新增題。
3. 若寫入後驗證失敗，停止 Web 驗證與 commit，依核准 rollback 方案恢復 JSON 與 SQLite。
4. 恢復後重新驗證題數、hash、SQLite integrity check 及核准題目不存在。
5. rollback 操作與結果必須記錄於 closeout 或 incident 文件，不得無紀錄覆蓋正式資料。

## 十、Web 驗證規則

正式補題後，在未 commit 前至少驗證：

1. 所有實際核准新增題均可依新 ID 查詢或由預期頁面存取。
2. 題幹完整，沒有截斷、OCR 亂碼或解析文字污染。
3. 選項數量、內容及順序與原稿一致。
4. 正確答案位置與原稿一致，作答判定正確。
5. subject 與 unit 顯示正確。
6. explanation 依核准內容顯示；無原稿解析時符合既定空值行為。
7. 法規或歷史時點題清楚保留教材版本語境，不得呈現為未標示版本的現行法結論。
8. 新增題不影響既有題目抽題、查詢、作答或解析功能。

驗證不得造成非必要的 quiz session 或其他資料表寫入；若必須執行會寫入的流程，須另行核准並在驗證前後比對資料表。

## 十一、outdated_law／教材版本語境規則

Q29、Q32、Q35、Q36、Q46 涉及法規或歷史時點。即使原稿與答案已確認，本階段也只能依 JY 教材版本登記：

1. 不得未經專門法規審查，就自行將答案改成現行法答案。
2. 等價題檢查必須把教材年度、法規時點及題目條件納入比較。
3. 若決定保留教材題，需在可支援的位置清楚記錄教材版本或歷史時點。
4. 若平台只允許現行法題目，應將案例延後或建立版本化策略，不得無痕改寫原稿答案。
5. 法規審查結果必須記錄依據版本、生效日期、審查人及採用決定。

## 十二、正式補入階段建議

後續應分為三個獨立、安全且可審查的階段：

### 階段 1：唯讀等價題檢查

- 同時搜尋 SQLite 與 `all_questions.json`。
- 逐題產出關鍵句、選項概念、候選對應與分類結果。
- 不修改任何正式資料，也不改變 `pending_inclusion_review` 狀態。

### 階段 2：補題計畫與 ID mapping

- 根據等價題結果決定補入、排除或延後。
- 唯讀查詢最大 ID，產出預定 mapping、欄位內容、題數變化、備份與 rollback 計畫。
- 交由使用者逐題或整批核准；此階段仍不得修改正式題庫。

### 階段 3：使用者核准後正式補入

- 只處理使用者核准的案例與 mapping。
- 先備份，再以受控流程同步 JSON 與 SQLite。
- 完成資料一致性、integrity check、Web 驗證及 closeout 後，才可 commit 與 push。

## 十三、禁止事項

1. 不得因建立本規則文件就直接補題。
2. 不得未備份就修改 `all_questions.json` 或 SQLite。
3. 不得未完成等價題檢查就新增題目。
4. 不得把 `pending_inclusion_review` 直接改為 `ready_to_fix`。
5. 不得自行修改法規或歷史時點題的原稿答案。
6. 不得只修改 JSON 或只修改 SQLite。
7. 不得用 output JSON 直接覆蓋正式題庫。
8. 不得重用缺號、覆蓋既有 ID 或未經核准變更 mapping。
9. 不得把改寫題、正反問法或相似但不同條件的題目草率合併。
10. 不得在驗證失敗、題數不符、integrity check 非 `ok` 或工作樹含非核准變更時 commit／push。
