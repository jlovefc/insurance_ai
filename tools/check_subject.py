# -*- coding: utf-8 -*-
"""
check_subject.py - 檢查目前 subject 狀態
"""
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

c = sqlite3.connect(r'platform\instance\insurance_exam.db')

print('=== id < 30 且非未分類非保險法規(就是剛才多分的) ===')
sql1 = (
    "SELECT id, subject, substr(content,1,80) "
    "FROM questions "
    "WHERE id < 30 "
    "AND subject != '未分類' "
    "AND subject != '保險法規' "
    "ORDER BY id"
)
for x in c.execute(sql1):
    print(x)

print()
print('=== 目前 subject 分佈 ===')
sql2 = "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
for x in c.execute(sql2):
    print(x)

c.close()
