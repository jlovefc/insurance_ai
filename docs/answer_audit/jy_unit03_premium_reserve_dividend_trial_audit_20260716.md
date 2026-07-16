# JY 單元 03 逐題原稿校對試跑報告

- 執行日期：2026-07-16
- 性質：唯讀比對；除本報告外未修改任何檔案
- 原稿：`input/JY-人身保險.pdf`
- 單元：三、保險費架構、解約金、準備金、保單紅利
- 中間文字：`shiwu_raw.txt`
- 解析來源：`output/JY-人身保險.json`
- 正式快照：`all_questions.json`
- 正式執行資料：`platform/instance/insurance_exam.db`（SQLite URI `mode=ro`）

## 1. 檢查結論摘要

原稿單元位於標示頁 P.89–P.92，題號 1–53，共 53 題。依題幹關鍵字及去空白、標點正規化比對，39 題可同時對應 `all_questions.json` 與 SQLite，14 題無正式題庫記錄。可對應的 39 題中，38 題原稿答案與兩個正式來源一致；唯一答案不一致為原稿 Q18／SQLite ID 3815，原稿答案 1、系統答案 3。

`output/JY-人身保險.json` 僅有本單元 P.89 的 17 筆記錄（陣列索引 176–192），漏掉 P.89 Q6，且完全缺少 P.90–P.92 的 Q19–Q53。該 JSON 多筆含 OCR 亂碼、空選項或解析併入選項，因此只能作為中間來源線索。

正式資料確認 1 題選項污染（Q18／ID 3815）；另有 1 題疑似選項污染（Q34／ID 3785，第 4 項含題幹尾語「而有差別」），須人工目視。需人工目視清單共 15 題：14 題無正式對應，加上 Q34。ID 3815 已有人工目視證據，狀態為 `confirmed_by_source`，不計入待目視數。

## 2. 原稿單元範圍

| 原稿頁 | 題號 | 題數 | raw text 邊界 |
|---|---:|---:|---|
| P.89 | 1–18 | 18 | 單元標題後至 `JY89JY`；其後 18 個答案值 |
| P.90 | 19–34 | 16 | `JY89JY` 後至 `JY90JY`；其後 16 個答案值 |
| P.91 | 35–50 | 16 | `JY90JY` 後至 `JY91JY`；其後 16 個答案值 |
| P.92 | 51–53 | 3 | `JY91JY` 後至 `JY92JY`；其前後可辨識 3 個答案值 |
| 合計 | 1–53 | 53 | 下一單元「四、人身保險意義、功能、分類」為結束邊界 |

頁碼採原稿印刷／文字標記 `JY89JY` 至 `JY92JY`。題目與答案的配對依每頁題號順序及其 Ans 欄序列；若後續目視版面與文字層有衝突，以 PDF 目視為準。

## 3. 原稿題目清單

以下每筆的 `source_file` 均為 `input/JY-人身保險.pdf`，`source_unit` 均為「三、保險費架構、解約金、準備金、保單紅利」。選項依原稿作答選項順序記錄；「—」表示原稿未附解析。

