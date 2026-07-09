# -*- coding: utf-8 -*-
"""
restore_and_audit.py
  1) 把 id=2 還原成「未分類」
  2) 用關鍵字找出疑似「教材導讀題」(垃圾題)
  3) 抽樣前 30 題,讓你目視確認
"""
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r'platform\instance\insurance_exam.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# ====== 1. 還原 #2 ======
print('=== 還原 #2 ===')
cur.execute("SELECT id, subject, substr(content,1,80) FROM questions WHERE id=2")
before = cur.fetchone()
print(f'還原前: {before}')

cur.execute("UPDATE questions SET subject='未分類' WHERE id=2")
conn.commit()

cur.execute("SELECT id, subject, substr(content,1,80) FROM questions WHERE id=2")
print(f'還原後: {cur.fetchone()}')
print()

# ====== 2. 確認分佈 ======
print('=== 目前 subject 分佈 ===')
for x in cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"):
    print(x)
print()

# ====== 3. 找疑似垃圾題 ======
# 關鍵字:教材、本書、應試、複習、學習方法、參閱章節、備考、本教材、考生
junk_keywords = [
    '教材', '本書', '本教材',
    '應試', '備考', '考生',
    '學習方法', '學習步驟', '學習指南',
    '複習', '複習方法', '複習策略',
    '參閱', '參閱章節', '參閱教材',
    '本章', '本節',
]

print('=== 疑似「教材導讀題」(命中下列關鍵字之一) ===')
print(f'關鍵字: {junk_keywords}')
print()

# 用 SQL OR 拼接
where = ' OR '.join([f"content LIKE '%{k}%'" for k in junk_keywords])
sql = f"""
    SELECT id, substr(content,1,100)
    FROM questions
    WHERE subject = '未分類'
    AND ({where})
    ORDER BY id
"""
hits = list(cur.execute(sql))
print(f'命中題數: {len(hits)} / 750\n')

print('=== 前 30 題預覽 ===')
for qid, preview in hits[:30]:
    print(f'#{qid:>4}  {preview}')

if len(hits) > 30:
    print(f'\n...還有 {len(hits)-30} 題,請看 tools\\junk_full.txt')
    # 寫完整清單到檔案
    with open('tools/junk_full.txt', 'w', encoding='utf-8') as f:
        for qid, preview in hits:
            f.write(f'#{qid}\t{preview}\n')
    print('  完整清單已存到 tools/junk_full.txt')

conn.close()
print('\n完成。請目視前 30 題,確認是否都該刪除。')
