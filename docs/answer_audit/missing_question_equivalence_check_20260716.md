# 14 題漏題候選唯讀等價題檢查報告

## 一、檢查目的與限制

本報告依 `docs/answer_audit/missing_question_inclusion_rules_20260716.md`，針對 `MISS-20260716-0001` 至 `MISS-20260716-0014` 執行正式題庫唯讀等價題檢查。本次只搜尋 `all_questions.json` 與以 SQLite URI `mode=ro` 開啟的 `platform/instance/insurance_exam.db`之 `questions` 表；不補題、不修題庫、不變更漏題候選狀態，所有案例仍為 `confirmed_by_source / pending_inclusion_review`，不得改列 `ready_to_fix`。

## 二、資料來源

- 規則與盤點：`docs/answer_audit/missing_question_inclusion_rules_20260716.md`、`docs/corrections/correction_ledger_20260716.md`、`docs/answer_audit/jy_unit03_manual_review_closeout_20260716.md`
- 正式快照：`all_questions.json`（4,122 題）
- 正式執行資料：`platform/instance/insurance_exam.db`／`questions`（4,135 題；唯讀查詢；`integrity_check = ok`）
- 證據文件：
  - `docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md`
  - `docs/corrections/p89_q14_jy_premium_calculation_missing_candidate_20260716.md`
  - `docs/corrections/p90_q19_jy_missing_candidate_20260716.md`
  - `docs/corrections/p90_q22_jy_missing_candidate_20260716.md`
  - `docs/corrections/p90_q24_jy_missing_candidate_20260716.md`
  - `docs/corrections/p90_q28_jy_missing_candidate_20260716.md`
  - `docs/corrections/p90_q29_jy_missing_candidate_20260716.md`
  - `docs/corrections/p90_q31_jy_reserve_missing_candidate_20260716.md`
  - `docs/corrections/p90_q32_jy_missing_candidate_20260716.md`
  - `docs/corrections/p91_q35_jy_missing_candidate_20260716.md`
  - `docs/corrections/p91_q36_jy_missing_candidate_20260716.md`
  - `docs/corrections/p91_q46_jy_missing_candidate_20260716.md`
  - `docs/corrections/p91_q47_jy_missing_candidate_20260716.md`
  - `docs/corrections/p91_q49_jy_missing_candidate_20260716.md`

## 三、檢查方法

1. 正規化題幹的空白、標點、全半形數字與常見 OCR 差異，搜尋完整題幹及具識別力的關鍵句。
2. 交叉搜尋選項關鍵字、組合選項、答案概念、subject 與 unit；題號不作為唯一依據。
3. 檢查題目是否被拆分、改寫、調換選項順序，或因「選項在前、敘述在後」而失去直接題幹匹配。
4. 對候選既有題比較題幹、選項語意及答案所指概念；數字情境、問法或法規時點不同時，不直接判定等價。
5. 同一候選 ID 在兩個正式來源皆找到時，分別確認其存在；本報告所列主要候選均同時存在於 JSON 與 SQLite。答案以各來源儲存值呈現，字母答案另註明所指選項。

分類定義：A＝未見同題或等價題，可進入 ID mapping 規劃；B＝有高度相似題但等價性需人工確認；C＝正式題庫已有同題或等價題，不補入；D＝資料不足。

## 四、逐題檢查結果

### MISS-20260716-0001（P.89 Q12）

- source_answer：2
- evidence_file：`docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md`
- 搜尋關鍵字：`一萬名30歲男性`、`100萬死亡保險`、`死亡率千分之二`、`每人純保費`
- `all_questions.json`：未找到相同數值與完整題幹；相似候選 ID 3811、2671、2349。
- SQLite：與 JSON 相同，候選 ID 3811、2671、2349 均存在。
- 疑似等價題：ID 3811 亦以人數、死亡率、保額計算每人純保費，但年齡、人數、保額、死亡率及選項均不同；ID 2671、2349 為相同收支相等／純保費概念的其他數值題。
- 分類：**B－疑似等價題，需人工確認**。
- 建議下一步：由使用者決定「相同公式但數值情境不同」是否允許並存；決定前不得補入。

