# -*- coding: utf-8 -*-
"""
import_mixed_json_to_db.py - 匯入「每題各自 subject」的 JSON
============================================================
用於 parse_gaomingzhong.py 等多 subject 混合的 JSON 來源。
每個 question dict 內必須有 'subject' 欄位。

去重邏輯與 import_json_to_db.py 相同:題幹前 30 字 + 答案。

用法:
    # dry-run
    python tools\\import_mixed_json_to_db.py output\\高命中-人身保險.json

    # 真寫入
    python tools\\import_mixed_json_to_db.py output\\高命中-人身保險.json --apply
"""
import argparse
import sys
import os
import re
import json
import sqlite3
import shutil
import hashlib
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_DB = r"platform\instance\insurance_exam.db"


def normalize_for_hash(s):
    if not s:
        return ''
    s = re.sub(r'\s+', '', s)
    fullwidth_map = str.maketrans({
        '?': '?', ',': ',', '。': '.', ';': ';', ':': ':',
        '(': '(', ')': ')', '!': '!',
    })
    s = s.translate(fullwidth_map)
    return s.lower()


def fingerprint(stem, answer):
    normalized = normalize_for_hash(stem)[:30]
    key = f"{normalized}|{answer}"
    return hashlib.md5(key.encode('utf-8')).hexdigest()


def load_existing_fingerprints(conn):
    fps = {}
    cur = conn.cursor()
    cur.execute("SELECT id, subject, content, correct_answer FROM questions")
    for qid, subject, content, ans in cur.fetchall():
        if not content or not ans:
            continue
        fp = fingerprint(content, ans)
        if fp not in fps:
            fps[fp] = (qid, subject, content[:50])
    return fps


def options_to_db_format(options):
    return [f"{letter}. {options[letter]}" for letter in ['A', 'B', 'C', 'D']]


def backup_db(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = os.path.dirname(db_path)
    basename = os.path.basename(db_path).replace('.db', '')
    backup_path = os.path.join(dirname, f"{basename}.backup_mixedimport_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.json_file):
        print(f"X 找不到 {args.json_file}")
        sys.exit(1)
    if not os.path.exists(args.db):
        print(f"X 找不到 DB {args.db}")
        sys.exit(1)

    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    if not questions:
        print("X JSON 沒有題目")
        sys.exit(1)

    # 檢查每題都有 subject
    missing_subj = [i for i, q in enumerate(questions) if not q.get('subject')]
    if missing_subj:
        print(f"X 有 {len(missing_subj)} 題沒有 subject 欄位,中止")
        sys.exit(1)

    print(f"來源: {args.json_file}")
    print(f"JSON 含題數: {len(questions)}")

    # 統計每科題數
    by_subj = {}
    for q in questions:
        s = q['subject']
        by_subj[s] = by_subj.get(s, 0) + 1
    print(f"JSON 內 subject 分佈:")
    for s, n in by_subj.items():
        print(f"  {s}: {n}")
    print()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    print("=== 匯入前 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")
    print()

    print("掃描 DB 現有題目建指紋...")
    existing_fps = load_existing_fingerprints(conn)
    print(f"現有 {len(existing_fps)} 個獨特指紋\n")

    to_insert = []
    skipped = []
    fp_in_json = {}

    for q in questions:
        stem = q.get('stem', '')
        options = q.get('options', {})
        answer = q.get('answer', '')
        subject = q.get('subject', '')

        if not stem or not options or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
            skipped.append({'reason': '欄位缺失', 'stem': stem[:60]})
            continue

        fp = fingerprint(stem, answer)

        if fp in existing_fps:
            dup_qid, dup_subject, dup_stem = existing_fps[fp]
            skipped.append({
                'reason': 'DB 已存在',
                'stem': stem[:60],
                'subject': subject,
                'dup_qid': dup_qid,
                'dup_subject': dup_subject
            })
            continue

        if fp in fp_in_json:
            skipped.append({'reason': 'JSON 內重複', 'stem': stem[:60]})
            continue
        fp_in_json[fp] = stem

        to_insert.append(q)

    print("=== 比對結果 ===")
    # 依 subject 分組顯示
    insert_by_subj = {}
    for q in to_insert:
        insert_by_subj[q['subject']] = insert_by_subj.get(q['subject'], 0) + 1
    print(f"  即將匯入: {len(to_insert)} 題")
    for s, n in insert_by_subj.items():
        print(f"    - {s}: {n}")

    print(f"  跳過: {len(skipped)} 題")
    by_reason = {}
    for s in skipped:
        by_reason[s['reason']] = by_reason.get(s['reason'], 0) + 1
    for reason, n in by_reason.items():
        print(f"    - {reason}: {n}")
    print()

    if not args.apply:
        print("⚠ DRY-RUN 模式:沒有寫入 DB")
        print(f"  確認沒問題後,加 --apply 真寫入")
        conn.close()
        return

    if not to_insert:
        print("沒有題目要匯入,結束")
        conn.close()
        return

    backup_path = backup_db(args.db)
    print(f"已備份: {backup_path}\n")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for q in to_insert:
        opts_db = options_to_db_format(q['options'])
        cur.execute("""
            INSERT INTO questions
                (content, options, correct_answer, unit, explanation,
                 difficulty, created_at, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q['stem'],
            json.dumps(opts_db, ensure_ascii=False),
            q['answer'],
            None,
            None,
            None,
            now,
            q['subject']
        ))

    conn.commit()
    print(f"✅ 成功寫入 {len(to_insert)} 題\n")

    print("=== 匯入後 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")

    conn.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
