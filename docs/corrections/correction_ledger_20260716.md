# 保險題庫錯題修正總表

- 建立日期：2026-07-16
- 適用範圍：`C:\insurance_ai` 保險題庫之錯題追蹤、來源複核、修正準備與修正後驗證
- 流程依據：`docs/answer_audit/source_based_chapter_unit_question_audit_workflow_20260716.md`
- 首筆案例依據：`docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md`
- 本文件只負責登記與追蹤；登記不代表已修改正式題庫。

## 一、文件目的

本文件作為保險題庫的統一錯題修正總表，用來追蹤所有經人工目視、原稿比對、系統偵測或後續校驗發現的題庫問題。

每筆案例應保留可追溯來源、系統現況、預期修正、錯誤類型與處理狀態，使後續人工複核、批次修正及修正後驗證均有一致依據。未經來源確認的項目只能列為待查，不得因登記於本表就直接修改題庫。

## 二、修正原則

1. 不得只憑系統答案或 AI 推測直接修題。
2. 每一題正式修正前，必須有原稿、PDF、Word、法規或其他可追溯依據。
3. SQLite 與 `all_questions.json` 必須同步修正，並在修正後驗證一致性。
4. `output` 來源 JSON 原則上先不直接修改，除非後續建立並核准可重現的重建流程。
5. 已刪除題、未分類題與正式題需分開處理，不得混合計入同一修正批次。
6. 法規時效題必須標記依據版本、生效日期及教材適用時間。
7. 改寫題、相似題與原題必須分別登記，不得只依題幹關鍵字合併。
8. `ready_to_fix` 以前的狀態均不得直接進入正式修正。

## 三、錯誤類型代碼

| 代碼 | 定義 |
|---|---|
| `wrong_answer` | 答案欄位錯誤，與已確認原稿或依據不一致 |
| `ocr_parse_error` | OCR 或 PDF 解析錯誤，造成文字、欄位或結構異常 |
| `option_pollution` | 選項被解析文字、題幹或相鄰內容污染 |
| `explanation_missing` | 原稿有解析，但系統解析缺漏 |
| `explanation_pollution` | 解析被併入選項或題幹，或混入其他內容 |
| `truncated_question` | 題幹截斷 |
| `truncated_explanation` | 解析截斷 |
| `duplicate_conflict` | 重複題或高度相似題的答案衝突 |
| `source_mapping_error` | 題目對應到錯誤的來源、頁面、題號或改寫版本 |
| `outdated_law` | 法規時效、版本或適用日期存在疑義 |
| `manual_review` | 無法可靠自動判斷，需人工目視或專業判斷 |

單一案例可以同時登記多個錯誤類型。錯誤類型只描述已觀察到的問題，不取代來源證據或人工確認。

## 四、狀態代碼

| 狀態 | 定義 |
|---|---|
| `suspected` | 已發現疑點，但尚未找到或確認來源 |
| `source_found` | 已找到可能來源，尚待完成原稿比對 |
| `confirmed_by_source` | 已由原稿、法規或其他可追溯來源確認問題 |
| `ready_to_fix` | 證據及預期修正內容完整，已通過修正前審查 |
| `fixed` | SQLite 與正式 JSON 已依核准內容完成修正 |
| `verified` | 已驗證資料一致性及必要的 Web 顯示／行為 |
| `deferred` | 因來源不清、版本疑義或其他原因延後處理 |

狀態必須依實際進度更新。`confirmed_by_source` 不等於已修正；`fixed` 不等於已完成驗證。

## 五、目前已確認案例

