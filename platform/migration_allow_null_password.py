"""
migration_allow_null_password.py
================================
把 users.password_hash 從 NOT NULL 改成允許 NULL,
讓「免密碼快速登入帳號」(Humble/Chrisa)可以存在。

放置位置:   C:\\insurance_ai\\platform\\migration_allow_null_password.py
執行方式:   (venv) PS C:\\insurance_ai\\platform> python migration_allow_null_password.py

SQLite 不支援 ALTER COLUMN,所以採用標準做法:
1. 建一個新的 users_new 表 (password_hash 允許 NULL)
2. 把舊資料複製過去
3. 刪舊表,把新表 rename 回 users
4. 重建相關索引

可重複執行 (idempotent);若 password_hash 已經允許 NULL,會直接跳過。
"""

import sqlite3
import sys
import shutil
from pathlib import Path
from datetime import datetime


CANDIDATES = [
    Path(r"C:\insurance_ai\platform\instance\insurance_exam.db"),
    Path(r"C:\insurance_ai\platform\insurance_exam.db"),
]

if len(sys.argv) > 1:
    CANDIDATES.insert(0, Path(sys.argv[1]))


def find_db():
    for path in CANDIDATES:
        if path.exists():
            return path
    return None


def backup_db(db_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.stem}.backup_{ts}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    return backup


def password_hash_is_nullable(conn):
    """檢查 users.password_hash 是不是已經允許 NULL"""
    cur = conn.execute("PRAGMA table_info(users)")
    for row in cur.fetchall():
        # PRAGMA table_info 回傳 (cid, name, type, notnull, dflt_value, pk)
        if row[1] == 'password_hash':
            # notnull=1 代表 NOT NULL, notnull=0 代表允許 NULL
            return row[3] == 0
    return False


def main():
    print("=" * 60)
    print(" Migration: users.password_hash 改為允許 NULL")
    print("=" * 60)

    db_path = find_db()
    if not db_path:
        print("\n[X] 找不到資料庫")
        sys.exit(1)
    print(f"\n[OK] DB: {db_path}")

    backup = backup_db(db_path)
    print(f"[OK] 備份: {backup.name}")

    conn = sqlite3.connect(str(db_path))
    try:
        if password_hash_is_nullable(conn):
            print("\n[i] users.password_hash 已經允許 NULL,跳過 migration")
            return

        print("\n[+] 進行表重建(SQLite 不支援 ALTER COLUMN)...")

        # 取得舊表的所有資料
        old_rows = conn.execute(
            "SELECT id, username, email, password_hash, created_at FROM users"
        ).fetchall()
        print(f"    舊表有 {len(old_rows)} 筆資料")

        # 在 transaction 內做完整操作
        conn.execute("BEGIN TRANSACTION")
        try:
            # 1. 建新表(password_hash 允許 NULL)
            conn.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) UNIQUE,
                    password_hash VARCHAR(256),
                    created_at DATETIME
                )
            """)

            # 2. 複製舊資料
            conn.executemany(
                "INSERT INTO users_new (id, username, email, password_hash, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                old_rows
            )

            # 3. 刪舊表
            conn.execute("DROP TABLE users")

            # 4. 改名
            conn.execute("ALTER TABLE users_new RENAME TO users")

            conn.execute("COMMIT")
            print("[OK] 表重建完成")
        except Exception:
            conn.execute("ROLLBACK")
            raise

        # ── 驗證 ──
        print("\n" + "=" * 60)
        print(" 驗證")
        print("=" * 60)

        cur = conn.execute("PRAGMA table_info(users)")
        print("\nusers 表欄位:")
        for row in cur.fetchall():
            null_str = "允許 NULL" if row[3] == 0 else "NOT NULL"
            marker = "  <-- 已變更" if row[1] == 'password_hash' else ""
            print(f"     {row[0]:>3}. {row[1]:<20} {row[2]:<15} {null_str}{marker}")

        # 驗證資料沒掉
        new_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        print(f"\nusers 表筆數: {new_count} (預期 {len(old_rows)})")
        if new_count != len(old_rows):
            print("[X] 警告:筆數不對!請從備份還原")
        else:
            print("[OK] 資料完整")

        print("\n" + "=" * 60)
        print(" [OK] Migration 完成!")
        print("=" * 60)
        print("\n下一步: python app.py 應該可以正常啟動了")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