### MISS-20260716-0002（P.89 Q14）

- source_answer：1（ABC）
- evidence_file：`docs/corrections/p89_q14_jy_premium_calculation_missing_candidate_20260716.md`
- 搜尋關鍵字：`30歲女性死亡率千分之三`、`一千名`、`2千萬`、`6000萬`、`每人6萬`
- `all_questions.json`：ID 2662 與原題正規化題幹及組合選項相同，答案 1；ID 2178 為近乎相同題幹，以字母選項表示且答案 A（即第一項）。
- SQLite：同樣找到 ID 2662、2178。
- 疑似等價題：ID 2662 為同題；ID 2178 為格式改寫版。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：在 ledger 記錄既有對應 ID，不建立新題。

### MISS-20260716-0003（P.90 Q31）

- source_answer：3（責任準備金）
- evidence_file：`docs/corrections/p90_q31_jy_reserve_missing_candidate_20260716.md`
- 搜尋關鍵字：`純保險費扣除已經過的危險保費`、`提存保管`、`特設的帳簿`、`責任準備金`
- `all_questions.json`：ID 2334、2652 均含相同定義；選項順序不同，答案分別為 A、1，皆指「責任準備金」。
- SQLite：同樣找到 ID 2334、2652。
- 疑似等價題：兩題均為原題「選項在前、敘述在後」結構的正規化／重排版本。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：記錄 ID 2334、2652 為既有等價題，不新增。

### MISS-20260716-0004（P.90 Q19）

- source_answer：3（便宜）
- evidence_file：`docs/corrections/p90_q19_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`預定死亡率降低`、`定期保險的保險費`、`便宜`
- `all_questions.json`：未找到相同題；ID 3814 問預定利率降低，ID 2451、2647、3777 問年金保險與死亡率，因素或商品方向不同。
- SQLite：結果與 JSON 相同，未見同題或可直接視為等價的改寫題。
- 疑似等價題：上述題目僅共享「預定因素影響保費」概念，問法與正確方向不同，不構成同題。
- 分類：**A－可補入候選**。
- 建議下一步：納入後續 inclusion plan 與 ID mapping；補入前仍須使用者明確核准。

### MISS-20260716-0005（P.90 Q22）

- source_answer：1（AB）
- evidence_file：`docs/corrections/p90_q22_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`民國88年起簽發之人壽保險單`、`繳費之解約金`、`分期付款期滿解約金`
- `all_questions.json`：ID 2649 為同題（含 OCR 字差），答案 1；ID 2648 為縮寫版；ID 2661、2174、2343 為敘述或選項重排版，正確概念均為 AB。
- SQLite：同樣找到上述候選。
- 疑似等價題：ID 2649 可直接認定同題；其餘為等價改寫。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：記錄 ID 2649 為主對應，其他 ID 作重複題線索。

### MISS-20260716-0006（P.90 Q24）

- source_answer：3（AC）
- evidence_file：`docs/corrections/p90_q24_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`保單價值準備金之計算`、`危險發生率`、`附加費用率`、`行庫每月初牌告`
- `all_questions.json`：ID 3007 題幹及選項相同，答案 3（AC）。
- SQLite：同樣找到 ID 3007，內容與答案一致。
- 疑似等價題：ID 3007 為同題。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：將漏題候選改記為既有題對應線索；本次不改 ledger。

### MISS-20260716-0007（P.90 Q28）

- source_answer：3（AD）
- evidence_file：`docs/corrections/p90_q28_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`責任準備金之提存方式`、`較低之預定利率`、`較高之預定死亡率`
- `all_questions.json`：ID 2664 題幹與選項順序相同但答案為 1（BC），與原稿衝突；ID 2197 為同題字母選項版，答案 C，即第三項 AD，與原稿一致。
- SQLite：同樣存在 ID 2664、2197，且答案狀態相同。
- 疑似等價題：兩者均為同題；ID 2664 顯示既有重複題答案衝突，不能以新增題解決。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：另案將 ID 2664 登記為 `duplicate_conflict / wrong_answer` 疑點並回原稿複核；不得新增第三份同題。