| case_id | question_id | subject | unit | source | source_page | source_question_no | current_answer | source_answer | expected_answer | error_types | status | next_status | fix_target | notes |
|---|---:|---|---|---|---|---:|---|---|---|---|---|---|---|---|
| CORR-20260716-0001 | 3815 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.89 | 18 | 3 | 1 | 1 | `wrong_answer`, `ocr_parse_error`, `option_pollution`, `explanation_missing` | `confirmed_by_source` | `ready_to_fix` | `all_questions.json` id=3815；SQLite `questions.id`=3815 | 原稿右側答案欄為 1。系統誤將解析尾端「何者正確答案就會是 3」抓為正式答案，且第 4 選項被解析文字污染。已於第一批 JY 單元逐題原稿校對試跑再次確認；尚未修改正式題庫。不得混同 SQLite ID 2670。 |
| CORR-20260716-0002 | 3785 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 34 | 4 | 4 | 4 | `option_pollution`, `truncated_question` | `confirmed_by_source` | `ready_to_fix` | `all_questions.json` id=3785；SQLite `questions.id`=3785 | 原稿確認第 4 選項為 ABCD，「，而有差別。」屬於題幹句尾。系統目前將「，而有差別。」錯誤併入第 4 選項，造成題幹截斷與選項污染。此題不是答案錯誤，不得標記為 `wrong_answer`；尚未修改正式題庫。 |
| CORR-20260716-0003 | 2664 | 保險實務 | 第四章 人身保險的構造 | JY P.90 Q28 | P.90 | 28 | 1 | 3 | 3 | `wrong_answer`, `duplicate_conflict`, `explanation_conflict` | `fixed` | `applied` | `all_questions.json` id=2664；SQLite `questions.id`=2664（已修正） | 原稿與等價題 ID2197 均支持 AD；已由受控腳本同步修正答案與 SQLite 解析。 |
| CORR-20260716-0004 | 2654 | 保險實務 | 第四章 人身保險的構造 | JY P.91 Q49 | P.91 | 49 | 1 | 2 | 3 | `wrong_answer`, `duplicate_conflict`, `explanation_conflict` | `fixed` | `applied` | `all_questions.json` id=2654；SQLite `questions.id`=2654（已修正） | 原稿與等價題 ID2336 均支持「一樣」；已由受控腳本同步修正答案與 SQLite 解析。 |

### CORR-20260716-0001 證據文件

- 個案修正紀錄：`docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md`
- 第一批試跑報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 原稿：`input/JY-人身保險.pdf` P.89 第 18 題
- 流程規格：`docs/answer_audit/source_based_chapter_unit_question_audit_workflow_20260716.md`
- 試跑狀態：`confirmed_by_source`。
- 後續狀態：`ready_to_fix`；此狀態只表示證據與修正建議已具備，尚未修改 SQLite 或 `all_questions.json`，不得標記為 `fixed`。

### CORR-20260716-0002 證據與建議修正

- 個案修正紀錄：`docs/corrections/id3785_jy_p90_reserve_option_pollution_correction_20260716.md`
- 人工目視工作表：`docs/answer_audit/jy_unit03_manual_review_worklist_20260716.md`，JY-U03-MR-010
- 第一批試跑報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 原稿：`input/JY-人身保險.pdf` P.90 第 34 題
- 目前狀態：`confirmed_by_source`
- 後續狀態：`ready_to_fix`
- 修正界線：只限 ID 3785；答案維持 4，不得標記為 `wrong_answer`。

建議修正內容：

```text
content = "責任準備金計算與提存牽涉複雜的精算技術與法令規定，會因保險契約之 A.保險期間；B.繳費方式；C.契約生效日；D.繳費期間，而有差別。"
options = ["ABD", "BD", "ABC", "ABCD"]
correct_answer = "4"
explanation = ""
```

上述內容尚未套用至 SQLite 或 `all_questions.json`。

### CORR-20260716-0003 證據與建議修正

