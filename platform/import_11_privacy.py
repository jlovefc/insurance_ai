# -*- coding: utf-8 -*-
import sqlite3, json, shutil
from datetime import datetime

db_path = r'C:\insurance_ai\platform\instance\insurance_exam.db'
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(db_path, db_path.replace('.db', f'.backup_11_{ts}.db'))
print('備份完成')

questions = [
    {"subject":"A 保險法規-分類","content":"保戶填寫要保書聲明同意保險人依個資法取得相關資料，即符合非公務機關於蒐集個資時，除符合特定目的外，亦符合：A.法律明文規定；B.與當事人有契約關係且已採取適當安全措施；C.經當事人同意；D.為增進公共利益所必要","options":json.dumps(["AB","AD","AC","BC"],ensure_ascii=False),"correct_answer":"4","unit":"11 個人資料保護法","explanation":"保戶同意保險人依個資法取得相關資料，所以跟A.法律、D.公共利益無關。","is_important":0},
    {"subject":"A 保險法規-分類","content":"非公務機關在蒐集個人資料時，除了須符合特定目的外，尚須具有下列何種情形始得為之？A.經當事人同意；B.當事人自行公開或其他已合法公開之個人資料；C.對當事人權益無侵害；D.為增進公共利益所必要","options":json.dumps(["ABCD","ABD","ABC","AB"],ensure_ascii=False),"correct_answer":"1","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"非公務機關在蒐集個人資料時，除了需符合目的外，尚須具有下列何種情形，使得為之？","options":json.dumps(["經當事人口頭同意書","雖未公開之資料但無害於當事人之重大權益者","為學術研究而有必要且無害於當事人之重大利益者","以上皆是"],ensure_ascii=False),"correct_answer":"3","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"個人資料保護法規範的對象主要是持有他人之個人資料者，分為公務機關及非公務機關兩類，下列何者為個人資料保護法規範的對象？","options":json.dumps(["保險業","金融業","受保險業委託處理資料之團體或個人","以上皆是"],ensure_ascii=False),"correct_answer":"4","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"當事人就其個人資料依個資法規定，行使「請求刪除」之權利，下列敘述何者錯誤？","options":json.dumps(["不得預先拋棄","不得以特約限制之","為尊重當事人得預先拋棄","以上皆正確"],ensure_ascii=False),"correct_answer":"3","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"保險公司應依下列那項法令之規範，就所掌握的保戶個人資料作最有效的運用？","options":json.dumps(["個人資料保護法","消費者保護法","保險法","公平交易法"],ensure_ascii=False),"correct_answer":"1","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"有關個人資料保護法，何者為非？","options":json.dumps(["姓名、出生年月日、身分證字號、指紋及護照號碼等皆屬個人資料","非公務機關蒐集個人資料僅須符合指定目的即得為之","保險公司蒐集保戶資料係符合特定目的、與當事人有契約關係且已採取適當之安全措施及經當事人同意等要件","當事人可請求刪除、停止處理或利用該個人資料"],ensure_ascii=False),"correct_answer":"2","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"個人資料保護法規範的行為態樣，主要可分為電腦處理、蒐集、利用、國際傳遞等。以非公務機關而言，在蒐集個人資料時除了須符合特定目的外，下列敘述何者為保險業所合乎的蒐集條件？","options":json.dumps(["經當事人書面同意者或與當事人有契約關係或類似契約之關係，且已採取適當之安全措施","當事人自行公開或其他已合法公開之個人資料","學術研究機構基於公共利益為學術研究而有必要，且資料經過提供者處理後或蒐集者依其揭露方式無從識別特定之當事人","與公共利益有關"],ensure_ascii=False),"correct_answer":"1","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"非公務機關為國際傳輸個人資料，而有下列何者情形者，中央目的事業主管機關得限制之？","options":json.dumps(["涉及國家重大利益","國際條約或協定有特別規定","接受國對於個人資料之保護未有完善之法規，致有損當事人權益之虞","以上皆是"],ensure_ascii=False),"correct_answer":"4","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"個人資料保護法因何而制訂？","options":json.dumps(["規範個人資料之蒐集、處理及利用","避免人格權受侵害","促進個人資料之合理利用","以上皆是"],ensure_ascii=False),"correct_answer":"4","unit":"11 個人資料保護法","explanation":"","is_important":0},
    {"subject":"A 保險法規-分類","content":"保險業於核保理賠時需蒐集當事人之特種個資，除經當事人書面同意外，須符合法律明文規定使得為之，下列何者為保險業蒐集之特種個資？A.健康檢查；B.病歷；C.指紋；D.職業","options":json.dumps(["ABCD","ABC","BC","AB"],ensure_ascii=False),"correct_answer":"4","unit":"11 個人資料保護法","explanation":"","is_important":1},
    {"subject":"A 保險法規-分類","content":"業務員銷售保險商品逕向要保人蒐集之資料，下列何者正確？","options":json.dumps(["不需告知要保人使用目的","屬公務機關之資料蒐集","若依法律規定得免告知者，得免為告知","法律雖有規定但基於保護消費者，皆需為告知，不得免除"],ensure_ascii=False),"correct_answer":"3","unit":"11 個人資料保護法","explanation":"","is_important":0},
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM questions')
before = cur.fetchone()[0]

inserted = skipped = 0
for q in questions:
    cur.execute('SELECT id FROM questions WHERE subject=? AND content=?', (q['subject'], q['content']))
    if cur.fetchone():
        skipped += 1
        continue
    cur.execute(
        "INSERT INTO questions (subject,content,options,correct_answer,unit,explanation,difficulty,is_important) VALUES (?,?,?,?,?,?,?,?)",
        (q['subject'], q['content'], q['options'], q['correct_answer'], q['unit'], q['explanation'], 'medium', q['is_important'])
    )
    inserted += 1

conn.commit()
cur.execute('SELECT COUNT(*) FROM questions')
after = cur.fetchone()[0]
conn.close()
print(f'新增:{inserted} 跳過:{skipped} 總題數:{before}->{after}')