| source_question_no | source_page | source_question_text | source_options | source_answer | source_explanation |
|---:|---:|---|---|---:|---|
| 1 | P.89 | 計算保險費時，使用生命表是為了計算保險費之何種因素 | 預定利率；預定死亡率；預定營業費用率；核保率 | 2 | — |
| 2 | P.89 | 用來作為計算將來要支付死亡保險金的保險費基礎是 | 預定死亡率；預定利率；預定營業費用；以上皆是 | 1 | — |
| 3 | P.89 | 保險費由那幾項因素組成？A.預估保險費；B.純保險費；C.附加保險費 | AB；BC；AC；ABC | 2 | — |
| 4 | P.89 | 為將來給付保險金財源，以預定死亡率與預定利率為基礎計算的保險費是？ | 純保險費；附加保險費；平準保險費；自然保險費 | 1 | — |
| 5 | P.89 | 下列何者為給付滿期保險金財源之保險費？ | 死亡保險費；生存保險費；附加保險費；營業保費 | 2 | — |
| 6 | P.89 | 為了克服自然保險費的缺點及簡化保險費的收取所設計每一期保險費數額皆相等的保險費稱為 | 平準保險費；賦課保險費；復效保險費；彈性保險費 | 1 | — |
| 7 | P.89 | 附加保費是為 | 壽險公司營運所需費用；給付意外事故、住院給付金、手術津貼等；累積責任準備金；以上皆是 | 1 | — |
| 8 | P.89 | 要保人所繳納之保險費稱為？ | 自然保險費；附加保險費；總保險費；純保險費 | 3 | — |
| 9 | P.89 | 純保險費的計算是根據是什麼原則？ | 收支相等；量出為入；盈餘預估原則；大數法則 | 1 | — |
| 10 | P.89 | 人壽保險保費計算基礎三種因素為？ | 預定死亡率、預定職業類別費率、預定利率；預定死亡率、預定利率、預定營業費用率；預定獲益率、預定利率、預定營業費用率；預定營業費用率、預定死亡率、預定職業類別費率 | 2 | — |
| 11 | P.89 | 死亡保險費計算基礎是根據何者？ | 預定死亡率；預定利率；預定營業費用率；以上皆是 | 1 | — |
| 12 | P.89 | 一萬名 30 歲男性各投保 100 萬一年期死亡保險，死亡率千分之二，每人純保費多少？ | 1 仟元；2 仟元；3 仟元；4 仟元 | 2 | 10000×2/1000＝20 人；20×1000000/10000＝2000 |
| 13 | P.89 | 1,000 名四十五歲男性各投保 1,000 萬一年期死亡保險，死亡率千分之六，每人保險費？ | 4 萬元；6 萬元；4 仟元；6 仟元 | 2 | — |
| 14 | P.89 | 一千名 30 歲女性各投保 2 千萬一年期死亡保險，死亡率千分之三，所列 A–D 敘述何者正確？ | ABC；BC；BD；AC | 1 | — |
| 15 | P.89 | 下列何者錯誤？ | 保險費與死亡率成正比；保險費與預定利率成正比；保險費與營業費用率成正比；以上皆非 | 2 | — |
| 16 | P.89 | 實際營業費用低於預定營業費用時，會產生？ | 費差損；費差益；利差損；死差益 | 2 | — |
| 17 | P.89 | 其他條件不變下，預定利率降低，保險費就會？ | 升高；沒有影響；不一定；降低 | 1 | — |
| 18 | P.89 | 定期保險下列何者不正確？A.保費與死亡率成正比；B.保費與利率成正比；C.保費與費用率成正比 | B；C；AC；ABC | 1 | 此題 B 錯誤；保費與利率成反比。若換問何者正確，答案為 3。 |
| 19 | P.90 | 若預定死亡率降低，定期保險的保險費就會？ | 一樣；不一定；便宜；貴 | 3 | — |
| 20 | P.90 | 年金生命表的死亡率愈高則其保險費？ | 沒有影響；愈高；愈低；不一定 | 3 | 年金是活著才能領，所以死亡率越高的族群保費越低。 |
| 21 | P.90 | 壽險付足多久以上保費或累積達有保單價值準備金，解約時應償付解約金？ | 半年；二年；僅限躉繳；一年 | 4 | — |
| 22 | P.90 | 民國 88 年起簽發之人壽保險單，有關解約金何者正確？ | AB；CD；AD；BC | 1 | — |
| 23 | P.90 | 以簽單保費利率及危險發生率為基礎計算之準備金？ | 保單價值準備金；保險費；責任準備金；解約金 | 1 | — |
| 24 | P.90 | 保單價值準備金之計算以何者為基礎？A.危險發生率；B.附加費用率；C.簽單保費利率；D.二年期定存利率平均值 | ABCD；BCD；AC；ABC | 3 | — |
| 25 | P.90 | 為履行保險金責任，於保費中提存之累積資金稱為 | 解約金；責任準備金；退休金；安定基金 | 2 | — |
| 26 | P.90 | 責任準備金之作用是在？ | 公司費用支出準備；保險給付準備；公司可用盈餘準備；以上皆是 | 2 | — |
| 27 | P.90 | 責任準備金提存與哪些費率因子有關？A.死亡率；B.營業費用率；C.利率 | AC；AB；BC；ABC | 1 | — |
| 28 | P.90 | 較穩健的責任準備金提存，相對保單價值準備金採何種利率、死亡率？ | BC；BD；AD；AC | 3 | — |
| 29 | P.90 | 下列何者正確？（保單招攬廣告與預定利率／紅利） | 不分紅保單廣告不得單獨強調預定利率；分紅保單廣告可記載預期紅利；可與定存利率比較；以上皆非 | 1 | — |
| 30 | P.90 | 保險費所累積的責任準備金，下列何者錯誤？ | 是保戶儲蓄；保戶承擔投資風險且無確保利潤；專家運作獲利較一般利息優厚；是有利投資 | 2 | — |
| 31 | P.90 | 將純保險費扣除已經過的危險保費後提存保管者為何？ | 解約金；保單紅利；責任準備金；保單價值準備金 | 3 | — |
| 32 | P.90 | 保險法所稱各種責任準備金包括哪些？A.賠款；B.差額；C.未滿期保費；D.特別 | ABD；BCD；ABC；ACD | 4 | — |
| 33 | P.90 | 終身壽險當期責任準備金累積越多時，淨危險保額會？ | 增加；減少；一樣；依投資情況 | 2 | 若責任準備金累積越少，淨危險保額會增加。 |
| 34 | P.90 | 責任準備金計算提存會因 A.保險期間；B.繳費方式；C.生效日；D.繳費期間而有差別 | ABD；BD；ABC；ABCD | 4 | — |
| 35 | P.91 | 超過一年人壽保險最低責任準備金，自何年起採二十五年滿期生死合險修正制？ | 九十二；九十一；八十八；八十七 | 3 | — |
| 36 | P.91 | 超過一年人壽保險最低責任準備金採二十年繳費終身保險修正制，始自民國何年？ | 九十五；八十七；九十四；八十八 | 1 | — |
| 37 | P.91 | 健康保險最低責任準備金之提存採用？ | 15 年繳費 15 年滿期修正制；公司自訂並核准；平衡準備金；一年定期修正制 | 4 | — |
| 38 | P.91 | 年金保險最低責任準備金提存採？ | 二十年滿期修正制；二十年繳費終身修正制；平衡準備金制；二十五年滿期修正制 | 3 | — |
| 39 | P.91 | 利率變動型人壽保險最低責任準備金提存採？ | 20 年滿期；25 年滿期；20 年繳費終身；主管機關另訂 | 4 | — |
| 40 | P.91 | 民國 95 年起純保費較 20 年繳費終身保險為大者，最低準備金採？ | 25 年繳費終身；1 年定期；20 年滿期；20 年繳費終身 | 4 | — |
| 41 | P.91 | 生存保險責任準備金之提存採用？ | 平衡準備金；一年定期；25 年繳費 25 年滿期；公司自訂並核准 | 1 | — |
| 42 | P.91 | 何種原因造成營運不確定性，主管機關公告停售強制分紅保單？ | 金控成立；投保率逾 100%；國民所得提高；利率下降 | 4 | — |
| 43 | P.91 | 實際死亡人數比預定死亡人數少時產生？ | 死差益；死差損；死差異；以上皆非 | 1 | — |
| 44 | P.91 | 人壽保險公司盈餘之利源是指？ | 死差益；利差益；費差益；以上皆是 | 4 | — |
| 45 | P.91 | 民國 93 年起分紅保單，保單分紅依據？ | 死差益；利差益；該險經營損益；費差益 | 3 | — |
| 46 | P.91 | 每保單年度終了應分配之保單紅利為哪些項目之和？A.利差；B.費差；C.死差 | AC；AB；BC；ABC | 1 | — |
| 47 | P.91 | 保單紅利支付方法有哪些？A.增額繳清；B.積存；C.抵繳保費；D.現金 | BCD；ACD；ABCD；ABC | 3 | — |
| 48 | P.91 | 以保單紅利扣抵保險費稱為？ | 增額繳清；抵繳保費；儲存生息；現金支付 | 2 | — |
| 49 | P.91 | 選擇儲存生息後，被保險人死亡時給付金額較原保額為？ | 高；一樣；低；不一定 | 2 | — |
| 50 | P.91 | 對保單面額與現金價值皆有影響的紅利選擇方式？ | 現金支付；增額繳清保險；儲存生息；抵繳保費 | 2 | — |
| 51 | P.92 | 傳統強制分紅保單依利差、死差計算，其分紅標準為何？ | 同時有利差益及死差益才分紅；僅有死差益即使利差損仍分紅；有任一差損仍分紅；以上皆非 | 2 | — |
| 52 | P.92 | 分紅方式與發放年度揭露，何者錯誤？ | 復效期間是否分紅由公司自訂；首次發放年度依商品訂定；失效解約是否分紅由公司自訂；身故年度是否分紅由公司自訂 | 1 | 復效者至少應依當年度經過期間比例給付紅利。 |
| 53 | P.92 | 分紅保險契約之敘述何者錯誤？ | 明訂分紅方式及決算基準日；展期後維持分紅特性；增額繳清部分可由公司決定分紅；減額繳清後維持分紅特性 | 2 | — |

