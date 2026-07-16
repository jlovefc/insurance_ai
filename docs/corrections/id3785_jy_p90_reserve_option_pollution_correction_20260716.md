# ID 3785 題幹截斷與選項污染修正紀錄

- 紀錄日期：2026-07-16
- 文件性質：人工目視原稿確認後之正式修正紀錄
- 本文件僅記錄問題與後續修正方案；本次未修改 SQLite、JSON 或平台程式。

## 一、修正對象

- SQLite `questions.id`：3785
- `subject`：B 保險實務-分類
- `unit`：03 保險費架構、解約金、準備金、保單紅利
- 原稿題號：Q34

## 二、原稿來源

- 原稿：JY價值筆記／JY-人身保險.pdf
- 路徑：`input/JY-人身保險.pdf`
- 頁碼：P.90
- 章節：三、保險費架構、解約金、準備金、保單紅利
- 題號：34
- 人工目視確認：右側答案欄為 4

## 三、原稿題目結構

### 題幹

責任準備金計算與提存牽涉複雜的精算技術與法令規定，會因保險契約之 A.保險期間；B.繳費方式；C.契約生效日；D.繳費期間，而有差別。

### 作答選項

1. (1) ABD
2. (2) BD
3. (3) ABC
4. (4) ABCD

### 原稿答案

4

### 解析

原稿未見獨立解析。

## 四、目前系統錯誤狀態

- SQLite 與 `all_questions.json` 的 `correct_answer` 目前為 `4`，答案本身正確。
- `content` 缺少題幹句尾「，而有差別。」
- `options` 第 4 項目前為「ABCD   ，而有差別。」
- 「，而有差別。」被錯誤併入第 4 個選項。
- `explanation` 為空字串。

## 五、錯誤原因判斷

此題錯誤來自 PDF／OCR／JSON 轉換流程，將題幹句尾「，而有差別。」錯誤歸入第 4 個作答選項，造成題幹截斷與選項污染。此題不是答案錯誤，而是題目結構錯誤。

## 六、建議修正內容

後續應修正為：

```text
content = "責任準備金計算與提存牽涉複雜的精算技術與法令規定，會因保險契約之 A.保險期間；B.繳費方式；C.契約生效日；D.繳費期間，而有差別。"
options = ["ABD", "BD", "ABC", "ABCD"]
correct_answer = "4"
explanation = ""
```

## 七、狀態與錯誤類型

```text
status = confirmed_by_source
next_status = ready_to_fix
error_types = option_pollution, truncated_question
```

## 八、後續修正注意事項

1. 修正前需備份 SQLite。
2. 修正前需備份 `all_questions.json`。
3. SQLite 與 `all_questions.json` 應保持一致。
4. 此題不得標為 `wrong_answer`，因為原稿答案與系統答案皆為 4。
5. 修正目標只限 ID 3785。
6. 修正後需重新測試網頁顯示。
7. 修正後需產生 `git diff` 與 `git status`。
8. 修正後才可進入 commit。

