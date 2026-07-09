# -*- coding: utf-8 -*-
"""
fix_finmarket_unit.py
把 subject='金融市場常識' 且 unit IS NULL 的題目,unit 設為「全部題目」,
讓主 app 的科目下拉選單能正確顯示這個科目。
"""
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r'platform\instance\insurance_exam.db'

c = sqlite3.connect(DB)
cur = c.cursor()

# 先看現況
cur.execute("""
    SELECT COUNT(*) FROM questions
    WHERE subject = '金融市場常識' AND unit IS NULL
""")
before = cur.fetchone()[0]
print(f"準備更新: {before} 題")

# 更新
cur.execute("""
    UPDATE questions
    SET unit = '全部題目'
    WHERE subject = '金融市場常識' AND unit IS NULL
""")
c.commit()
print(f"已更新: {cur.rowcount} 題")

# 確認
cur.execute("""
    SELECT subject, unit, COUNT(*)
    FROM questions
    WHERE subject = '金融市場常識'
    GROUP BY subject, unit
""")
print("\n金融市場常識的 (subject, unit) 分佈:")
for row in cur.fetchall():
    print(f"  {row}")

c.close()
print("\n完成。請 Ctrl+F5 重新整理主 app 的 dashboard。")
