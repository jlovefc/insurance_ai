# 第一批 JY 單元 03 manual_review 人工目視工作表

- 建立日期：2026-07-16
- 原稿：`input/JY-人身保險.pdf`
- 單元：三、保險費架構、解約金、準備金、保單紅利
- 原稿範圍：P.89–P.92，Q1–Q53
- 工作表範圍：第一批試跑列出的 15 題 `manual_review`／`source_needed`
- 文件性質：人工目視工作表；本文件不授權修正任何題庫資料

## 一、依據與使用原則

依據文件：

1. `docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md`
2. `docs/corrections/correction_ledger_20260716.md`
3. `docs/answer_audit/source_based_chapter_unit_question_audit_workflow_20260716.md`

人工檢查時必須直接打開 `input/JY-人身保險.pdf` 的指定頁面，核對題號、題幹、四個選項、Ans 欄及解析。文字層、output JSON、正式 JSON、SQLite 或 AI 推論均不得取代原稿目視結果。

本表的 `source_answer` 是試跑依 raw text Ans 欄整理的待確認值；尚未經本輪人工目視前，不得據此新增或修改正式題庫。`system_answer` 為 `all_questions.json` 與 SQLite 的正式答案；「未對應」表示試跑未找到可靠的正式題庫記錄。

## 二、分類摘要

| 分類 | 題目 | 題數 | 說明 |
|---|---|---:|---|
| 1. 已進正式題庫但需人工確認 | Q34／ID 3785 | 1 | 答案一致，但第 4 選項疑似混入題幹尾語。 |
| 2. 原稿有題但正式題庫未對應 | Q12、Q14、Q19、Q22、Q24、Q28、Q29、Q31、Q32、Q35、Q36、Q46、Q47、Q49 | 14 | 不得直接視為漏題並補入；須先確認正式題庫收錄範圍。 |
| 3. 中間 JSON 污染但正式題庫是否受影響待查 | Q12、Q14 | 2 | Q12 有解析／選項污染；Q14 題幹嚴重污染。兩題均未對應正式記錄。 |
| 4. 選項污染候選 | Q12、Q34／ID 3785 | 2 | Q12 為中間 JSON 污染；Q34 為正式題庫候選。 |
| 5. 答案疑似不一致候選 | 無新增候選 | 0 | Q18／ID 3815 已人工確認，不屬本次 manual_review 15 題。其餘 14 題沒有 system answer，不能判定答案不一致。 |

分類可重疊，因此各分類題數不可直接加總。工作表唯一題數為 15 題。

## 三、人工目視工作清單

所有題目的「是否可直接修正」一律為「否，需人工確認」。

