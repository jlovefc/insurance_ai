# 既有題答案衝突唯讀盤點：ID 2664、ID 2654

## 一、檢查目的

本報告針對漏題候選等價題檢查所發現的兩組既有題答案衝突進行唯讀盤點：

1. ID 2664 對 ID 2197，對應 `MISS-20260716-0007`／JY P.90 Q28。
2. ID 2654 對 ID 2336，對應 `MISS-20260716-0014`／JY P.91 Q49。

目的在確認 JSON、SQLite、重複題與原稿證據之間的差異，評估是否應進入正式修正審核。本次不裁定最終答案、不修改題庫、不更新 correction ledger，也不將任何題目直接列為 `ready_to_fix`。

## 二、檢查範圍與方法

### 2.1 資料來源

- `docs/answer_audit/missing_question_equivalence_check_20260716.md`
- `docs/answer_audit/missing_question_equivalence_review_decision_20260716.md`
- `docs/corrections/correction_ledger_20260716.md`
- `docs/corrections/p90_q28_jy_missing_candidate_20260716.md`
- `docs/corrections/p91_q49_jy_missing_candidate_20260716.md`
- `all_questions.json`
- `platform/instance/insurance_exam.db`／SQLite `questions`

### 2.2 唯讀檢查

- 讀取 JSON 的 ID 2664、2197、2654、2336 完整正式欄位。
- 以 SQLite URI `mode=ro` 讀取四題的 subject、unit、content、options、correct_answer、explanation、difficulty 與 is_important。
- 比較題幹正規化後的文字、選項概念與順序、答案所指選項及解析。
- 對照人工目視原稿紀錄的頁碼、題號、右側答案欄與人工校核說明。
- SQLite `questions` 題數為 4,137，`PRAGMA integrity_check = ok`。

## 三、ID 2664 詳細盤點

### 3.1 `all_questions.json` 與 SQLite 正式內容

| 欄位 | JSON ID 2664 | SQLite ID 2664 |
|---|---|---|
| subject | 保險實務 | 保險實務 |
| unit | 第四章 人身保險的構造 | 第四章 人身保險的構造 |
| content | 保險公司對於責任準備金之提存方式往往採取較穩健的作法，採比保單價值準備金 A 較低之預定利率；B 較高之預定利率；C 較低之預定死亡率；D 較高之預定死亡率 | 與 JSON 相同 |
| options | `["BC", "BD", "AD", "AC"]` | 與 JSON 相同（以 JSON 字串儲存） |
| correct_answer | `"1"` | `"1"` |
| explanation | JSON schema 無此欄 | 「穩健提存責任準備金：採較高預定利率（B）會使準備金較低，不穩健；應採較低預定利率（A錯）及較高預定死亡率（D）。依題選BC（較高預定利率、較低預定死亡率）為穩健作法。」 |

JSON 與 SQLite 的核心題目欄位一致。SQLite explanation 內部存在明顯矛盾：前段指出 B「不穩健」並描述應採較低預定利率與較高預定死亡率，概念對應 AD；末段卻選 BC。文字中的「A錯」亦與前句「應採較低預定利率」互相衝突。

### 3.2 與 ID 2197 的同題／等價題比較

| 欄位 | ID 2664 | ID 2197 |
|---|---|---|
| 題幹 | 責任準備金穩健提存，A低利率、B高利率、C低死亡率、D高死亡率 | 同一題幹；僅空白、標點及部分字形不同 |
| 選項順序 | 1 BC、2 BD、3 AD、4 AC | A BC、B BD、C AD、D AC |
| correct_answer | 1＝BC | C＝第三項AD |
| unit | 第四章 人身保險的構造 | 永達線上題庫-實務 |

判定：ID 2664 與 ID 2197 為同題／等價格式版。題幹敘述、A至D子敘述及四個組合選項的順序皆一致；只有選項標記使用數字或字母、空白、標點、字形及 unit 不同。兩筆答案所指概念直接衝突。

### 3.3 與 P.90 Q28 原稿差異

- 原稿題號：JY P.90 Q28。
- 原稿作答選項：1 BC、2 BD、3 AD、4 AC。
- 原稿右側答案欄：3，即 AD。
- ID 2664：答案 1，即 BC。
- ID 2197：答案 C，即第三項 AD，與原稿所指選項一致。
- 差異：ID 2664 與原稿在相同選項順序下相差兩個答案位置，且答案概念由 AD 變為 BC。

### 3.4 初步品質判斷

- issue_type：`wrong_answer`、`duplicate_conflict`、`manual_review`。
- 嚴重度：高。錯誤若成立，會直接使 Web 作答判定與解析誤導使用者。
- 信心：高（衝突存在）；最終答案修正仍需 ChatGPT 審核。
- 可能原因：重複題匯入時答案欄轉換錯誤，並由錯誤答案衍生自相矛盾的解析。
- 是否可直接修正：否。本報告是唯讀 triage，未取得正式答案修正核准。

## 四、ID 2654 詳細盤點

### 4.1 `all_questions.json` 與 SQLite 正式內容

| 欄位 | JSON ID 2654 | SQLite ID 2654 |
|---|---|---|
| subject | 保險實務 | 保險實務 |
| unit | 第四章 人身保險的構造 | 第四章 人身保險的構造 |
| content | 如要保人選擇以儲存生息之方式給付紅利之後，當被保險人死亡時，保險人所給付之保險金額較原保險金額為 | 與 JSON 相同 |
| options | `["高", "不一定", "一樣", "低"]` | 與 JSON 相同（以 JSON 字串儲存） |
| correct_answer | `"1"` | `"1"` |
| explanation | JSON schema 無此欄 | 「以儲存生息方式給付紅利，紅利累積生息後加計於保險金額，被保險人身故時給付金額將高於原保險金額。」 |