### MISS-20260716-0008（P.90 Q29）

- source_answer：1
- evidence_file：`docs/corrections/p90_q29_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`不分紅保險單之招攬廣告`、`不得單獨強調保險費預定利率`、`預期保險單紅利金額`、`銀行定存利率比較`
- `all_questions.json`：未找到包含上述關鍵敘述的同題；僅有其他招攬廣告法規題（如 ID 3611、2035、2043），規範主題不同。
- SQLite：結果與 JSON 相同，未見同題或等價改寫。
- 疑似等價題：無；一般招攬廣告題不足以視為本題等價。
- 分類：**A－可補入候選**。
- 建議下一步：先執行教材版本／`outdated_law` 專門審查；僅在保留教材時點語境且使用者核准後，才進入 ID mapping。

### MISS-20260716-0009（P.90 Q32）

- source_answer：4（ACD）
- evidence_file：`docs/corrections/p90_q32_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`保險法所稱之各種責任準備金包括`、`賠款準備金`、`差額準備金`、`未滿期保費準備金`、`特別準備金`
- `all_questions.json`：ID 2653 為同題，組合選項順序不同，答案 3 所指 ACD；ID 2335 為字母選項版，答案 C，亦指 ACD。
- SQLite：同樣找到 ID 2653、2335。
- 疑似等價題：兩者均與原題等價，差異僅選項呈現及順序。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：記錄既有 ID；如需法規時點審查，應針對既有題另案處理。

### MISS-20260716-0010（P.91 Q35）

- source_answer：3（民國八十八年）
- evidence_file：`docs/corrections/p91_q35_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`最低責任準備金的提存`、`民國幾年起`、`二十五年滿期生死合險修正制`
- `all_questions.json`：未找到同一「起始年度」題；ID 3788、2666、2344 等詢問特定保險採何種修正制，並非詢問制度開始年份。
- SQLite：結果與 JSON 相同，未見同題或等價改寫。
- 疑似等價題：相關題只共享責任準備金制度概念，考點不同。
- 分類：**A－可補入候選**。
- 建議下一步：先完成教材版本／`outdated_law` 審查，再決定是否列入 inclusion plan。

### MISS-20260716-0011（P.91 Q36）

- source_answer：1（民國九十五年）
- evidence_file：`docs/corrections/p91_q36_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`二十年繳費終身保險修正制`、`最低責任準備金`、`始自民國`
- `all_questions.json`：ID 3787、3788、2666、2344 等包含相同修正制名稱，但詢問「何種保險採何種修正制」；未找到詢問起始年度的同題。
- SQLite：結果與 JSON 相同。
- 疑似等價題：上述題目主題高度相近，但考點由制度選擇改為歷史年度，不能自動認定等價。
- 分類：**A－可補入候選**。
- 建議下一步：先完成 `outdated_law` 與教材時點審查；通過後才進入 ID mapping。

### MISS-20260716-0012（P.91 Q46）