## 4. 對應結果與逐題比對表

`json_id` 指 `all_questions.json` 的 `id`；該值與 SQLite `questions.id` 相同。`output_index` 是 `output/JY-人身保險.json` 的零起算陣列索引，該中間 JSON 本身沒有 id。`N/A` 表示沒有可比較的正式記錄或原稿無解析。

| source_question_no | source_page | output_index | sqlite_id | json_id | source_answer | system_answer | answer_match | option_match | explanation_match | issue_type | status | evidence_note | fix_suggestion |
|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 1 | P.89 | 176 | 3800 | 3800 | 2 | 2 | yes | yes | N/A | — | matched | 題幹正規化一致 | 無 |
| 2 | P.89 | 177 | 3801 | 3801 | 1 | 1 | yes | yes | N/A | intermediate_ocr_parse_error | matched | 正式資料已清除 output D 項亂碼 | 不改正式題庫；保留來源風險 |
| 3 | P.89 | 178 | 3802 | 3802 | 2 | 2 | yes | yes | N/A | intermediate_ocr_parse_error | matched | output 題幹含「筆記」 | 不改正式題庫 |
| 4 | P.89 | 179 | 3803 | 3803 | 1 | 1 | yes | yes | N/A | intermediate_ocr_parse_error | matched | output C 空白、D 亂碼；正式選項完整 | 不改正式題庫 |
| 5 | P.89 | 180 | 3804 | 3804 | 2 | 2 | yes | yes | N/A | — | matched | 題幹及選項一致 | 無 |
| 6 | P.89 | — | 3805 | 3805 | 1 | 1 | yes | yes | N/A | source_mapping_error | matched | output JSON 漏題，正式資料可由題幹對應 | 查明匯入來源，不直接修題 |
| 7 | P.89 | 181 | 3806 | 3806 | 1 | 1 | yes | yes | N/A | intermediate_ocr_parse_error | matched | output A、B 選項亂碼；正式資料完整 | 不改正式題庫 |
| 8 | P.89 | 182 | 3807 | 3807 | 3 | 3 | yes | yes | N/A | — | matched | 題幹及選項一致 | 無 |
| 9 | P.89 | 183 | 3808 | 3808 | 1 | 1 | yes | yes | N/A | intermediate_ocr_parse_error | matched | output 多個選項亂碼；正式資料完整 | 不改正式題庫 |
| 10 | P.89 | 184 | 3809 | 3809 | 2 | 2 | yes | yes | N/A | intermediate_ocr_parse_error | matched | output C 空白；正式資料完整 | 不改正式題庫 |
| 11 | P.89 | 185 | 3810 | 3810 | 1 | 1 | yes | yes | N/A | — | matched | 題幹及選項一致 | 無 |
| 12 | P.89 | 186 | — | — | 2 | — | N/A | N/A | N/A | source_mapping_error, explanation_missing | manual_review | output 題幹嚴重亂碼且解析併入 D；正式題庫無記錄 | 人工目視後登記候選，不直接補題 |
| 13 | P.89 | 187 | 3811 | 3811 | 2 | 2 | yes | yes | N/A | intermediate_truncated_question | matched | output 題幹錯置，正式題幹可可靠對應 | 不改正式題庫 |
| 14 | P.89 | 188 | — | — | 1 | — | N/A | N/A | N/A | source_mapping_error, truncated_question | manual_review | output 題幹嚴重污染；正式題庫無記錄 | 人工目視後登記候選 |
| 15 | P.89 | 189 | 3812 | 3812 | 2 | 2 | yes | yes | N/A | intermediate_option_pollution | matched | output D 項含異源亂碼；正式資料完整 | 不改正式題庫 |
| 16 | P.89 | 190 | 3813 | 3813 | 2 | 2 | yes | yes | N/A | — | matched | 題幹及選項一致 | 無 |
| 17 | P.89 | 191 | 3814 | 3814 | 1 | 1 | yes | yes | N/A | intermediate_truncated_question | matched | output 題幹為亂碼，正式題幹可對應 | 不改正式題庫 |
| 18 | P.89 | 192 | 3815 | 3815 | 1 | 3 | no | no | no | wrong_answer, ocr_parse_error, option_pollution, explanation_missing | confirmed_by_source | 原稿 P.89 Q18 右側答案欄為 1；第 4 項併入解析，解析欄空白 | 依既有修正紀錄列入 ready_to_fix；本次不修 |
| 19 | P.90 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error | manual_review | output、正式快照、SQLite 均無記錄 | 人工目視與來源追蹤 |
| 20 | P.90 | — | 3777 | 3777 | 3 | 3 | yes | yes | yes | source_mapping_error | matched | output 缺頁；正式資料含原稿解析 | 查明正式資料的實際匯入鏈 |
| 21 | P.90 | — | 3778 | 3778 | 4 | 4 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；題幹正規化對應 | 不改題庫 |
| 22 | P.90 | — | — | — | 1 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 三個來源均無正式記錄 | 人工目視與來源追蹤 |
| 23 | P.90 | — | 3779 | 3779 | 1 | 1 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 24 | P.90 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 三個來源均無正式記錄 | 人工目視與來源追蹤 |
| 25 | P.90 | — | 3780 | 3780 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 26 | P.90 | — | 3781 | 3781 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 27 | P.90 | — | 3782 | 3782 | 1 | 1 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；空白切割略異 | 不改題庫 |
| 28 | P.90 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 三個來源均無正式記錄 | 人工目視與來源追蹤 |
| 29 | P.90 | — | — | — | 1 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 三個來源均無正式記錄 | 人工目視與來源追蹤 |
| 30 | P.90 | — | 3783 | 3783 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 31 | P.90 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 原稿題幹前置詞在 raw 排序異常；正式無記錄 | 人工目視與來源追蹤 |
| 32 | P.90 | — | — | — | 4 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 三個來源均無正式記錄 | 人工目視與來源追蹤 |
| 33 | P.90 | — | 3784 | 3784 | 2 | 2 | yes | yes | yes | source_mapping_error | matched | 原稿解析與 SQLite 一致 | 不改題庫 |
| 34 | P.90 | — | 3785 | 3785 | 4 | 4 | yes | no | N/A | option_pollution | manual_review | 系統第 4 項為「ABCD，而有差別」；尾語語意屬題幹 | 目視 P.90 版面後登記候選 |
| 35 | P.91 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error, outdated_law | manual_review | 正式無記錄且涉及歷史法規時點 | 目視並標記教材版本 |
| 36 | P.91 | — | — | — | 1 | — | N/A | N/A | N/A | source_mapping_error, outdated_law | manual_review | 正式無記錄且涉及歷史法規時點 | 目視並標記教材版本 |
| 37 | P.91 | — | 3786 | 3786 | 4 | 4 | yes | yes | N/A | source_mapping_error, outdated_law | matched | output 缺頁；答案一致但法規時效待另案 | 不以現行法覆蓋教材答案 |
| 38 | P.91 | — | 3787 | 3787 | 3 | 3 | yes | yes | N/A | source_mapping_error, outdated_law | matched | output 缺頁；答案一致 | 不以現行法覆蓋教材答案 |
| 39 | P.91 | — | 3788 | 3788 | 4 | 4 | yes | yes | N/A | source_mapping_error, outdated_law | matched | output 缺頁；答案一致 | 不以現行法覆蓋教材答案 |
| 40 | P.91 | — | 3789 | 3789 | 4 | 4 | yes | yes | N/A | source_mapping_error, outdated_law | matched | output 缺頁；答案一致 | 不以現行法覆蓋教材答案 |
| 41 | P.91 | — | 3790 | 3790 | 1 | 1 | yes | yes | N/A | source_mapping_error, outdated_law | matched | output 缺頁；答案一致 | 不以現行法覆蓋教材答案 |
| 42 | P.91 | — | 3791 | 3791 | 4 | 4 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 43 | P.91 | — | 3792 | 3792 | 1 | 1 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 44 | P.91 | — | 3793 | 3793 | 4 | 4 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 45 | P.91 | — | 3794 | 3794 | 3 | 3 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 46 | P.91 | — | — | — | 1 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 正式無記錄 | 人工目視與來源追蹤 |
| 47 | P.91 | — | — | — | 3 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 正式無記錄 | 人工目視與來源追蹤 |
| 48 | P.91 | — | 3795 | 3795 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 49 | P.91 | — | — | — | 2 | — | N/A | N/A | N/A | source_mapping_error | manual_review | 正式無記錄 | 人工目視與來源追蹤 |
| 50 | P.91 | — | 3796 | 3796 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 51 | P.92 | — | 3797 | 3797 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |
| 52 | P.92 | — | 3798 | 3798 | 1 | 1 | yes | yes | yes | source_mapping_error | matched | 原稿解析與 SQLite 一致 | 不改題庫 |
| 53 | P.92 | — | 3799 | 3799 | 2 | 2 | yes | yes | N/A | source_mapping_error | matched | output 缺頁；正式資料可對應 | 不改題庫 |

