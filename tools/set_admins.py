# -*- coding: utf-8 -*-
"""
set_admins.py - 把 Humble 和 Chrisa 設為管理員
"""
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r'platform\instance\insurance_exam.db'
ADMINS = ['Humble', 'Chrisa']

c = sqlite3.connect(DB)
cur = c.cursor()

print("目標管理員:", ADMINS)
print()

for name in ADMINS:
    cur.execute("SELECT id, username, is_admin FROM users WHERE username = ?", (name,))
    row = cur.fetchone()
    if not row:
        print(f"  X {name}: 找不到此使用者,跳過")
        continue
    uid, uname, current = row
    if current == 1:
        print(f"  - {name}: 已是管理員(is_admin=1),跳過")
    else:
        cur.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (uid,))
        print(f"  ✅ {name}: 已設為管理員")

c.commit()

print("\n=== 確認結果 ===")
for uid, uname, is_admin in cur.execute(
    "SELECT id, username, is_admin FROM users ORDER BY id"
):
    flag = "管理員" if is_admin else ""
    print(f"  #{uid} {uname} {flag}")

c.close()
print("\n完成。")
