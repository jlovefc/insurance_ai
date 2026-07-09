# -*- coding: utf-8 -*-
"""
diagnose_questions.py
快速診斷 questions 表的結構、未分類題分佈與來源欄位。

用法 (PowerShell):
    cd C:\\insurance_ai\\platform
    python tools\\diagnose_questions.py --db instance\\app.db
    # 或你實際的 DB 路徑
"""
import sqlite3
import sys
import argparse

# Windows 終端機顯示中文
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="SQLite DB 檔案路徑")
    ap.add_argument("--sample", type=int, default=15, help="隨機抽樣題數")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # 1. Schema
    print("=" * 60)
    print("【1】questions 表結構")
    print("=" * 60)
    cur.execute("PRAGMA table_info(questions)")
    cols = cur.fetchall()
    for cid, name, ctype, notnull, default, pk in cols:
        flags = []
        if pk:
            flags.append("PK")
        if notnull:
            flags.append("NOT NULL")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  {name:<25} {ctype}{flag_str}")
    all_col_names = [c[1] for c in cols]

    # 2. 科目分佈
    print()
    print("=" * 60)
    print("【2】subject 欄位分佈")
    print("=" * 60)
    cur.execute("""
        SELECT COALESCE(subject, '<NULL>') AS s, COUNT(*)
        FROM questions GROUP BY s ORDER BY 2 DESC
    """)
    rows = cur.fetchall()
    total = sum(r[1] for r in rows)
    for s, c in rows:
        print(f"  {s:<35} {c:>5}  ({c*100/total:.1f}%)")
    print(f"  {'─' * 35} {'─' * 5}")
    print(f"  {'總計':<35} {total:>5}")

    # 3. 未分類條件
    print()
    print("=" * 60)
    print("【3】未分類條件測試")
    print("=" * 60)
    conditions = [
        "subject IS NULL",
        "subject = ''",
        "subject = '未分類'",
        "(subject IS NULL OR subject = '' OR subject = '未分類')",
    ]
    for cond in conditions:
        cur.execute(f"SELECT COUNT(*) FROM questions WHERE {cond}")
        print(f"  {cond:<55} → {cur.fetchone()[0]}")

    # 4. 看有沒有 source/file/batch 之類的欄位
    print()
    print("=" * 60)
    print("【4】來源相關欄位偵測")
    print("=" * 60)
    source_hints = ["source", "file", "batch", "origin", "import", "from", "category"]
    source_cols = [c for c in all_col_names if any(h in c.lower() for h in source_hints)]
    if source_cols:
        print(f"  偵測到可能的來源欄位: {source_cols}\n")
        for col in source_cols:
            print(f"  [{col}] 在未分類題裡的分佈:")
            cur.execute(f"""
                SELECT COALESCE({col}, '<NULL>'), COUNT(*)
                FROM questions
                WHERE subject IS NULL OR subject = '' OR subject = '未分類'
                GROUP BY {col} ORDER BY 2 DESC LIMIT 15
            """)
            for v, c in cur.fetchall():
                vstr = str(v)[:55]
                print(f"    {vstr:<55} {c:>5}")
            print()
        print("  ⚠ 如果未分類題集中在某些 source,代表 OCR 那一批可能整批就是同一科")
    else:
        print("  沒找到 source/file/batch 之類的欄位")
        print("  → 無法用來源反推科目,需要靠題目內容分類")

    # 5. 內容欄位偵測
    print("=" * 60)
    print("【5】題目內容欄位偵測")
    print("=" * 60)
    content_hints = ["content", "text", "stem", "question", "body", "title"]
    content_cols = [c for c in all_col_names
                    if any(h in c.lower() for h in content_hints)]
    print(f"  候選欄位: {content_cols}")
    # 探每個欄位的平均長度
    for col in content_cols:
        try:
            cur.execute(f"""
                SELECT AVG(LENGTH(COALESCE({col}, ''))),
                       MAX(LENGTH(COALESCE({col}, '')))
                FROM questions
            """)
            avg, mx = cur.fetchone()
            print(f"    {col}: 平均長度 {avg:.0f}, 最長 {mx}")
        except sqlite3.OperationalError:
            pass

    # 6. 隨機抽樣
    print()
    print("=" * 60)
    print(f"【6】隨機抽樣 {args.sample} 題 (未分類)")
    print("=" * 60)
    # 用最像內容的欄位
    pick = None
    for c in ["content", "question_text", "question", "stem", "text"]:
        if c in all_col_names:
            pick = c
            break
    if not pick and content_cols:
        pick = content_cols[0]
    if not pick:
        print("  找不到內容欄位,跳過抽樣")
    else:
        print(f"  (使用欄位: {pick})\n")
        cur.execute(f"""
            SELECT id, COALESCE(subject, '<NULL>'),
                   substr(COALESCE({pick}, ''), 1, 220)
            FROM questions
            WHERE subject IS NULL OR subject = '' OR subject = '未分類'
            ORDER BY RANDOM() LIMIT ?
        """, (args.sample,))
        for qid, subj, preview in cur.fetchall():
            print(f"  ── #{qid}  subject={subj}")
            print(f"     {preview}")
            print()

    conn.close()
    print("=" * 60)
    print("診斷完成。請把 [1] schema、[3] 未分類數、[4] 來源欄位、[6] 抽樣")
    print("貼給我看,我會調整分類腳本的參數。")
    print("=" * 60)


if __name__ == "__main__":
    main()
