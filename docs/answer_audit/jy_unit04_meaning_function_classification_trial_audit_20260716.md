# JY unit04 人身保險意義、功能、分類逐題原稿校對試跑

## 一、檢查結論摘要

本次依 source-based workflow，唯讀比對 `input/JY-人身保險.pdf` P.93–P.95 的「四、人身保險意義、功能、分類」Q1–Q38，並核對 `shiwu_raw.txt`、`output/JY-人身保險.json`、`all_questions.json` 與本機 SQLite `questions`。

- 原稿題數：38。
- 正式題庫成功對應：28 題。
- 正式題庫未對應：10 題，為 Q26–Q30、Q34–Q38。
- 已對應題答案一致：27 題。
- 已對應題答案不一致：1 題，Q13／ID3840。
- 正式題庫題目結構污染候選：2 題，Q8／ID3835、Q13／ID3840。
- `output/JY-人身保險.json`：僅14筆，只有 P.93 部分題目；P.94、P.95 全部缺漏。
- `all_questions.json` 與 SQLite：28題逐欄一致，ID3816–3843。
- 本報告只登記風險，不修正、不補題、不更新 correction ledger。

Q13／ID3840 為本批最高風險：原稿答案為4，正式題庫答案為2，且正式題庫第4選項被截斷為「僅選項」。Q8／ID3835 的共同題幹尾句被併入第4選項，屬題目結構污染候選。

## 二、原稿單元範圍

- source_file：`input/JY-人身保險.pdf`
- source_unit：`四、人身保險意義、功能、分類`
- P.93：Q1–Q16，共16題。
- P.94：Q17–Q32，共16題。
- P.95：Q33–Q38，共6題。
- 下一單元自 P.96「五、人身保險—人壽保險」開始。

PDF 頁面右側答案欄與題號經視覺核對；PDF 文字層另用於整理題幹、選項與解析。

## 三、資料來源狀態

| 資料來源 | unit04 題數 | 範圍與狀態 |
|---|---:|---|
| `input/JY-人身保險.pdf`／`shiwu_raw.txt` | 38 | P.93–P.95，Q1–Q38 |
| `output/JY-人身保險.json` | 14 | 僅 P.93 部分題；0-based index 193–206／record 194–207 |
| `all_questions.json` | 28 | ID3816–3843 |
| SQLite `questions` | 28 | ID3816–3843，與正式 JSON 逐欄一致 |

中間 JSON 對應 P.93 的 Q1–Q5、Q7–Q10、Q12–Q16；未收錄 Q6、Q11，亦未收錄 P.94 Q17–Q32 與 P.95 Q33–Q38。14筆中多筆含「轉檔異常」、雜訊字串、題幹污染或選項污染，不得作為最終答案依據。

## 四、原稿答案分布

| 答案 | 題數 |
|---:|---:|
| 1 | 11 |
| 2 | 9 |
| 3 | 9 |
| 4 | 9 |
| 合計 | 38 |

正式題庫28題的答案分布為1：8題、2：7題、3：7題、4：6題。與其已對應原稿相比，差異只來自 Q13／ID3840 將原稿答案4記為2。

## 五、逐題比對結果

`json_id` 指 `all_questions.json` ID；`—` 表示正式題庫未對應。`option_match` 以原稿作答選項的邏輯結構為準，不以 OCR 換行位置判定。

