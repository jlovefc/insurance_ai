# ID2654 儲存生息紅利答案修正證據

## 一、案例性質

- 類型：既有題答案錯誤
- question_id：2654
- status：`confirmed_by_source`
- next_status：`ready_to_fix`
- issue_type：`wrong_answer / duplicate_conflict / explanation_conflict`

本文件僅記錄修正證據與建議內容，不代表正式題庫已完成修正。

## 二、目前系統資料

- subject：保險實務
- unit：第四章 人身保險的構造
- content：如要保人選擇以儲存生息之方式給付紅利之後，當被保險人死亡時，保險人所給付之保險金額較原保險金額為
- options：`["高", "不一定", "一樣", "低"]`
- current correct_answer：`"1"`
- current answer concept：高

目前答案指向第一項「高」，將累積紅利總給付與原保單約定的保險金額混同。

## 三、原稿依據

- source：JY-人身保險.pdf / JY價值筆記
- source_page：P.91
- source_question_no：49
- source_answer：2
- source answer concept：一樣
- evidence_file：`docs/corrections/p91_q49_jy_missing_candidate_20260716.md`

## 四、等價題依據

- equivalent_id：2336
- equivalent_answer：C，即一樣
- 判斷：ID2336 與 ID2654 為同題或高度等價題，且 ID2336 的答案與原稿一致。

## 五、ChatGPT 裁定

- ID2654 的 `correct_answer` 應由 `"1"` 改為 `"3"`。
- `options` 維持不變。
- 原因：題目問的是保險金額是否改變。儲存生息紅利是紅利另行累積生息，不改變原保單保險金額。
- 現行解析將累積紅利總給付與原保險金額混同，需重寫。

## 六、建議修正內容

```text
correct_answer = "3"
explanation = "選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。"
```

`content` 與 `options` 均維持不變。正式修正時應同步更新 `all_questions.json` 與 SQLite `questions.id=2654`，並於修正前完成備份、修正後執行一致性及 Web 顯示驗證。