## 5. 題目總數與對應統計

- 原稿題目：53 題。
- `output/JY-人身保險.json`：17 題（Q1–Q5、Q7–Q18），Q6 與 Q19–Q53 缺漏。
- `all_questions.json`：39 題可對應。
- SQLite：39 題可對應，id 與正式快照完全相同。
- 成功同時對應正式快照及 SQLite：39 題。
- 無法對應正式題庫：14 題（Q12、Q14、Q19、Q22、Q24、Q28、Q29、Q31、Q32、Q35、Q36、Q46、Q47、Q49）。
- 正式快照與 SQLite 的 content、options、correct_answer：39 題全部一致。

## 6. 答案一致題目

38 題：Q1–Q11、Q13、Q15–Q17、Q20–Q21、Q23、Q25–Q27、Q30、Q33–Q34、Q37–Q45、Q48、Q50–Q53。

這裡的「一致」僅表示原稿 Ans 欄、`all_questions.json.correct_answer` 與 SQLite `correct_answer` 的字面值一致，不表示法規時效或教材內容已另行實質審查。

## 7. 答案不一致題目

僅 1 題：Q18／ID 3815。原稿答案 1；`all_questions.json` 與 SQLite 均為 3。此案已有 P.89 人工目視證據。

14 題因正式題庫不存在，不能列為「答案不一致」，應列為無法對應／待人工處理。