| source_question_no | source_page | sqlite_id | json_id | source_answer | system_answer | answer_match | option_match | explanation_match | issue_type | status | evidence_note | fix_suggestion |
|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 1 | P.93 | 3828 | 3828 | 1 | 1 | 是 | 是 | 是（皆空） | — | matched | 保障力量題，題幹與四選項一致 | 不修正 |
| 2 | P.93 | 3829 | 3829 | 4 | 4 | 是 | 是 | 是（皆空） | — | matched | 保險特質題一致 | 不修正 |
| 3 | P.93 | 3830 | 3830 | 1 | 1 | 是 | 是 | 是（皆空） | — | matched | 壽險價格原則組合題一致 | 不修正 |
| 4 | P.93 | 3831 | 3831 | 3 | 3 | 是 | 是 | 是（皆空） | — | matched | 不正確敘述題一致 | 不修正 |
| 5 | P.93 | 3832 | 3832 | 1 | 1 | 是 | 是 | 是（皆空） | — | matched | 健全營運要素題一致 | 不修正 |
| 6 | P.93 | 3833 | 3833 | 1 | 1 | 是 | 是 | 是（皆空） | `output_missing` | matched | 正式題庫存在，中間 JSON 未收錄 | 不修正正式題庫；記錄中間來源缺漏 |
| 7 | P.93 | 3834 | 3834 | 2 | 2 | 是 | 是 | 是（皆空） | `output_pollution` | matched | 正式題庫一致；中間 JSON 選項A污染 | 不修正正式題庫 |
| 8 | P.93 | 3835 | 3835 | 3 | 3 | 是 | 否 | 是（皆空） | `option_pollution`, `truncated_question` | manual_review | 原稿「出極少的錢……保障生活」是套用四個主詞選項後的共同題幹；系統全併入第4選項 | 建立獨立修正證據前再次目視；不得直接修改 |
| 9 | P.93 | 3836 | 3836 | 1 | 1 | 是 | 是 | 是（皆空） | `output_pollution` | matched | 正式題庫一致；中間 JSON 題幹尾端污染 | 不修正正式題庫 |
| 10 | P.93 | 3837 | 3837 | 2 | 2 | 是 | 是 | 是（皆空） | `output_pollution` | matched | 無形商品題正式資料一致 | 不修正正式題庫 |
| 11 | P.93 | 3838 | 3838 | 1 | 1 | 是 | 是 | 是（皆空） | `output_missing`, `version_review` | manual_review | 保險存摺服務題；中間 JSON 未收錄，內容具時效性 | 保留教材版本；另案確認是否需版本標示 |
| 12 | P.93 | 3839 | 3839 | 4 | 4 | 是 | 是 | 是（皆空） | `output_pollution`, `version_review` | manual_review | 正式題庫一致；中間 JSON 選項污染，內容具時效性 | 不改答案；另案做版本審查 |
| 13 | P.93 | 3840 | 3840 | 4 | 2 | 否 | 否 | 是（皆空） | `wrong_answer`, `truncated_option`, `duplicate_conflict_candidate` | manual_review | 原稿第4項為「僅選項2、3為真」，右側答案4；系統第4項僅「僅選項」，答案2 | 最高優先建立原稿確認與修正證據；本次不得直接修正 |
| 14 | P.93 | 3841 | 3841 | 2 | 2 | 是 | 是 | 是（皆空） | `version_review` | manual_review | 電子保單敘述題答案一致，內容具時效性 | 保留教材語境，必要時版本審查 |
| 15 | P.93 | 3842 | 3842 | 3 | 3 | 是 | 是 | 是（皆空） | `version_review` | manual_review | 網址取代紙本條款題答案一致，內容具時效性 | 保留教材語境，必要時版本審查 |
| 16 | P.93 | 3843 | 3843 | 4 | 4 | 是 | 是 | 是（皆空） | `output_pollution` | matched | 強迫儲蓄題正式資料一致 | 不修正正式題庫 |
| 17 | P.94 | 3816 | 3816 | 3 | 3 | 是 | 是 | 是（皆空） | `output_missing` | matched | 現代生活三重保障題；中間 JSON 未收錄 | 不修正正式題庫 |
| 18 | P.94 | 3817 | 3817 | 1 | 1 | 是 | 是 | 是（皆空） | `output_missing` | matched | 公平危險分擔題一致 | 不修正 |
| 19 | P.94 | 3818 | 3818 | 2 | 2 | 是 | 是 | 是（皆空） | `output_missing` | matched | 收支相等原則題一致 | 不修正 |
| 20 | P.94 | 3819 | 3819 | 3 | 3 | 是 | 是 | 是 | `output_missing` | matched | 複保險題與原稿解析均一致 | 不修正 |
| 21 | P.94 | 3820 | 3820 | 3 | 3 | 是 | 是 | 是（皆空） | `output_missing` | matched | 再保險定義題一致 | 不修正 |
| 22 | P.94 | 3821 | 3821 | 2 | 2 | 是 | 是 | 是（皆空） | `output_missing` | matched | 分散危險題一致 | 不修正 |
| 23 | P.94 | 3822 | 3822 | 4 | 4 | 是 | 是 | 是（皆空） | `output_missing` | matched | 國外再保題一致 | 不修正 |
| 24 | P.94 | 3823 | 3823 | 4 | 4 | 是 | 是 | 是（皆空） | `output_missing` | matched | 人身保險功能題一致 | 不修正 |
| 25 | P.94 | 3824 | 3824 | 1 | 1 | 是 | 是 | 是（皆空） | `output_missing` | matched | 個人功能情境題一致 | 不修正 |
| 26 | P.94 | — | — | 4 | — | N/A | N/A | N/A | `source_mapping_error` | source_found | 個人功能 ABCD 組合題原稿存在，正式題庫未對應 | 先做等價題檢查，不得直接補題 |
| 27 | P.94 | — | — | 2 | — | N/A | N/A | N/A | `source_mapping_error` | source_found | 個人功能 ABC 組合題，原稿另有解析 | 先做等價題檢查並保留解析 |
| 28 | P.94 | — | — | 4 | — | N/A | N/A | N/A | `source_mapping_error` | source_found | 社會功能 BCD 組合題原稿存在 | 先做等價題檢查，不得直接補題 |
| 29 | P.94 | — | — | 1 | — | N/A | N/A | N/A | `source_mapping_error` | source_found | 國家功能 ACD 組合題原稿存在 | 先做等價題檢查，不得直接補題 |
| 30 | P.94 | — | — | 1 | — | N/A | N/A | N/A | `source_mapping_error` | source_found | 國家功能 ABD 組合題原稿存在 | 先做等價題檢查，不得直接補題 |
| 31 | P.94 | 3825 | 3825 | 3 | 3 | 是 | 是 | 是（皆空） | `output_missing` | matched | 晚年生活憑恃題一致 | 不修正 |
| 32 | P.94 | 3826 | 3826 | 2 | 2 | 是 | 是 | 是（皆空） | `output_missing` | matched | 形成資本、調整金融題一致 | 不修正 |
| 33 | P.95 | 3827 | 3827 | 4 | 4 | 是 | 是 | 是（皆空） | `output_missing` | matched | 穩定經濟、安定政治題一致 | 不修正 |
| 34 | P.95 | — | — | 1 | — | N/A | N/A | N/A | `source_mapping_error`, `law_version_review` | source_found | 保險法第13條二分法題原稿存在 | 等價題與法規版本檢查後再裁定 |
| 35 | P.95 | — | — | 2 | — | N/A | N/A | N/A | `source_mapping_error`, `law_version_review` | source_found | 人身保險法定類別組合題，原稿附解析 | 等價題與法規版本檢查後再裁定 |
| 36 | P.95 | — | — | 3 | — | N/A | N/A | N/A | `source_mapping_error`, `law_version_review` | source_found | 人身保險四大類題原稿存在 | 等價題與法規版本檢查後再裁定 |
| 37 | P.95 | — | — | 3 | — | N/A | N/A | N/A | `source_mapping_error`, `law_version_review` | source_found | 保險法第13條正確敘述題原稿存在 | 等價題與法規版本檢查後再裁定 |
| 38 | P.95 | — | — | 2 | — | N/A | N/A | N/A | `source_mapping_error`, `law_version_review` | source_found | 實務人身保險項目題，原稿附版本語境解析 | 先做等價題及法規／教材語境審查 |