- question_id：2664
- source：JY P.90 Q28
- current_answer：`"1"`（BC）
- expected_answer：`"3"`（AD）
- issue_type：`wrong_answer / duplicate_conflict / explanation_conflict`
- status：`fixed`
- correction_status：`applied`
- all_questions.json：已修正
- SQLite questions：已修正
- fixed_question_id：2664
- apply_script：`tools/apply_existing_question_corrections_2664_2654.py`
- closeout_file：`docs/answer_audit/existing_question_corrections_2664_2654_apply_closeout_20260716.md`
- evidence_file：`docs/corrections/id2664_jy_p90_q28_reserve_assumption_answer_correction_20260716.md`
- notes：原稿與等價題 ID2197 均支持 AD；ID2664 現行答案 BC 與解析自相矛盾。

建議修正 `correct_answer` 為 `"3"`，選項維持不變，並將解析改為：

> 保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率亦使死亡給付成本估計較高，因此答案為AD。

### CORR-20260716-0004 證據與建議修正

- question_id：2654
- source：JY P.91 Q49
- current_answer：`"1"`（高）
- expected_answer：`"3"`（一樣）
- issue_type：`wrong_answer / duplicate_conflict / explanation_conflict`
- status：`fixed`
- correction_status：`applied`
- all_questions.json：已修正
- SQLite questions：已修正
- fixed_question_id：2654
- apply_script：`tools/apply_existing_question_corrections_2664_2654.py`
- closeout_file：`docs/answer_audit/existing_question_corrections_2664_2654_apply_closeout_20260716.md`
- evidence_file：`docs/corrections/id2654_jy_p91_q49_dividend_interest_answer_correction_20260716.md`
- notes：原稿與等價題 ID2336 均支持「一樣」；ID2654 現行答案「高」係將累積紅利總給付與保險金額混同。

建議修正 `correct_answer` 為 `"3"`，選項維持不變，並將解析改為：

> 選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。

CORR-20260716-0003 與 CORR-20260716-0004 已完成備份、受控修正及資料一致性驗證；Web 顯示驗證另行記錄。

### MISS-20260716-0001 漏題候選案例

| 欄位 | 內容 |
|---|---|
| case_id | `MISS-20260716-0001` |
| source_question_no | 12 |
| sqlite_id | 4137 |
| json_id | 4137 |
| subject | B 保險實務-分類候選 |
| unit | 03 保險費架構、解約金、準備金、保單紅利 |
| source | `input/JY-人身保險.pdf` / JY價值筆記 |
| source_page | P.89 |
| source_answer | 2 |
| expected_answer | 2 |
| issue_type | `source_mapping_error` |
| status | `confirmed_by_source` |
| next_status | `applied` |
| fix_target | `all_questions.json` id=4137；SQLite `questions.id`=4137（已新增） |
| evidence_file | `docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md` |
| 補入結果 | 已正式補入 |
| new_question_id | 4137 |
| all_questions.json | 已新增 |
| SQLite questions | 已新增 |
| inclusion_status | `applied` |
| apply_note | 由受控腳本 `tools/apply_missing_questions_4136_4137.py --apply` 執行。 |
| notes | 原稿 P.89 Q12 已人工目視確認，右側答案欄為 2，解析為 `10000 × 2/1000 = 20人`、`20 × 1000000 / 10000 = 2000`。完成等價題審核、ID mapping、備份及 dry-run 後，已正式同步新增為 JSON／SQLite ID 4137。 |

此案例保留 `confirmed_by_source` 作為原稿證據狀態；補題流程已另經審核並完成，`inclusion_status = applied`。本案例未使用 `ready_to_fix` 狀態。

### MISS-20260716-0002 漏題候選案例