## 8. 選項污染題目

### 正式題庫

1. Q18／ID 3815：第 4 項由 `ABC` 污染為 `ABC解析：……答案就會是`，已確認。
2. Q34／ID 3785：第 4 項為 `ABCD，而有差別。`，其中「而有差別」依句法應屬題幹尾語；列為疑似污染，待目視 P.90。

正式題庫選項污染計數：確認 1 題；含待目視候選共 2 題。

### 中間解析 JSON

Q2、Q4、Q7、Q9、Q10、Q12、Q15、Q18 共 8 題具有空選項、OCR 亂碼或解析併入選項。Q3、Q13、Q14、Q17 另有題幹污染／截斷。這些問題不得以中間 JSON 直接覆蓋正式題庫。

## 9. 解析缺漏或解析污染題目

- Q12：原稿有計算解析；正式題庫無此題。output JSON 將計算解析併入第 4 選項。
- Q18／ID 3815：原稿有解析；SQLite explanation 為空，且解析併入第 4 選項。
- Q20／ID 3777、Q33／ID 3784、Q52／ID 3798：原稿解析與 SQLite explanation 可對應。
- 其餘題目原稿未見獨立解析；系統空 explanation 不列為缺漏。

## 10. 需要人工目視確認題目

共 15 題：

1. 14 題無正式對應：Q12、Q14、Q19、Q22、Q24、Q28、Q29、Q31、Q32、Q35、Q36、Q46、Q47、Q49。
2. Q34／ID 3785：確認第 4 選項與題幹尾語的版面邊界。

