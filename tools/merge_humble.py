# -*- coding: utf-8 -*-
"""
merge_humble.py
合併 #1 humble → #2 Humble,然後刪除 #1。

處理的關聯表:
  - quiz_sessions
  - user_answers (透過 session 間接關聯,跟著 session 走)
  - weak_areas (要小心,如果 #2 已有同 unit 的紀錄,要合併數字)
  - user_question_marks (要小心,如果 #2 已有同 question_id 的紀錄,衝突)
"""
import sqlite3
import shutil
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r'platform\instance\insurance_exam.db'
OLD_ID = 1     # humble (小寫,要刪)
NEW_ID = 2     # Humble (要保留)


def backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = DB.replace('.db', f'.backup_merge_{ts}.db')
    shutil.copy2(DB, bak)
    return bak


def main():
    print(f"合併 #{OLD_ID} → #{NEW_ID}\n")

    bak = backup()
    print(f"已備份: {bak}\n")

    c = sqlite3.connect(DB)
    cur = c.cursor()

    # === 1. 確認兩個帳號都存在 ===
    cur.execute(
        "SELECT id, username, is_admin FROM users WHERE id IN (?, ?)",
        (OLD_ID, NEW_ID)
    )
    users = cur.fetchall()
    print("=== 合併前 ===")
    for u in users:
        print(f"  #{u[0]} {u[1]} (is_admin={u[2]})")
    print()

    if len(users) < 2:
        print("X 找不到兩個帳號,中止")
        c.close()
        return

    # === 2. 轉移 quiz_sessions (含 user_answers,因為透過 session_id 關聯,改 session 就夠) ===
    cur.execute("SELECT COUNT(*) FROM quiz_sessions WHERE user_id = ?", (OLD_ID,))
    n_sessions = cur.fetchone()[0]
    cur.execute(
        "UPDATE quiz_sessions SET user_id = ? WHERE user_id = ?",
        (NEW_ID, OLD_ID)
    )
    print(f"[1] quiz_sessions: 轉移 {n_sessions} 筆")

    # === 3. 轉移 weak_areas (要處理 unit 衝突) ===
    cur.execute("""
        SELECT id, unit, wrong_count, total_count
        FROM weak_areas WHERE user_id = ?
    """, (OLD_ID,))
    old_weak = cur.fetchall()
    n_weak_merged = 0
    n_weak_moved = 0
    for old_wa_id, unit, wrong, total in old_weak:
        # 看 NEW_ID 有沒有同 unit 的紀錄
        cur.execute(
            "SELECT id FROM weak_areas WHERE user_id = ? AND unit = ?",
            (NEW_ID, unit)
        )
        existing = cur.fetchone()
        if existing:
            # 合併數字
            cur.execute("""
                UPDATE weak_areas
                SET wrong_count = wrong_count + ?,
                    total_count = total_count + ?
                WHERE id = ?
            """, (wrong, total, existing[0]))
            # 刪掉舊的
            cur.execute("DELETE FROM weak_areas WHERE id = ?", (old_wa_id,))
            n_weak_merged += 1
        else:
            # 直接搬
            cur.execute(
                "UPDATE weak_areas SET user_id = ? WHERE id = ?",
                (NEW_ID, old_wa_id)
            )
            n_weak_moved += 1
    print(f"[2] weak_areas: 合併 {n_weak_merged} 筆,搬移 {n_weak_moved} 筆")

    # === 4. 轉移 user_question_marks (有 UniqueConstraint user_id+question_id) ===
    cur.execute("""
        SELECT id, question_id, mark_type, correct_streak, last_practiced
        FROM user_question_marks WHERE user_id = ?
    """, (OLD_ID,))
    old_marks = cur.fetchall()
    n_mark_kept = 0
    n_mark_moved = 0
    n_mark_dropped = 0
    for old_mark_id, qid, mtype, streak, last in old_marks:
        # 看 NEW_ID 有沒有同 question_id 的紀錄
        cur.execute("""
            SELECT id, mark_type FROM user_question_marks
            WHERE user_id = ? AND question_id = ?
        """, (NEW_ID, qid))
        existing = cur.fetchone()
        if existing:
            # 衝突:保留 NEW_ID 的(因為比較新),刪 OLD_ID 的
            cur.execute(
                "DELETE FROM user_question_marks WHERE id = ?",
                (old_mark_id,)
            )
            n_mark_dropped += 1
        else:
            # 直接搬
            cur.execute(
                "UPDATE user_question_marks SET user_id = ? WHERE id = ?",
                (NEW_ID, old_mark_id)
            )
            n_mark_moved += 1
    print(f"[3] user_question_marks: 搬移 {n_mark_moved},衝突丟棄 {n_mark_dropped}")

    # === 5. (如果有的話) user_explanations 也轉移 ===
    cur.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='user_explanations'
    """)
    if cur.fetchone():
        cur.execute(
            "UPDATE user_explanations SET user_id = ? WHERE user_id = ?",
            (NEW_ID, OLD_ID)
        )
        n_exp = cur.rowcount
        print(f"[4] user_explanations: 轉移 {n_exp} 筆")

    # === 6. 最後刪掉 OLD_ID 帳號 ===
    cur.execute("DELETE FROM users WHERE id = ?", (OLD_ID,))
    print(f"[5] 刪除 #{OLD_ID} humble 帳號")

    c.commit()

    # === 7. 確認結果 ===
    print()
    print("=== 合併後 ===")
    for uid, uname, is_admin in cur.execute(
        "SELECT id, username, is_admin FROM users ORDER BY id"
    ):
        flag = " 管理員" if is_admin else ""
        cur2 = c.cursor()
        cur2.execute("SELECT COUNT(*) FROM quiz_sessions WHERE user_id = ?", (uid,))
        n_s = cur2.fetchone()[0]
        cur2.execute("SELECT COUNT(*) FROM weak_areas WHERE user_id = ?", (uid,))
        n_w = cur2.fetchone()[0]
        cur2.execute("SELECT COUNT(*) FROM user_question_marks WHERE user_id = ?", (uid,))
        n_m = cur2.fetchone()[0]
        print(f"  #{uid} {uname}{flag}: {n_s} sessions, {n_w} weak_areas, {n_m} marks")

    c.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