| 欄位 | 內容 |
|---|---|
| case_id | `MISS-20260716-0002` |
| source_question_no | 14 |
| sqlite_id | 未對應 |
| json_id | 未對應 |
| subject | B 保險實務-分類候選 |
| unit | 03 保險費架構、解約金、準備金、保單紅利 |
| source | `input/JY-人身保險.pdf` / JY價值筆記 |
| source_page | P.89 |
| source_answer | 1 |
| expected_answer | 1 |
| issue_type | `source_mapping_error` |
| status | `confirmed_by_source` |
| next_status | `pending_inclusion_review` |
| fix_target | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` |
| evidence_file | `docs/corrections/p89_q14_jy_premium_calculation_missing_candidate_20260716.md` |
| notes | 原稿 P.89 Q14 已人工目視確認，右側答案欄為 1，作答選項為 (1)ABC、(2)BC、(3)BD、(4)AC。人工校核顯示死亡人數為 3 人，死亡保險金總額為 6000 萬，每人純保費為 6 萬，因此 A、B、C 正確，D 錯誤，原稿答案 (1)ABC 合理。正式 SQLite 與 `all_questions.json` 目前未成功對應此題。此題暫列漏題候選，需先建立補題規則與正式收錄範圍判定，不得直接新增。 |

此案例的 `confirmed_by_source` 僅表示原稿題目、答案與人工校核結果已確認，不代表已核准納入正式題庫，也不得進入 `ready_to_fix`。

### MISS-20260716-0003 漏題候選案例

| 欄位 | 內容 |
|---|---|
| case_id | `MISS-20260716-0003` |
| source_question_no | 31 |
| sqlite_id | 未對應 |
| json_id | 未對應 |
| subject | B 保險實務-分類候選 |
| unit | 03 保險費架構、解約金、準備金、保單紅利 |
| source | `input/JY-人身保險.pdf` / JY價值筆記 |
| source_page | P.90 |
| source_answer | 3 |
| expected_answer | 3 |
| issue_type | `source_mapping_error` / `truncated_question` |
| status | `confirmed_by_source` |
| next_status | `pending_inclusion_review` |
| fix_target | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` |
| evidence_file | `docs/corrections/p90_q31_jy_reserve_missing_candidate_20260716.md` |
| notes | 原稿 P.90 Q31 已人工目視確認，右側答案欄為 3。此題為選項在前、敘述在後的特殊結構，選項為 (1)解約金、(2)保單紅利、(3)責任準備金、(4)保單價值準備金。題幹描述將純保險費扣除已經過危險保費後的資金提存保管，並按保險種類計算、記載於特設帳簿，概念對應責任準備金，因此原稿答案 (3) 合理。正式 SQLite 與 `all_questions.json` 目前未成功對應此題。此題暫列漏題候選，需先建立補題規則與正式收錄範圍判定，不得直接新增。 |

此案例的 `confirmed_by_source` 僅表示原稿題目、答案與特殊題型結構已確認，不代表已核准納入正式題庫，也不得進入 `ready_to_fix`。

### MISS-20260716-0004 至 MISS-20260716-0014 漏題候選案例

下列 11 題已由人工提供的 PDF 截圖核對完整題幹、選項及右側答案欄。截圖本身未顯示 PDF 頁碼；P.90／P.91 定位依本批次提供內容及既有工作表判定。

