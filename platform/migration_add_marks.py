"""
migration_add_marks.py
======================
為 insurance_ai 平台新增 user_question_marks 資料表,
用來記錄每個使用者對每題的「收藏 / 精熟」狀態,以及
連續答對次數(用於收藏題自動升級為精熟)。

放置位置:   C:\\insurance_ai\\platform\\migration_add_marks.py
執行方式:   (venv) PS C:\\insurance_ai\\platform> python migration_add_marks.py

特性:
- 可重複執行 (idempotent),已存在不會壞掉
- 會自動備份 DB
- 新表 schema:
    id            INTEGER 主鍵
    user_id       INTEGER 對應 users.id
    question_id   INTEGER 對應 questions.id
    mark_type     VARCHAR(20)  'favorite' / 'mastered' / NULL
    correct_streak INTEGER 連續答對次數
    last_practiced DATETIME
    UNIQUE(user_id, question_id)

執行前請先停掉 Flask (Ctrl+C)。
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


def table_exists(conn, table):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


def backup_db(db_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.stem}.backup_{ts}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    return backup


def main():
    print("=" * 60)
    print(" Migration: user_question_marks 表")
    print("=" * 60)

    db_path = find_db()
    if not db_path:
        print("\n[X] 找不到資料庫")
        for p in CANDIDATES:
            print(f"    - {p}")
        sys.exit(1)
    print(f"\n[OK] DB: {db_path}")

    backup = backup_db(db_path)
    print(f"[OK] 備份: {backup.name}")

    conn = sqlite3.connect(str(db_path))
    try:
        if table_exists(conn, "user_question_marks"):
            print("\n[i] user_question_marks 表已存在,跳過建表")
        else:
            print("\n[+] 建立 user_question_marks 表...")
            conn.execute("""
                CREATE TABLE user_question_marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    mark_type VARCHAR(20),
                    correct_streak INTEGER DEFAULT 0,
                    last_practiced DATETIME,
                    UNIQUE(user_id, question_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(question_id) REFERENCES questions(id)
                )
            """)
            print("[+] 建立索引...")
            conn.execute("CREATE INDEX idx_uqm_user_mark ON user_question_marks(user_id, mark_type)")
            conn.execute("CREATE INDEX idx_uqm_question ON user_question_marks(question_id)")

        conn.commit()

        # ── 驗證 ──
        print("\n" + "=" * 60)
        print(" 驗證")
        print("=" * 60)

        cur = conn.execute("PRAGMA table_info(user_question_marks)")
        print("\nuser_question_marks 欄位:")
        for row in cur.fetchall():
            print(f"     {row[0]:>3}. {row[1]:<20} {row[2]:<15}")

        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='user_question_marks'"
        )
        print("\n索引:")
        for (name,) in cur.fetchall():
            print(f"     - {name}")

        cur = conn.execute("SELECT COUNT(*) FROM user_question_marks")
        print(f"\n目前資料筆數: {cur.fetchone()[0]} (預期 0 — 新表)")

        print("\n" + "=" * 60)
        print(" [OK] Migration 完成!")
        print("=" * 60)
        print("\n下一步: 用新版 models.py + app.py 覆蓋,然後重啟 Flask")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
