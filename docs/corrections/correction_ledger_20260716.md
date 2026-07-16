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
| CORR-20260716-0001 | 3815 | B 保險實務-分類 | 03 保險費架構、解約金、準備金、保單紅利 | `input/JY-人身保險.pdf` / JY價值筆記 | P.89 | 18 | 3 | 1 | 1 | `wrong_answer`, `ocr_parse_error`, `option_pollution`, `explanation_missing` | `confirmed_by_source` | `all_questions.json` id=3815；SQLite `questions.id`=3815 | 原稿右側答案欄為 1。系統誤將解析尾端「何者正確答案就會是 3」抓為正式答案，且第 4 選項被解析文字污染。已於第一批 JY 單元逐題原稿校對試跑再次確認；試跑狀態為 `confirmed_by_source`，後續進入 `ready_to_fix`，但尚未修改正式題庫。不得混同 SQLite ID 2670。 |

### CORR-20260716-0001 證據文件

- 個案修正紀錄：`docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md`
- 第一批試跑報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 原稿：`input/JY-人身保險.pdf` P.89 第 18 題
- 流程規格：`docs/answer_audit/source_based_chapter_unit_question_audit_workflow_20260716.md`
- 試跑狀態：`confirmed_by_source`。
- 後續狀態：`ready_to_fix`；此狀態只表示證據與修正建議已具備，尚未修改 SQLite 或 `all_questions.json`，不得標記為 `fixed`。

## 六、第一批 JY 單元試跑發現摘要

- 依據報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 原稿範圍：P.89–P.92，Q1–Q53。
- 題目總數：53 題。
- 成功對應 SQLite／`all_questions.json`：39 題。
- 無法對應正式題庫：14 題。
- 答案一致：38 題。
- 答案不一致：1 題，Q18／ID 3815。
- 正式題庫選項污染：確認 1 題；含候選共 2 題。
- 中間 JSON 選項或解析污染：8 題。
- 需人工目視：15 題。
- `output/JY-人身保險.json` 僅收錄 17 題，漏掉 P.89 Q6 及 P.90–P.92 全部題目。

### 1. 待人工目視清單

| source_question_no | source_page | sqlite_id | issue_type | status | note |
|---:|---:|---|---|---|---|
| 12 | P.89 | 未對應 | `source_mapping_error`, `explanation_missing` | `manual_review` | output 題幹嚴重亂碼，計算解析併入第 4 選項；正式題庫無記錄。 |
| 14 | P.89 | 未對應 | `source_mapping_error`, `truncated_question` | `manual_review` | output 題幹嚴重污染；正式題庫無記錄。 |
| 19 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，output、正式快照及 SQLite 均無對應。 |
| 22 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 24 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 28 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 29 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 31 | P.90 | 未對應 | `source_mapping_error`, `truncated_question` | `manual_review` | raw 題幹前置詞排序異常，正式題庫無對應。 |
| 32 | P.90 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 34 | P.90 | 3785 | `option_pollution` | `manual_review` | 第 4 選項含「而有差別」；需目視確認該文字是否屬題幹尾語。 |
| 35 | P.91 | 未對應 | `source_mapping_error`, `outdated_law` | `manual_review` | 正式題庫無對應，且涉及歷史法規時點。 |
| 36 | P.91 | 未對應 | `source_mapping_error`, `outdated_law` | `manual_review` | 正式題庫無對應，且涉及歷史法規時點。 |
| 46 | P.91 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 47 | P.91 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |
| 49 | P.91 | 未對應 | `source_mapping_error` | `source_needed` | 原稿有題，正式題庫無對應。 |

`source_needed` 在本表表示原稿題目已定位，但尚需人工確認其是否屬於應納入的正式題庫範圍；完成判斷前不得新增題目。

### 2. 漏題候選清單

| source_question_no | source_page | source_answer | reason | status | next_action |
|---:|---:|---:|---|---|---|
| 12 | P.89 | 2 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 14 | P.89 | 1 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 19 | P.90 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 22 | P.90 | 1 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 24 | P.90 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 28 | P.90 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 29 | P.90 | 1 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 31 | P.90 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 32 | P.90 | 4 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 35 | P.91 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 36 | P.91 | 1 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 46 | P.91 | 1 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 47 | P.91 | 3 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |
| 49 | P.91 | 2 | 原稿有題，但正式題庫未成功對應 | `source_found` | 人工確認是否應補入正式題庫 |

### 3. 中間 JSON 污染清單

`json_record` 為 `output/JY-人身保險.json` 的零起算陣列索引；該檔記錄本身沒有 id。

| source_question_no | source_page | json_record | issue_type | status | note |
|---:|---:|---:|---|---|---|
| 2 | P.89 | 177 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 4 選項含轉檔警告；正式題庫目前已清除。 |
| 4 | P.89 | 179 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 3 選項空白、第 4 選項為異源亂碼；正式題庫完整。 |
| 7 | P.89 | 181 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 1、2 選項為異源亂碼；正式題庫完整。 |
| 9 | P.89 | 183 | `ocr_parse_error`, `option_pollution` | `source_found` | output 多個選項含異源亂碼；正式題庫完整。 |
| 10 | P.89 | 184 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 3 選項空白；正式題庫完整。 |
| 12 | P.89 | 186 | `ocr_parse_error`, `explanation_pollution` | `manual_review` | output 題幹嚴重亂碼，計算解析併入第 4 選項；正式題庫無對應。 |
| 15 | P.89 | 189 | `ocr_parse_error`, `option_pollution` | `source_found` | output 第 4 選項含異源亂碼；正式題庫完整。 |
| 18 | P.89 | 192 | `ocr_parse_error`, `option_pollution`, `explanation_pollution` | `confirmed_by_source` | 解析併入第 4 選項，並進一步污染正式題庫 ID 3815。 |

### 4. 正式題庫選項污染確認與候選

| question_id | source_question_no | source_page | status | fix_target | note |
|---:|---:|---:|---|---|---|
| 3815 | 18 | P.89 | `ready_to_fix` | `all_questions.json` id=3815；SQLite `questions.id`=3815 | 已由原稿及第一批試跑再次確認；第 4 選項併入解析，答案亦誤為 3。尚未修改正式題庫。 |
| 3785 | 34 | P.90 | `manual_review` | `all_questions.json` id=3785；SQLite `questions.id`=3785 | 第 4 選項含「而有差別」；需先目視確認是否為題幹尾語，不得直接修正。 |

### 5. 第一批試跑後續處理原則

1. 本次只登記，不修題庫。
2. 漏題候選不得直接新增，需人工確認是否屬於正式題庫範圍。
3. 中間 JSON 污染不等於正式題庫錯誤，需確認是否已污染 `all_questions.json` 或 SQLite。
4. 所有 `ready_to_fix` 題目修正前，都需備份 SQLite 與 `all_questions.json`。
5. 第一批後續應先人工目視 15 題 `manual_review`／`source_needed`，再決定哪些案例升級為 `confirmed_by_source`。

## 七、後續待查清單

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

- 狀態：試跑報告已完成；15 題待人工目視
- 原稿：`input/JY-人身保險.pdf`
- 單元：三、保險費架構、解約金、準備金、保單紅利
- 範圍：P.89–P.92，Q1–Q53
- 試跑報告：`docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
- 後續動作：依本文件第六節清單人工目視 15 題，確認漏題範圍與選項污染候選，不得直接修題庫。

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