| case_id | source_question_no | sqlite_id | json_id | subject | unit | source | source_page | source_answer | expected_answer | issue_type | status | next_status | fix_target | evidence_file | notes |
|---|---:|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| `MISS-20260716-0004` | 19 | 4136 | 4136 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 3 | 3 | `source_mapping_error` | `confirmed_by_source` | `applied` | `all_questions.json` id=4136；SQLite `questions.id`=4136（已新增） | `docs/corrections/p90_q19_jy_missing_candidate_20260716.md` | 補入結果：已正式補入；new_question_id：4136；`all_questions.json`：已新增；SQLite `questions`：已新增；inclusion_status：`applied`。由受控腳本 `tools/apply_missing_questions_4136_4137.py --apply` 執行。 |
| `MISS-20260716-0005` | 22 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 1 | 1 | `source_mapping_error` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p90_q22_jy_missing_candidate_20260716.md` | 截圖確認解約金敘述、組合選項及右側答案 1；正式題庫未對應。 |
| `MISS-20260716-0006` | 24 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 3 | 3 | `source_mapping_error` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p90_q24_jy_missing_candidate_20260716.md` | 截圖確認準備金計算基礎、組合選項及右側答案 3；正式題庫未對應。 |
| `MISS-20260716-0007` | 28 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 3 | 3 | `source_mapping_error` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p90_q28_jy_missing_candidate_20260716.md` | 截圖確認預定利率／死亡率敘述、組合選項及右側答案 3；正式題庫未對應。 |
| `MISS-20260716-0008` | 29 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 1 | 1 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p90_q29_jy_missing_candidate_20260716.md` | 截圖確認招攬廣告題幹、選項及右側答案 1；只依教材版本登記，現行法另案審查。 |
| `MISS-20260716-0009` | 32 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.90 | 4 | 4 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p90_q32_jy_missing_candidate_20260716.md` | 截圖確認責任準備金種類、組合選項及右側答案 4；只依教材版本登記，現行法另案審查。 |
| `MISS-20260716-0010` | 35 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.91 | 3 | 3 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p91_q35_jy_missing_candidate_20260716.md` | 截圖確認歷史年度題幹、選項及右側答案 3；只依教材版本登記，現行法另案審查。 |
| `MISS-20260716-0011` | 36 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.91 | 1 | 1 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p91_q36_jy_missing_candidate_20260716.md` | 截圖確認修正制年度題幹、選項及右側答案 1；只依教材版本登記，現行法另案審查。 |
| `MISS-20260716-0012` | 46 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.91 | 1 | 1 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p91_q46_jy_missing_candidate_20260716.md` | 截圖確認保單紅利差益組合及右側答案 1；只依教材版本登記，現行法另案審查。 |
| `MISS-20260716-0013` | 47 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.91 | 3 | 3 | `source_mapping_error` | `confirmed_by_source` | `pending_inclusion_mapping` | 尚未分配新 ID；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p91_q47_jy_missing_candidate_20260716.md` | Q47 為正向完整組合題；ID107 為反向排除題；ID3795、ID3796 僅部分重疊，不足以覆蓋 Q47。可與 ID107 並存並進入補題計畫。 |
| `MISS-20260716-0014` | 49 | 未對應 | 未對應 | B 保險實務-分類候選 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.91 | 2 | 2 | `source_mapping_error` | `confirmed_by_source` | `pending_inclusion_review` | 尚未決定；不得直接補入 SQLite 或 `all_questions.json` | `docs/corrections/p91_q49_jy_missing_candidate_20260716.md` | 截圖確認儲存生息情境、四個選項及右側答案 2；正式題庫未對應。 |

上述案例中，`MISS-20260716-0004` 已另經等價題審核、ID mapping、備份及受控腳本流程正式補入為 ID 4136；`MISS-20260716-0013` 已完成等價題裁定並轉為 `confirmed_by_source`／`pending_inclusion_mapping`；其餘案例維持原狀。漏題候選均不屬於 `ready_to_fix`，不得直接補入正式題庫。

### MISS-20260716-0013 等價題裁定

| 欄位 | 內容 |
|---|---|
| status | `confirmed_by_source` |
| next_status | `pending_inclusion_mapping` |
| equivalence_decision | 可與 ID107 並存，可進入補題計畫 |
| decision_file | `docs/answer_audit/jy_unit03_q47_equivalence_decision_20260716.md` |
| notes | Q47 為正向完整組合題；ID107 為反向排除題；ID3795、ID3796 僅部分重疊，不足以覆蓋 Q47。 |

此狀態只允許建立 ID mapping 草案，不代表已核准或完成正式補題。

## 六、第一批 JY 單元試跑發現摘要

- 依據報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 原稿範圍：P.89–P.92，Q1–Q53。
- 題目總數：53 題。
- 成功對應 SQLite／`all_questions.json`：39 題。
- 無法對應正式題庫：14 題。
- 答案一致：38 題。
- 答案不一致：1 題，Q18／ID 3815。
- 正式題庫選項污染：確認 2 題（ID 3815、ID 3785）；兩題均尚未修正。
- 中間 JSON 選項或解析污染：8 題。
- 原列需人工目視：15 題；ID 3785 已完成並升級，其餘 14 題已全數由原稿確認並登記為 `MISS-20260716-0001` 至 `MISS-20260716-0014`；剩餘 manual_review 0 題。
- `output/JY-人身保險.json` 僅收錄 17 題，漏掉 P.89 Q6 及 P.90–P.92 全部題目。

### 1. 待人工目視清單

| source_question_no | source_page | sqlite_id | issue_type | status | note |
|---:|---:|---|---|---|---|
| 12 | P.89 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已確認為漏題候選 `MISS-20260716-0001`，自剩餘 manual_review 清單移出；尚未判定是否補入正式題庫。 |
| 14 | P.89 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已確認為漏題候選 `MISS-20260716-0002`，自剩餘 manual_review 清單移出；尚未判定是否補入正式題庫。 |
| 19 | P.90 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0004`；尚未判定是否補入正式題庫。 |
| 22 | P.90 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0005`；尚未判定是否補入正式題庫。 |
| 24 | P.90 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0006`；尚未判定是否補入正式題庫。 |
| 28 | P.90 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0007`；尚未判定是否補入正式題庫。 |
| 29 | P.90 | 未對應 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0008`；教材版本已保留，現行法另案審查。 |
| 31 | P.90 | 未對應 | `source_mapping_error`, `truncated_question` | `confirmed_by_source` | 已確認為漏題候選 `MISS-20260716-0003`，自剩餘 manual_review 清單移出；題型為選項在前、敘述在後，尚未判定是否補入正式題庫。 |
| 32 | P.90 | 未對應 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0009`；教材版本已保留，現行法另案審查。 |
| 34 | P.90 | 3785 | `option_pollution`, `truncated_question` | `confirmed_by_source` | 已完成目視並升級為 CORR-20260716-0002；第 4 選項應為 ABCD，「，而有差別。」屬題幹句尾。尚未修改正式題庫。 |
| 35 | P.91 | 未對應 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0010`；教材版本已保留，現行法另案審查。 |
| 36 | P.91 | 未對應 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0011`；教材版本已保留，現行法另案審查。 |
| 46 | P.91 | 未對應 | `source_mapping_error`, `outdated_law` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0012`；教材版本已保留，現行法另案審查。 |
| 47 | P.91 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0013`；尚未判定是否補入正式題庫。 |
| 49 | P.91 | 未對應 | `source_mapping_error` | `confirmed_by_source` | 已登記為漏題候選 `MISS-20260716-0014`；尚未判定是否補入正式題庫。 |

`source_needed` 在本表表示原稿題目已定位，但尚需人工確認其是否屬於應納入的正式題庫範圍；完成判斷前不得新增題目。

### 2. 漏題候選清單

| source_question_no | source_page | source_answer | reason | status | next_action |
|---:|---:|---:|---|---|---|
| 12 | P.89 | 2 | 原稿有題，但正式題庫未成功對應；已有原稿確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；尚未判定是否補入正式題庫，依 `MISS-20260716-0001` 進行收錄審查 |
| 14 | P.89 | 1 | 原稿有題，但正式題庫未成功對應；已有原稿確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；尚未判定是否補入正式題庫，依 `MISS-20260716-0002` 進行收錄審查 |
| 19 | P.90 | 3 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0004` 進行收錄審查 |
| 22 | P.90 | 1 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0005` 進行收錄審查 |
| 24 | P.90 | 3 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0006` 進行收錄審查 |
| 28 | P.90 | 3 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0007` 進行收錄審查 |
| 29 | P.90 | 1 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0008` 進行教材版本與收錄審查 |
| 31 | P.90 | 3 | 原稿有題，但正式題庫未成功對應；已有原稿確認紀錄，題型為選項在前、敘述在後 | `confirmed_by_source` | `next_status = pending_inclusion_review`；尚未判定是否補入正式題庫，依 `MISS-20260716-0003` 進行收錄審查 |
| 32 | P.90 | 4 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0009` 進行教材版本與收錄審查 |
| 35 | P.91 | 3 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0010` 進行教材版本與收錄審查 |
| 36 | P.91 | 1 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0011` 進行教材版本與收錄審查 |
| 46 | P.91 | 1 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0012` 進行教材版本與收錄審查 |
| 47 | P.91 | 3 | 原稿有題、已有截圖確認紀錄，且已裁定可與 ID107 並存 | `confirmed_by_source` | `next_status = pending_inclusion_mapping`；依 `MISS-20260716-0013` 建立補題 ID mapping 草案，不得直接補入 |
| 49 | P.91 | 2 | 原稿有題且已有截圖確認紀錄 | `confirmed_by_source` | `next_status = pending_inclusion_review`；依 `MISS-20260716-0014` 進行收錄審查 |

