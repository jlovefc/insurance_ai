"""
diagnose_db.py
==============
列出 instance/insurance_exam.db 內的所有表名與欄位結構,
用來確認 Question 資料表實際叫什麼名字。
"""
import sqlite3
from pathlib import Path

CANDIDATES = [
    Path(r"C:\insurance_ai\platform\instance\insurance_exam.db"),
    Path(r"C:\insurance_ai\platform\insurance_exam.db"),
]

for db_path in CANDIDATES:
    if db_path.exists():
        break
else:
    print("找不到 DB 檔案")
    raise SystemExit(1)

print(f"DB: {db_path}\n")
conn = sqlite3.connect(str(db_path))

# 列所有表
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print(f"共找到 {len(tables)} 個資料表:\n")

for (table_name,) in tables:
    # 列每個表的欄位
    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  [{table_name}]  ({count} 筆資料)")
    for col in cols:
        print(f"     - {col[1]:<20} {col[2]}")
    print()

conn.close()