優先頁次：P.90（8 題，含 Q34）、P.91（5 題）、P.89（2 題，Q12、Q14）、P.92 無新增待目視題。此計數按題去重。

## 11. 已知案例 ID 3815 再確認

- 原稿：`input/JY-人身保險.pdf` P.89，第 18 題。
- 題目：「定期保險下列何者不正確？」
- 原稿右側答案欄：1（既有人工目視確認）。
- 原稿第 4 作答選項：`ABC`。
- 原稿解析：B 錯誤，保險費與利率成反比；若換問何者正確，答案為 3。
- `all_questions.json` id 3815／SQLite questions.id 3815：答案 3，第 4 選項遭解析文字污染，explanation 空白。
- 結論：`wrong_answer, ocr_parse_error, option_pollution, explanation_missing`；狀態 `confirmed_by_source`。
- ID 2670 是「何者正確」的另一改寫題，未納入本單元對應，且不得與 ID 3815 合併。

## 12. 不得直接修正清單

本報告不授權修正任何題目。下列項目尤其不得直接處理：

1. ID 3815：雖已確認，仍須依既有修正流程備份、同步修正、驗證後另案執行。
2. ID 3785：尚待目視確認選項邊界。
3. 14 題無正式對應：不得直接新增或以 output JSON 覆蓋。
4. Q35–Q41 等法規時點題：不得用現行法直接覆蓋教材答案，須記錄教材／法規版本。
5. 所有 output JSON OCR 污染題：不得以 AI 推論自動改值。