### 3. 中間 JSON 污染清單

`json_record` 為 `output/JY-人身保險.json` 的零起算陣列索引；該檔記錄本身沒有 id。

| source_question_no | source_page | json_record | issue_type | status | note |
|---:|---:|---:|---|---|---|
| 2 | P.89 | 177 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 4 選項含轉檔警告；正式題庫目前已清除。 |
| 4 | P.89 | 179 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 3 選項空白、第 4 選項為異源亂碼；正式題庫完整。 |
| 7 | P.89 | 181 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 1、2 選項為異源亂碼；正式題庫完整。 |
| 9 | P.89 | 183 | `ocr_parse_error`, `option_pollution` | `source_found` | output 多個選項含異源亂碼；正式題庫完整。 |
| 10 | P.89 | 184 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 3 選項空白；正式題庫完整。 |
| 12 | P.89 | 186 | `ocr_parse_error`, `explanation_pollution` | `confirmed_by_source` | 原稿已確認並登記為 `MISS-20260716-0001`；output 題幹嚴重亂碼且計算解析併入第 4 選項，正式題庫仍無對應。 |
| 15 | P.89 | 189 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 4 選項含異源亂碼；正式題庫完整。 |
| 18 | P.89 | 192 | `ocr_parse_error`, `option_pollution`, `explanation_pollution` | `confirmed_by_source` | 解析併入第 4 選項，並進一步污染正式題庫 ID 3815。 |

