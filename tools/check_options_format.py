# -*- coding: utf-8 -*-
"""
check_options_format.py - 看現有題目的 options 欄位格式
"""
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

c = sqlite3.connect(r'platform\instance\insurance_exam.db')

print("=== 抽樣 5 題,看欄位實際內容 ===\n")
sql = """
    SELECT id, subject, content, options, correct_answer, unit, explanation
    FROM questions
    WHERE subject = '保險法規'
    ORDER BY id LIMIT 5
"""
for row in c.execute(sql):
    qid, subject, content, options, ans, unit, expl = row
    print(f"── #{qid} [{subject}]")
    print(f"  content       : {(content or '')[:80]}")
    print(f"  options (raw) : {(options or '')[:200]}")
    print(f"  options type  : {type(options).__name__}, length={len(options or '')}")
    print(f"  correct_answer: {repr(ans)}")
    print(f"  unit          : {repr(unit)}")
    print(f"  explanation   : {(expl or '')[:80] if expl else '(none)'}")
    print()

c.close()