## 13. 後續應登記到 correction ledger 的候選案例

| 優先級 | 候選 | 原因 | 建議狀態 |
|---|---|---|---|
| P0 | Q18／ID 3815 | 已確認答案錯誤、選項污染、解析缺漏 | 已登記；後續 `ready_to_fix` |
| P1 | Q34／ID 3785 | 疑似題幹尾語併入第 4 選項 | `manual_review` |
| P1 | Q12、Q14 | P.89 output 嚴重 OCR／切割錯誤且正式題庫缺漏 | `manual_review` |
| P1 | Q19、Q22、Q24、Q28、Q29、Q31、Q32 | P.90 正式題庫缺漏 | `manual_review` |
| P1 | Q35、Q36 | P.91 正式題庫缺漏且有法規時效 | `manual_review` |
| P2 | Q46、Q47、Q49 | P.91 正式題庫缺漏 | `manual_review` |
| P2 | output Q2、Q4、Q7、Q9、Q10、Q15 | 中間來源選項污染，但正式資料目前完整 | 來源重建流程候選 |

## 14. 執行過的唯讀命令

下列為本次實際使用的命令類型；SQLite 全程使用 URI `mode=ro`：

```powershell
Get-Location
git branch --show-current
git rev-parse HEAD
git status -sb
Test-Path docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md
Get-Content C:\Users\FCE\.codex\plugins\cache\openai-primary-runtime\pdf\26.715.12143\skills\pdf\SKILL.md
python -c "以 pathlib 唯讀搜尋 shiwu_raw.txt 的單元標題、JY89JY–JY92JY、題號與 Ans 欄"
python -c "以 json 模組唯讀列出 output/JY-人身保險.json 的章節、頁碼、題幹、選項與答案"
python -c "以 json 模組唯讀讀取 all_questions.json 並依 unit／正規化題幹比對"
python -c "以 sqlite3 URI file:...insurance_exam.db?mode=ro 查詢 questions 表"
python -c "逐題比較 source answer、JSON correct_answer、SQLite correct_answer、options 與 explanation"
git diff -- docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md
git status -sb
```

未執行 Flask、套件安裝、`git add`、`git commit` 或 `git push`。

## 15. git status -sb

建立報告前：

```text
## main...origin/main
```

建立報告後：

```text
## main...origin/main
?? docs/answer_audit/jy_unit03_premium_reserve_dividend_trial_audit_20260716.md
```

只有本報告為未追蹤新增檔；未 stage、未 commit、未 push。
