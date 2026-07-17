# ID2664 責任準備金假設答案修正證據

## 一、案例性質

- 類型：既有題答案錯誤
- question_id：2664
- status：`confirmed_by_source`
- next_status：`ready_to_fix`
- issue_type：`wrong_answer / duplicate_conflict / explanation_conflict`

本文件僅記錄修正證據與建議內容，不代表正式題庫已完成修正。

## 二、目前系統資料

- subject：保險實務
- unit：第四章 人身保險的構造
- content：保險公司對於責任準備金之提存方式往往採取較穩健的作法，採比保單價值準備金 A 較低之預定利率；B 較高之預定利率；C 較低之預定死亡率；D 較高之預定死亡率
- options：`["BC", "BD", "AD", "AC"]`
- current correct_answer：`"1"`
- current answer concept：BC

目前答案指向第一項 BC，與原稿、等價題及穩健提存概念不一致。

## 三、原稿依據

- source：JY-人身保險.pdf / JY價值筆記
- source_page：P.90
- source_question_no：28
- source_answer：3
- source answer concept：AD
- evidence_file：`docs/corrections/p90_q28_jy_missing_candidate_20260716.md`

## 四、等價題依據

- equivalent_id：2197
- equivalent_answer：C，即 AD
- 判斷：ID2197 與 ID2664 為同題或高度等價題，且 ID2197 的答案與原稿一致。

## 五、ChatGPT 裁定

- ID2664 的 `correct_answer` 應由 `"1"` 改為 `"3"`。
- `options` 維持不變。
- 原因：穩健提存責任準備金應採較低預定利率與較高預定死亡率，即 AD。
- 現行解析自相矛盾，需重寫。

## 六、建議修正內容

```text
correct_answer = "3"
explanation = "保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率亦使死亡給付成本估計較高，因此答案為AD。"
```

`content` 與 `options` 均維持不變。正式修正時應同步更新 `all_questions.json` 與 SQLite `questions.id=2664`，並於修正前完成備份、修正後執行一致性及 Web 顯示驗證。
