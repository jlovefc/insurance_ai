# -*- coding: utf-8 -*-
"""
migration_user_explanations.py
================================
為 user_explanations 功能準備資料庫:

  1. users 表加 is_admin 欄位(預設 0)
  2. 新建 user_explanations 表(每題可多筆使用者解說)
  3. 在 user_explanations 上建立 (question_id) 索引,加速查詢
  4. 自動備份 DB

執行(在 C:\\insurance_ai 目錄下):
    python tools\\migration_user_explanations.py

可逆:備份檔放在 platform\\instance\\
"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r'platform\instance\insurance_exam.db'


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(r[1] == column for r in cur.fetchall())


def table_exists(conn, table):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


def backup_db():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = DB.replace('.db', f'.backup_userexp_{ts}.db')
    shutil.copy2(DB, bak)
    return bak


def main():
    if not os.path.exists(DB):
        print(f"X 找不到 {DB}")
        sys.exit(1)

    print("=" * 60)
    print(" Migration: user_explanations 功能")
    print("=" * 60)

    bak = backup_db()
    print(f"\n已備份: {bak}\n")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # === 1. users 表加 is_admin 欄位 ===
    print("[1] users 表加 is_admin 欄位")
    if column_exists(conn, 'users', 'is_admin'):
        print("    已存在,跳過")
    else:
        cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("    ✅ 已新增")

    # === 2. 建 user_explanations 表 ===
    print("\n[2] 建 user_explanations 表")
    if table_exists(conn, 'user_explanations'):
        print("    已存在,跳過")
    else:
        cur.execute("""
            CREATE TABLE user_explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                report_count INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("    ✅ 已建立")

    # === 3. 索引 ===
    print("\n[3] 建立 question_id 索引")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_userexp_question_id "
        "ON user_explanations(question_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_userexp_user_id "
        "ON user_explanations(user_id)"
    )
    print("    ✅ 已建立(若不存在)")

    conn.commit()

    # === 4. 顯示現有 users 讓你確認誰要設為管理員 ===
    print("\n[4] 現有使用者")
    print(f"    {'ID':<5} {'username':<20} {'is_admin':<10}")
    print(f"    {'-'*5} {'-'*20} {'-'*10}")
    for uid, uname, is_admin in cur.execute(
        "SELECT id, username, is_admin FROM users ORDER BY id"
    ):
        print(f"    {uid:<5} {uname:<20} {is_admin}")

    conn.close()

    print("\n" + "=" * 60)
    print(" Migration 完成")
    print("=" * 60)
    print("\n下一步:把 Humble 和 Chrisa 設為管理員")
    print("用下面這個指令(請在 C:\\insurance_ai 跑):")
    print("\n  python tools\\set_admins.py")
    print("\n或之後可用 SQL 自行調整:")
    print("  UPDATE users SET is_admin=1 WHERE username IN ('Humble','Chrisa')")


if __name__ == "__main__":
    main()