- source_answer：1（AC）
- evidence_file：`docs/corrections/p91_q46_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`民國八十一年度起`、`保單紅利係指`、`利差紅利`、`費差紅利`、`死差紅利`
- `all_questions.json`：ID 2689 為同題，選項順序不同，答案 2 所指 AC；ID 2367 為字母選項版，答案 B，亦指 AC。
- SQLite：同樣找到 ID 2689、2367。
- 疑似等價題：兩者均為同題／等價格式版。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：記錄既有 ID；教材版本或法規疑義另案審查，不新增。

### MISS-20260716-0013（P.91 Q47）

- source_answer：3（ABCD）
- evidence_file：`docs/corrections/p91_q47_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`保單紅利支付的方法`、`購買增額繳清`、`積存方法`、`抵繳保費`、`現金支付`
- `all_questions.json`：未找到相同組合題；ID 107 問「何者非教材列舉的方式」，其選項含現金支付、購買增額繳清保險、抵繳保費及「存入指定帳戶」；ID 3795、3796 分別測試抵繳保費與增額繳清的個別效果。
- SQLite：同樣找到 ID 107、3795、3796。
- 疑似等價題：ID 107 與原題皆測試紅利支付方式且選項高度重疊，但一題問全部方法、一題問非列舉方法，且「積存方法」與「存入指定帳戶」是否等價不明。
- 分類：**B－疑似等價題，需人工確認**。
- 建議下一步：人工決定 ID 107 是否已涵蓋同一教材考點，以及同概念不同問法是否允許並存；決定前不得補入。

### MISS-20260716-0014（P.91 Q49）

- source_answer：2（一樣）
- evidence_file：`docs/corrections/p91_q49_jy_missing_candidate_20260716.md`
- 搜尋關鍵字：`選擇以儲存生息之方式給付紅利`、`被保險人死亡`、`較原保險金額`
- `all_questions.json`：ID 2654 為同題但選項重排後答案為 1（高），與原稿衝突；ID 2336 為同題字母選項版，答案 C，即「一樣」，與原稿一致。
- SQLite：同樣存在 ID 2654、2336，答案狀態相同。
- 疑似等價題：兩者均為同題；ID 2654 顯示既有重複題答案衝突。
- 分類：**C－正式題庫已存在，不補入**。
- 建議下一步：另案將 ID 2654 登記為 `duplicate_conflict / wrong_answer` 疑點並回原稿複核；不得新增同題。

## 五、總結表

| 分類 | 題數 | case_id |
|---|---:|---|
| A 可補入候選 | 4 | MISS-20260716-0004、0008、0010、0011 |
| B 疑似等價題，需人工確認 | 2 | MISS-20260716-0001、0013 |
| C 正式題庫已存在，不補入 | 8 | MISS-20260716-0002、0003、0005、0006、0007、0009、0012、0014 |
| D 資料不足 | 0 | 無 |
| **合計** | **14** |  |

重要風險：C 類中的 Q28（ID 2664 對 ID 2197）與 Q49（ID 2654 對 ID 2336）各發現既有同題答案衝突。這是既有題庫校驗議題，不應以新增漏題候選處理。本次未變更任何題目或 ledger。

## 六、下一階段建議

1. 先由使用者審核本報告的 A／B／C 分類，尤其確認「相同計算公式但不同數字」及「相同概念但正反問法不同」的重複容許標準。
2. B 類維持 `pending_inclusion_review`，完成等價性人工判斷前不得補入。
3. C 類不得補入；Q28、Q49 的既有答案衝突應另建證據與校驗流程，不直接修改。
4. A 類中的 Q29、Q35、Q36 必須先完成教材版本／`outdated_law` 審查並保留時點語境。
5. 僅在 A 類獲使用者核准後，下一階段才建立 `docs/answer_audit/missing_question_inclusion_plan_20260716.md`，進行 ID mapping、備份、同步與 rollback 規劃；本次未建立該文件。

## 七、唯讀檢查紀錄

- `git status -sb`、`git branch --show-current`、`git rev-parse HEAD`
- `rg` 搜尋 `all_questions.json` 的題幹關鍵句、選項關鍵字與候選 ID 周邊內容
- Python 唯讀載入 `all_questions.json`，執行正規化與相似度候選搜尋
- Python 以 SQLite URI `mode=ro` 查詢 `questions` 表、題數及 `PRAGMA integrity_check`
- `Get-Content -Raw -Encoding UTF8` 讀取證據文件與 ledger

本報告產出前狀態為 `## main...origin/main`；未修改 SQLite、`all_questions.json`、output JSON、platform、correction ledger 或既有證據文件。