### 4. 正式題庫選項污染確認與候選

| question_id | source_question_no | source_page | status | fix_target | note |
|---:|---:|---:|---|---|---|
| 3815 | 18 | P.89 | `ready_to_fix` | `all_questions.json` id=3815；SQLite `questions.id`=3815 | 已由原稿及第一批試跑再次確認；第 4 選項併入解析，答案亦誤為 3。尚未修改正式題庫。 |
| 3785 | 34 | P.90 | `ready_to_fix` | `all_questions.json` id=3785；SQLite `questions.id`=3785 | 已升級為 CORR-20260716-0002，不再只是候選。原稿已確認第 4 選項為 ABCD，「，而有差別。」屬題幹句尾；尚未修改正式題庫。 |

### 5. 第一批試跑後續處理原則

1. 本次只登記，不修題庫。
2. 漏題候選不得直接新增到正式題庫，需人工確認是否屬於正式題庫範圍。
3. 中間 JSON 污染不等於正式題庫錯誤，需確認是否已污染 `all_questions.json` 或 SQLite。
4. 所有 `ready_to_fix` 題目修正前，都需備份 SQLite 與 `all_questions.json`。
5. 第一批原列 15 題已全部完成原稿確認：ID 3785 為既有題修正案例，其餘 14 題為漏題候選 `MISS-20260716-0001` 至 `MISS-20260716-0014`；剩餘 manual_review 0 題。
6. 本次只更新 ledger，不修題庫。
7. ID 3815 與 ID 3785 可列入下一批 `ready_to_fix`。
8. 修正前必須備份 SQLite 與 `all_questions.json`。
9. 修正時只允許修改已 `confirmed_by_source` 且 `ready_to_fix` 的題目。
10. 修正後需驗證 Web 顯示。
11. 補題前需建立新題 ID 分配規則。
12. 補題前需確認是否已有改寫題或等價題。
13. 補題前需定義 `all_questions.json` 與 SQLite 同步規則，補題後需進行 Web 驗證。
14. 目前 `ready_to_fix` 僅限已確認且已有既有 ID 的修正題，不包含漏題候選。

