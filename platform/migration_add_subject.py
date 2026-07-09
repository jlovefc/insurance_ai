"""
migration_add_subject.py  (v2)
================================
為 insurance_ai 平台的「題目」資料表新增 subject 欄位。

v2 變更:
- 不再寫死表名為 'question',改用欄位特徵自動偵測
  (找有 content + correct_answer + options 三個欄位的表)
- 兼容 'question' / 'questions' / 任何自訂表名

放置位置:   C:\\insurance_ai\\platform\\migration_add_subject.py
執行方式:   (venv) C:\\insurance_ai\\platform> python migration_add_subject.py

執行前請務必先停掉 Flask (Ctrl+C),避免 SQLite 鎖檔。
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


def find_question_table(conn):
    """
    自動偵測題目資料表 — 找有 content + correct_answer + options 三個欄位的表。
    回傳表名,找不到回傳 None。
    """
    required_cols = {"content", "correct_answer", "options"}
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    for (table_name,) in tables:
        cols = {
            row[1]
            for row in conn.execute(f"PRAGMA table_info({table_name})")
        }
        if required_cols.issubset(cols):
            return table_name
    return None


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def backup_db(db_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.stem}.backup_{ts}{db_path.suffix}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def main():
    print("=" * 60)
    print(" Migration v2: 題目資料表新增 subject 欄位")
    print("=" * 60)

    # ── 找 DB ──
    db_path = find_db()
    if not db_path:
        print("\n[X] 找不到資料庫檔案,試過以下位置:")
        for p in CANDIDATES:
            print(f"     - {p}")
        print("\n如果 DB 在別的位置,請執行:")
        print("     python migration_add_subject.py <DB完整路徑>")
        sys.exit(1)
    print(f"\n[OK] 找到資料庫: {db_path}")

    # ── 備份 ──
    backup_path = backup_db(db_path)
    print(f"[OK] 已備份至: {backup_path.name}")

    # ── 連線 + 找表 ──
    conn = sqlite3.connect(str(db_path))
    try:
        table_name = find_question_table(conn)
        if not table_name:
            print("\n[X] 自動偵測失敗 — DB 內找不到符合特徵的題目資料表")
            print("    (需要有 content + correct_answer + options 三個欄位)")
            print("\n    請改執行 diagnose_db.py 查看實際表結構")
            sys.exit(1)
        print(f"[OK] 自動偵測到題目資料表: '{table_name}'")

        # 顯示處理前題數
        cur = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        before_count = cur.fetchone()[0]
        print(f"     表內現有 {before_count} 筆題目")

        # 已經有 subject 欄位就跳過 ALTER
        if column_exists(conn, table_name, "subject"):
            print("\n[i] subject 欄位已存在,跳過 ALTER TABLE")
        else:
            print(f"\n[+] 對 '{table_name}' 表新增 subject VARCHAR(50) 欄位...")
            conn.execute(
                f"ALTER TABLE {table_name} ADD COLUMN subject VARCHAR(50)"
            )

            # Backfill
            cur = conn.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE subject IS NULL"
            )
            null_count = cur.fetchone()[0]
            if null_count > 0:
                print(
                    f"[+] Backfill: 將 {null_count} 筆既有題目的 subject 設為 '未分類'"
                )
                conn.execute(
                    f"UPDATE {table_name} SET subject = '未分類' "
                    "WHERE subject IS NULL"
                )

        # 建立複合索引加速去重查詢
        idx_name = f"idx_{table_name}_subject_content"
        print(f"[+] 建立 (subject, content) 複合索引 '{idx_name}' (如未存在)...")
        conn.execute(
            f"CREATE INDEX IF NOT EXISTS {idx_name} "
            f"ON {table_name}(subject, content)"
        )

        conn.commit()

        # ── 驗證 ──
        print("\n" + "=" * 60)
        print(" 驗證結果")
        print("=" * 60)

        # 顯示新 schema
        cur = conn.execute(f"PRAGMA table_info({table_name})")
        print(f"\n'{table_name}' 表欄位:")
        for row in cur.fetchall():
            marker = "  <-- 新增" if row[1] == "subject" else ""
            print(f"     {row[0]:>3}. {row[1]:<20} {row[2]:<15}{marker}")

        # 題目分佈
        cur = conn.execute(
            f"SELECT COALESCE(subject, '(NULL)'), COUNT(*) "
            f"FROM {table_name} GROUP BY subject"
        )
        rows = cur.fetchall()
        if rows:
            print("\n目前題目分佈:")
            total = 0
            for sub, cnt in rows:
                print(f"     {sub:<15} {cnt} 題")
                total += cnt
            print(f"     {'-' * 25}")
            print(f"     {'合計':<15} {total} 題")
        else:
            print("\n資料表是空的 (沒題目)")

        # 索引
        cur = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND tbl_name=?",
            (table_name,),
        )
        print(f"\n'{table_name}' 表索引:")
        for (name,) in cur.fetchall():
            print(f"     - {name}")

        print("\n" + "=" * 60)
        print(" [OK] Migration 完成!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 編輯 platform\\app.py,套用 Question 模型 + load_questions 修改")
        print("  2. 重新啟動 Flask: python app.py")
        print("  3. 如有問題,可從備份還原:")
        print(f"       copy instance\\{backup_path.name} instance\\{db_path.name}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
