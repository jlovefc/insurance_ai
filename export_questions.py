# -*- coding: utf-8 -*-
import sqlite3, json

db_path = r'C:\insurance_ai\platform\instance\insurance_exam.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 導出所有題目（排除已刪除）
cur.execute("""
    SELECT id, subject, unit, content, options, correct_answer
    FROM questions
    WHERE subject != '已刪除'
    ORDER BY subject, unit, id
""")

rows = cur.fetchall()
conn.close()

data = []
for row in rows:
    qid, subject, unit, content, options_str, correct_answer = row
    try:
        options = json.loads(options_str) if options_str else []
    except:
        options = [options_str]
    data.append({
        'id': qid,
        'subject': subject,
        'unit': unit,
        'content': content,
        'options': options,
        'correct_answer': str(correct_answer).strip()
    })

with open(r'C:\insurance_ai\all_questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"共導出 {len(data)} 題")
print("已存至 C:\\insurance_ai\\all_questions.json")