## 六、正式題庫未對應清單

共10題：

- P.94：Q26、Q27、Q28、Q29、Q30。
- P.95：Q34、Q35、Q36、Q37、Q38。

這10題均已有原稿題幹、四個選項及右側答案欄，但本次只標記 `source_found`。不得直接新增到 `all_questions.json` 或 SQLite；下一階段必須先進行全題庫等價題搜尋，其中 Q34–Q38 還需保險法／教材版本語境審查。

## 七、優先高風險題

### 1. Q13／ID3840

- 原稿題幹：目前人身保險業所簽發的保單為。
- 原稿第4選項：`僅選項2、3為真`。
- 原稿答案：4。
- 系統第4選項：`僅選項`。
- 系統答案：2。
- 初步類型：`wrong_answer`, `truncated_option`。
- 下一步：建立單題人工目視修正證據，並確認是否存在同題／改寫題答案衝突；未完成證據流程前不得修正。

### 2. Q8／ID3835

- 原稿是套句型：「人身保險的意義，就是由（四個主詞選項之一）出極少的錢……保障生活」。
- 正式題庫 `content` 只保留「人身保險的意義，就是由？」。
- 正式題庫將「出極少的錢……保障生活」全部併入第4選項「保險公司的員工」。
- 原稿與系統答案均為3，答案本身未見衝突。
- 初步類型：`option_pollution`, `truncated_question`。
- 下一步：建立單題結構修正證據；不得標為 `wrong_answer`。

