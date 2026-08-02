# ID3835 JY P.93 Q8 題幹截斷與選項污染修正證據

## 一、案例性質

- 類型：既有題題目結構錯誤
- SQLite `questions.id`：3835
- source_question_no：8
- status：`confirmed_by_source`
- next_status：`ready_to_fix`
- issue_type：`option_pollution`, `truncated_question`, `ocr_parse_error`
- 是否為答案錯誤：否
- 是否已修改正式題庫：否

## 二、修正對象

- subject：B 保險實務-分類
- unit：04 人身保險意義、功能、分類
- 目前題幹：人身保險的意義，就是由？
- 目前答案：3

## 三、原稿來源

- 原稿：JY價值筆記／JY-人身保險.pdf
- 路徑：`input/JY-人身保險.pdf`
- 頁碼：P.93
- 章節：四、人身保險意義、功能、分類
- 題號：8
- 人工目視確認：右側答案欄為 3
- 視覺確認方式：直接檢視 PDF P.93 的題目表格、選項排列及右側答案欄。

## 四、原稿題目結構

原稿採「句首 + 四個主詞選項 + 共同句尾」的版面：

題幹句首：

> 人身保險的意義，就是由？

選項：

1. 許多窮苦的人們
2. 少數的社會熱心人士
3. 千千萬萬的人
4. 保險公司的員工

四個選項共同套用的題幹句尾：

> 出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活

原稿答案：3

原稿未見獨立解析。

## 五、目前正式題庫錯誤狀態

`all_questions.json` id=3835 與 SQLite `questions.id=3835` 目前逐欄一致：

```text
content = "人身保險的意義，就是由？"
options = [
  "許多窮苦的人們",
  "少數的社會熱心人士",
  "千千萬萬的人",
  "保險公司的員工 出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活"
]
correct_answer = "3"
explanation = ""  # SQLite
```

錯誤如下：

1. 題幹只保留句首，缺少原稿共同句尾。
2. 原稿共同句尾全部被併入第4選項。
3. 第4選項因此受到嚴重污染，並與其他三個選項不具相同層級。
4. 原稿與系統答案均為3，答案本身沒有衝突，不得標記為 `wrong_answer`。

## 六、中間 JSON 狀態

- 檔案：`output/JY-人身保險.json`
- 0-based record：199
- 1-based record：200
- page：93
- answer：`C`，對應第3項，與原稿答案一致
- stem：只保留「人身保險的意義，就是由？」
- option B：缺漏
- option C：遭異源 OCR 亂碼污染
- option D：混入共同題幹句尾及其他 OCR 雜訊

中間 JSON 的結構污染比正式題庫更嚴重，不得用來覆蓋正式題庫。本題正式修正應以 PDF 原稿目視結果為依據。

## 七、錯誤原因判斷

此題錯誤來自 PDF／OCR／JSON 轉換流程未能辨識「選項置於句中、後接共同題幹」的特殊版面。轉換流程將共同句尾錯誤歸入第4個選項，造成：

- 題幹截斷；
- 第4選項污染；
- 四個選項失去平行結構。

此題不是答案抓錯，也不涉及法規或教材版本時點。

## 八、建議修正內容

為符合 Web 題庫的「完整題幹在前、選項分列」結構，建議將原稿句中選項版面正規化如下；此調整只重建句法順序，不改變原稿題意：

```text
content = "人身保險的意義，就是由下列何者出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活？"
options = ["許多窮苦的人們", "少數的社會熱心人士", "千千萬萬的人", "保險公司的員工"]
correct_answer = "3"
explanation = ""
```

## 九、狀態與修正界線

- status：`confirmed_by_source`
- recommended_next_status：`ready_to_fix`
- fix_target：`all_questions.json` id=3835；SQLite `questions.id`=3835
- 修正欄位：`content`, `options`
- 不需變更：`correct_answer`, `subject`, `unit`
- SQLite `explanation` 維持空字串。

## 十、後續修正注意事項

1. 先將本案例登記到 correction ledger，再進入受控修正流程。
2. 修正前必須備份 `all_questions.json` 與 SQLite。
3. JSON 與 SQLite 必須同步修正。
4. 修正只限 ID3835，不得修改其他題目。
5. `correct_answer` 必須維持 `"3"`，不得標記為答案錯誤。
6. 修正後須驗證題數不變、非目標題未變及 SQLite `integrity_check = ok`。
7. Web 驗證須確認完整共同句尾位於題幹，第4選項只顯示「保險公司的員工」。
8. output JSON 本階段不修改。

## 十一、本次禁止事項確認

- 未修改 `all_questions.json`。
- 未修改 SQLite。
- 未修改 output JSON。
- 未修改 platform 程式。
- 未修改 correction ledger。
- 未執行 commit 或 push 前的題庫修正。