## 七、後續待查清單

以下項目目前只列入調查範圍。ID 3815 與 ID 3785 已另列正式確認案例；其餘項目未因列入本清單而判定答案或結構錯誤。

### 1. 第三章 OCR／切割疑點

- 狀態：`suspected`
- 建議錯誤類型：`ocr_parse_error`, `manual_review`
- SQLite IDs：3387、3778、3782、3783、3784、3786、3787、3788、3789、3791、3793、3796、3797、3798、3799
- 後續動作：逐題回到對應原稿頁面，核對題幹、選項、答案與解析。

### 2. ID 139：無選項但答案 A

- 狀態：`suspected`
- 建議錯誤類型：`ocr_parse_error`, `option_pollution`, `source_mapping_error`, `manual_review`
- 已知現象：系統選項為空，但答案欄為 A。
- 後續動作：追查原稿檔案與頁碼，確認題目是否完整及是否誤映射。

### 3. ID 795：題幹過短

- 狀態：`suspected`
- 建議錯誤類型：`truncated_question`, `manual_review`
- 已知現象：題幹只有「保險契約」。
- 後續動作：回到原稿確認完整題幹與來源題號。

### 4. 82 組重複題幹但答案字串不同

- 狀態：`suspected`
- 建議錯誤類型：`duplicate_conflict`, `manual_review`
- 後續動作：先將 `A–D` 與 `1–4` 正規化成選項位置，再排除僅格式不同的案例；剩餘衝突逐題回查原稿。

### 5. 第一批逐題原稿校對試跑範圍

- 狀態：試跑報告及原列 15 題人工目視均已完成；ID 3785 為既有題修正案例，其餘 14 題為漏題候選；剩餘 manual_review 0 題
- 原稿：`input/JY-人身保險.pdf`
- 單元：三、保險費架構、解約金、準備金、保單紅利
- 範圍：P.89–P.92，Q1–Q53
- 試跑報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 後續動作：進入漏題候選收錄規則與教材版本審查；不得直接補入或修改正式題庫。

## 八、後續批次修正流程

1. 逐題追蹤原稿、頁碼、題號或法規來源。
2. 由人工目視確認來源內容與系統差異。
3. 將已確認案例登記到 correction ledger，並附證據文件或依據。
4. 累積並審查 `ready_to_fix` 題目清單。
5. 修正前備份 SQLite 與 `all_questions.json`。
6. 依核准清單批次修正 SQLite 與 `all_questions.json`；`output` JSON 依既定重建策略處理。
7. 驗證修正前後題數不變，並確認 ID、題幹、選項、答案及解析符合核准內容。
8. 啟動 Web 畫面抽查題目顯示、作答判定及解析內容。
9. 檢查 diff，只提交核准範圍後建立 commit。
10. 經確認後 push，並將案例狀態更新到 `verified`。

任何步驟若發現來源不清、題目映射錯誤或法規版本疑義，應停止該題修正並改列 `deferred` 或重新進入人工複核。