JSON 與 SQLite 的核心題目欄位一致。ID 2654 的答案 1 指「高」，SQLite explanation 也支持「高」，因此該筆內部一致；衝突發生在原稿及另一同題 ID 2336。

### 4.2 與 ID 2336 的同題／等價題比較

| 欄位 | ID 2654 | ID 2336 |
|---|---|---|
| 題幹 | 儲存生息給付紅利後，死亡時給付的保險金額較原保險金額為何 | 同一題幹；僅部分字形不同 |
| 選項順序 | 1 高、2 不一定、3 一樣、4 低 | A 高、B 不一定、C 一樣、D 低 |
| correct_answer | 1＝高 | C＝第三項一樣 |
| explanation | 累積紅利加計後，給付金額高於原保險金額 | 保險人所給付的保險金額較原保險金額一樣 |
| unit | 第四章 人身保險的構造 | 第四章 人身保險的構造 |

判定：ID 2654 與 ID 2336 為同題／等價格式版。題幹、選項概念、選項順序及 unit 均相同；只有選項標記與字形不同。兩筆不僅答案衝突，SQLite explanations 亦支持互斥結論。

### 4.3 與 P.91 Q49 原稿差異

- 原稿題號：JY P.91 Q49。
- 原稿選項順序：1 高、2 一樣、3 低、4 不一定。
- 原稿右側答案欄：2，即「一樣」。
- ID 2654 選項順序不同，答案 1 指「高」。
- ID 2336 答案 C 指「一樣」，與原稿答案概念一致。
- 差異：比較時必須依答案所指文字而非只比答案字串；ID 2654 指「高」，原稿及 ID 2336 均指「一樣」。

題幹使用「所給付之保險金額」；ID 2654 解析將累積紅利視為加計於死亡時總給付，原稿人工校核則區分原死亡保險金額與另行累積的紅利。此語意差異可能是答案分歧的來源，正式修正前需由 ChatGPT 確認教材定義與題幹語境。

### 4.4 初步品質判斷

- issue_type：`wrong_answer`、`duplicate_conflict`、`manual_review`。
- 嚴重度：高。相同題目在正式題庫存在互斥答案與互斥解析。
- 信心：高（衝突存在）；對 ID 2654 是否為錯誤答案的最終裁定需人工審核題意。
- 可能原因：不同來源對「保險金額」與「死亡時總給付」概念的解釋不同，或匯入時沿用不同答案版本。
- 是否可直接修正：否。本報告不做正式答案裁定。

## 五、是否需要 PDF 截圖

目前不需要使用者重新提供 PDF 截圖，原因如下：

- `docs/corrections/p90_q28_jy_missing_candidate_20260716.md` 已記錄人工目視 P.90 Q28，右側答案欄為 3。
- `docs/corrections/p91_q49_jy_missing_candidate_20260716.md` 已記錄人工目視 P.91 Q49，右側答案欄為 2。
- 兩份證據均記錄完整題幹、選項、答案與人工校核說明，足以完成衝突 triage。

如後續審核者要求把原稿畫面直接封存於修正證據，才需重新提供包含題幹、全部選項與右側答案欄的 P.90 Q28、P.91 Q49 截圖；這不是本次盤點的阻塞條件。

## 六、是否可進入正式修正流程

兩題均可進入「正式修正審核流程」，但尚不可直接執行修正：

| question_id | 可進入修正審核 | 可直接改題庫 | 待審事項 |
|---:|---|---|---|
| 2664 | 是 | 否 | 確認原稿答案3／AD為正式依據；決定是否同步修正答案與自相矛盾解析 |
| 2654 | 是 | 否 | 確認「保險金額」的教材語境；決定ID2654答案／解析是否應改為「一樣」 |

在 ChatGPT 完成答案與題意裁定前，兩題只應維持 `manual_review`／修正候選，不得標記 `ready_to_fix`，也不得修改 `all_questions.json` 或 SQLite。

## 七、下一步建議

1. 將本報告交由 ChatGPT 審核，分別裁定 ID 2664 與 ID 2654 的正式答案概念。
2. 對 ID 2664，重點審查同題 ID 2197、原稿答案 3／AD 及 ID 2664 自相矛盾的 explanation。
3. 對 ID 2654，重點審查原稿與 ID 2336 所指「一樣」，以及 ID 2654 把累積紅利解釋為總給付增加的語意差異。
4. 經裁定確有錯誤後，分別建立獨立修正證據文件，再更新 correction ledger 為 `confirmed_by_source`；只有取得明確修正內容後才進入 `ready_to_fix`。
5. 正式修正前備份 JSON 與 SQLite，使用範圍受控腳本同步修改，驗證題數不變、重複題關係、SQLite 完整性與 Web 顯示。
6. 建議未來增加自動化檢查：對正規化題幹相同且選項概念相同的題目，比較「答案所指選項文字」而非答案字串；發現不一致時自動列為 `duplicate_conflict`，但不得自動改答案。

## 八、執行過的唯讀檢查

- `git status -sb`、`git rev-parse HEAD`
- PowerShell唯读解析`all_questions.json`
- SQLite URI `mode=ro` 查詢四個目標 ID、題數與 `PRAGMA integrity_check`
- 讀取兩份原稿確認紀錄及兩份等價題決策文件

本次未修改 SQLite、`all_questions.json`、output JSON、platform 程式、correction ledger 或既有證據文件。