| review_id | source_file | source_page | source_question_no | sqlite_id | json_id | source_answer | system_answer | 疑點類型 | 人工目視時要確認的事項 | 建議狀態 | 是否可直接修正 |
|---|---|---:|---:|---|---|---:|---|---|---|---|---|
| JY-U03-MR-001 | `input/JY-人身保險.pdf` | P.89 | 12 | 未對應 | 未對應 | 2 | 未對應 | `source_mapping_error`, `explanation_missing`, `ocr_parse_error`, `explanation_pollution` | 確認題幹數值、四個金額選項、Ans 是否為 2、計算解析全文及解析是否屬於本題；再判斷是否應納入正式題庫。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-002 | `input/JY-人身保險.pdf` | P.89 | 14 | 未對應 | 未對應 | 1 | 未對應 | `source_mapping_error`, `truncated_question`, `ocr_parse_error` | 確認 A–D 敘述是否完整、作答選項排列、Ans 是否為 1；排除中間 JSON 題幹污染後再判斷是否應收錄。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-003 | `input/JY-人身保險.pdf` | P.90 | 19 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error` | 確認完整題幹、四個選項、Ans 是否為 3，並搜尋是否以改寫題或不同單元存在；不得只依關鍵字新增。 | `source_needed` | 否，需人工確認 |
| JY-U03-MR-004 | `input/JY-人身保險.pdf` | P.90 | 22 | 未對應 | 未對應 | 1 | 未對應 | `source_mapping_error` | 確認 A–D 解約金敘述、組合選項、Ans 是否為 1，以及教材法規時點；判斷是否屬正式題庫範圍。 | `source_needed` | 否，需人工確認 |
| JY-U03-MR-005 | `input/JY-人身保險.pdf` | P.90 | 24 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error` | 確認 A–D 基礎項目、組合選項、Ans 是否為 3，以及法規版本；搜尋是否已有近似題但來源不同。 | `source_needed` | 否，需人工確認 |
| JY-U03-MR-006 | `input/JY-人身保險.pdf` | P.90 | 28 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error` | 確認預定利率／死亡率敘述、BC／BD／AD／AC 選項順序及 Ans 是否為 3；判斷是否應收錄。 | `source_needed` | 否，需人工確認 |
| JY-U03-MR-007 | `input/JY-人身保險.pdf` | P.90 | 29 | 未對應 | 未對應 | 1 | 未對應 | `source_mapping_error`, `outdated_law` | 確認招攬廣告題幹、四項敘述、Ans 是否為 1，並記錄教材適用時點；不得以現行規範直接覆蓋原稿。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-008 | `input/JY-人身保險.pdf` | P.90 | 31 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error`, `truncated_question` | 確認題幹前置詞是否因 raw 排序錯置、四個名詞選項及 Ans 是否為 3；完整抄錄原稿題幹。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-009 | `input/JY-人身保險.pdf` | P.90 | 32 | 未對應 | 未對應 | 4 | 未對應 | `source_mapping_error`, `outdated_law` | 確認 A–D 各種準備金名稱、組合選項、Ans 是否為 4，並記錄教材法規版本。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-010 | `input/JY-人身保險.pdf` | P.90 | 34 | 3785 | 3785 | 4 | 4 | `option_pollution` | 目視確認「而有差別」位於題幹還是第 4 選項；確認第 4 選項是否僅為 `ABCD`、Ans 是否為 4，並核對題幹尾句。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-011 | `input/JY-人身保險.pdf` | P.91 | 35 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error`, `outdated_law` | 確認年份選項、Ans 是否為 3、教材法規適用時點，以及此歷史題是否屬正式收錄範圍。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-012 | `input/JY-人身保險.pdf` | P.91 | 36 | 未對應 | 未對應 | 1 | 未對應 | `source_mapping_error`, `outdated_law` | 確認年份選項、Ans 是否為 1、教材法規適用時點，以及是否與其他責任準備金題混淆。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-013 | `input/JY-人身保險.pdf` | P.91 | 46 | 未對應 | 未對應 | 1 | 未對應 | `source_mapping_error`, `outdated_law` | 確認利差／費差／死差組合選項、Ans 是否為 1、題目適用年度及是否應收錄。 | `manual_review` | 否，需人工確認 |
| JY-U03-MR-014 | `input/JY-人身保險.pdf` | P.91 | 47 | 未對應 | 未對應 | 3 | 未對應 | `source_mapping_error` | 確認四種紅利支付方法、組合選項排列及 Ans 是否為 3；搜尋正式題庫是否有不同文字版本。 | `source_needed` | 否，需人工確認 |
| JY-U03-MR-015 | `input/JY-人身保險.pdf` | P.91 | 49 | 未對應 | 未對應 | 2 | 未對應 | `source_mapping_error` | 確認儲存生息情境、四個答案選項及 Ans 是否為 2；判斷是否已有改寫題或是否應納入正式題庫。 | `source_needed` | 否，需人工確認 |

## 四、建議目視順序

1. P.89：JY-U03-MR-001、JY-U03-MR-002。兩題均有中間解析／題幹污染，先完整抄錄原稿。
2. P.90：JY-U03-MR-003 至 JY-U03-MR-010。先確認 Q34 選項邊界，再逐題確認 7 題未對應題。
3. P.91：JY-U03-MR-011 至 JY-U03-MR-015。法規時效題須額外記錄教材版本與日期。

每題完成目視後，先填寫下方人工確認欄位，再決定是否更新 correction ledger。未取得可追溯的頁碼、題號及原稿內容前，不得升級為 `confirmed_by_source` 或 `ready_to_fix`。

## 五、人工確認欄位

| review_id | source_question_no | human_checked | human_source_answer | human_note | next_status |
|---|---:|---|---|---|---|
| JY-U03-MR-001 | 12 | 未確認 |  |  |  |
| JY-U03-MR-002 | 14 | 未確認 |  |  |  |
| JY-U03-MR-003 | 19 | 未確認 |  |  |  |
| JY-U03-MR-004 | 22 | 未確認 |  |  |  |
| JY-U03-MR-005 | 24 | 未確認 |  |  |  |
| JY-U03-MR-006 | 28 | 未確認 |  |  |  |
| JY-U03-MR-007 | 29 | 未確認 |  |  |  |
| JY-U03-MR-008 | 31 | 未確認 |  |  |  |
| JY-U03-MR-009 | 32 | 未確認 |  |  |  |
| JY-U03-MR-010 | 34 | 未確認 |  |  |  |
| JY-U03-MR-011 | 35 | 未確認 |  |  |  |
| JY-U03-MR-012 | 36 | 未確認 |  |  |  |
| JY-U03-MR-013 | 46 | 未確認 |  |  |  |
| JY-U03-MR-014 | 47 | 未確認 |  |  |  |
| JY-U03-MR-015 | 49 | 未確認 |  |  |  |

允許的 `next_status` 應依證據填寫，例如 `source_found`、`source_unclear`、`confirmed_by_source`、`deferred`；不得因答案看似合理而直接填為 `ready_to_fix`。