## 八、中間 JSON 狀態

`output/JY-人身保險.json` 的 unit04 只有14筆：

| source_question_no | 0-based index | 1-based record | 狀態摘要 |
|---:|---:|---:|---|
| 1 | 193 | 194 | 大致完整 |
| 2 | 194 | 195 | 大致完整 |
| 3 | 195 | 196 | 題幹明顯污染 |
| 4 | 196 | 197 | 選項含雜訊 |
| 5 | 197 | 198 | 題幹嚴重污染 |
| 7 | 198 | 199 | 選項污染 |
| 8 | 199 | 200 | 選項及題幹結構嚴重污染 |
| 9 | 200 | 201 | 題幹尾端污染 |
| 10 | 201 | 202 | 題幹污染 |
| 12 | 202 | 203 | 選項污染 |
| 13 | 203 | 204 | 選項污染，但中間答案D與原稿答案4一致 |
| 14 | 204 | 205 | 選項污染 |
| 15 | 205 | 206 | 題幹／選項污染 |
| 16 | 206 | 207 | 題幹污染 |

中間 JSON 不得用來覆蓋正式題庫。Q13 顯示中間資料答案仍為D，正式題庫卻為2，表示答案錯誤可能發生於中間 JSON 之後的轉換／匯入流程，需另案追蹤。

## 九、不得直接修正清單

- Q8／ID3835：需先建立結構污染證據文件。
- Q13／ID3840：需先建立答案錯誤與選項截斷證據文件。
- Q26–Q30、Q34–Q38：需先做等價題檢查，不得直接補入。
- Q11–Q15：涉及保險存摺、電子保單與紙本／網址規範，若後續改寫或補題，需保留教材版本與適用時點。
- Q34–Q38：不得未經法規版本審查，直接依現行法改寫或補入。

## 十、後續 correction ledger 候選

1. Q13／ID3840：`wrong_answer`, `truncated_option`，最高優先人工目視。
2. Q8／ID3835：`option_pollution`, `truncated_question`，第二優先人工目視。
3. Q26–Q30：5題漏題候選，需先等價題檢查。
4. Q34–Q38：5題漏題候選，需等價題及法規／教材版本審查。
5. Q11–Q15：時效性題群，答案未見全面衝突，但建議建立版本風險清單。

本報告本身不更新 correction ledger；只有人工確認或等價／版本審查完成後，才可依流程登記正式案例。

## 十一、執行過的唯讀命令與方法

- `git status -sb`
- `git rev-parse HEAD`
- `rg` 搜尋 `shiwu_raw.txt` 的 unit04／unit05 邊界與頁碼標記。
- 使用 `pypdf.PdfReader` 讀取 P.93–P.95 文字層。
- 使用 `pypdfium2` 將 P.93–P.95 暫時渲染至系統 Temp，逐頁視覺核對題號、選項及右側答案欄；未在 repository 新增渲染檔。
- 使用 Python `json` 唯讀查詢 `output/JY-人身保險.json` 與 `all_questions.json`。
- 使用 SQLite URI `mode=ro` 查詢 `platform/instance/insurance_exam.db`。
- 比對正式 JSON 與 SQLite 的 ID、題幹、選項、答案、subject、unit、解析。

## 十二、Git 狀態

建立本報告前：`## main...origin/main`。

本次只新增此 Markdown 報告；未修改 `all_questions.json`、SQLite、output JSON、platform 程式、correction ledger 或既有 docs。
