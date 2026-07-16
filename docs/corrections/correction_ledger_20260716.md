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

| case_id | question_id | subject | unit | source | source_page | source_question_no | current_answer | source_answer | expected_answer | error_types | status | fix_target | notes |
|---|---:|---|---|---|---|---:|---|---|---|---|---|---|---|
| CORR-20260716-0001 | 3815 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.89 | 18 | 3 | 1 | 1 | `wrong_answer`, `ocr_parse_error`, `option_pollution` | `confirmed_by_source` | `all_questions.json` id=3815；SQLite `questions.id`=3815 | 原稿右側答案欄為 1。系統誤將解析尾端「何者正確答案就會是 3」抓為正式答案，且第 4 選項被解析文字污染。不得混同 SQLite ID 2670。 |

### CORR-20260716-0001 證據文件

- 個案修正紀錄：`docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md`
- 原稿：`input/JY-人身保險.pdf` P.89 第 18 題
- 流程規格：`docs/answer_audit/source_based_chapter_unit_question_audit_workflow_20260716.md`
- 目前狀態說明：已確認來源與預期答案，尚未修改 SQLite 或 `all_questions.json`，因此不得標記為 `fixed`。

## 六、後續待查清單

以下項目目前只列入調查範圍。除 ID 3815 外，未因列入本清單而判定答案錯誤。

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

- 狀態：`source_found`
- 原稿：`input/JY-人身保險.pdf`
- 單元：三、保險費架構、解約金、準備金、保單紅利
- 範圍：該單元全部題目；實際頁碼範圍由後續唯讀盤點確認
- 後續動作：建立原稿題號清單，逐題對應 SQLite 與 `all_questions.json`，輸出答案、選項及解析差異，不得直接修題庫。

## 七、後續批次修正流程

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
