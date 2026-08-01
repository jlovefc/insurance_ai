# JY unit03 Q29／ID4141 正式補題前安全檢查

## 一、檢查目的

本文件記錄 `MISS-20260716-0008`（JY P.90 Q29）規劃補入為 ID4141 前的備份、完整性檢查與最終 dry-run 結果。本階段未執行 `--apply`，亦未修改正式題庫。

## 二、Q29／ID4141 補題草案摘要

- case_id：`MISS-20260716-0008`
- proposed_new_id：`4141`
- subject：`B 保險實務-分類`
- unit：`03 保險費架構、解約金、準備金、保單紅利`
- content：依金融監督管理委員會民國113年7月16日發布、同年11月1日生效之金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務時，下列有關銷售文件之敘述何者正確？
- options：`["不得單獨強調保費預定利率", "得以保單報酬率與銀行存款報酬率比較作為主要招攬訴求", "無須說明本保險不參加紅利分配及無紅利給付項目", "得將保費預定利率作為唯一銷售重點"]`
- correct_answer：`"1"`
- explanation：依金融監督管理委員會民國113年7月16日金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品業務，其銷售文件不得單獨強調保費預定利率，亦不得以保單報酬率與其他金融商品比較等方式誤導保戶；銷售文件、保險單面頁及保險單條款並應明確說明本保險為不分紅保險單、不參加紅利分配且無紅利給付項目。該令自民國113年11月1日生效，因此答案為第1項。

## 三、備份資訊

| 類型 | 備份路徑 | 檔案大小 |
|---|---|---:|
| JSON | `backups/all_questions_before_q29_4141_inclusion_20260716.json` | 2,093,429 bytes |
| SQLite | `backups/insurance_exam_before_q29_4141_inclusion_20260716.db` | 3,194,880 bytes |

SQLite 備份受 `.gitignore` 的資料庫規則排除，不應強制加入 Git。

## 四、SHA-256 與完整性檢查

### all_questions.json

- 正式檔 SHA-256：`90A28FD37B04F896C70611337F4CF5E9E35496700316D948483EF68D260F941F`
- 備份檔 SHA-256：`90A28FD37B04F896C70611337F4CF5E9E35496700316D948483EF68D260F941F`
- 比對結果：一致。

### SQLite

- 正式檔 SHA-256：`AB816D088993ED044F8AD2B99025E5151ABC52C18877B0316DF2F5FFA0B43B1F`
- 備份檔 SHA-256：`AB816D088993ED044F8AD2B99025E5151ABC52C18877B0316DF2F5FFA0B43B1F`
- 比對結果：一致。
- 備份 DB `PRAGMA integrity_check`：`ok`
- 正式 DB `PRAGMA integrity_check`：`ok`

## 五、最終 dry-run 結果

執行命令：

```text
python tools/apply_missing_question_4141_q29.py
```

未執行：

```text
python tools/apply_missing_question_4141_q29.py --apply
```

檢查結果：

- dry-run：成功。
- `all_questions.json` SHA-256：執行前後一致。
- SQLite 正式檔 SHA-256：執行前後一致。
- `all_questions.json` 題數：維持 4,127。
- SQLite `questions` 題數：維持 4,140。
- `all_questions.json` 最大 ID：維持 4140。
- SQLite `questions` 最大 ID：維持 4140。
- ID4141 存在於 `all_questions.json`：否。
- ID4141 存在於 SQLite：否。
- SQLite `integrity_check`：`ok`。

## 六、結論與下一步

本次僅建立正式補題前備份並完成最終 dry-run。ID4141 尚未正式補入，`all_questions.json` 與 SQLite 正式檔均未修改；output JSON、platform 程式及 correction ledger 亦未修改。

下一步必須取得對 Q29／ID4141 執行 `--apply` 的明確核准，方可正式同步修改 `all_questions.json` 與 SQLite。正式執行後仍須驗證題數、內容一致性、SQLite 完整性、差異範圍及 Web 顯示。
