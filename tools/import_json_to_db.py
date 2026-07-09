# -*- coding: utf-8 -*-
"""
import_json_to_db.py - 把解析好的 JSON 題庫匯入 DB
====================================================
特色:
  - 自動備份 DB
  - 去重:題幹前 30 字 + 答案 做雜湊比對
  - dry-run 預設,需 --apply 才真寫入
  - 跳過的題目會列出來給你看
  - 顯示新舊分佈比較

用法:
  # 預覽(不寫入)
  python tools\\import_json_to_db.py output\\PartI-金融市場常識.json

  # 真寫入
  python tools\\import_json_to_db.py output\\PartI-金融市場常識.json --apply

  # 預設讀的 subject 來自 JSON 內的 'subject' 欄位,可用 --subject 覆蓋
  python tools\\import_json_to_db.py xxx.json --subject 保險法規 --apply
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
    """指紋用的正規化:去空白、全形半形統一"""
    if not s:
        return ''
    # 去除所有空白
    s = re.sub(r'\s+', '', s)
    # 全形標點 → 半形
    fullwidth_map = str.maketrans({
        '?': '?', ',': ',', '。': '.', ';': ';', ':': ':',
        '(': '(', ')': ')', '!': '!',
    })
    s = s.translate(fullwidth_map)
    return s.lower()


def fingerprint(stem, answer):
    """題幹前 30 字 + 答案 → MD5 雜湊"""
    normalized = normalize_for_hash(stem)[:30]
    key = f"{normalized}|{answer}"
    return hashlib.md5(key.encode('utf-8')).hexdigest()


def load_existing_fingerprints(conn):
    """掃 DB 現有所有題目,建立指紋集合"""
    fps = {}  # fp -> (id, subject, stem_preview)
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
    """{'A':'xx','B':'yy',...} → ["A. xx", "B. yy", "C. zz", "D. ww"]"""
    return [f"{letter}. {options[letter]}" for letter in ['A', 'B', 'C', 'D']]


def backup_db(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = os.path.dirname(db_path)
    basename = os.path.basename(db_path).replace('.db', '')
    backup_path = os.path.join(dirname, f"{basename}.backup_import_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file", help="JSON 檔路徑")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--subject", default=None,
                    help="強制指定 subject(預設讀 JSON 內的 subject 欄位)")
    ap.add_argument("--apply", action="store_true",
                    help="真寫入 DB(預設 dry-run)")
    ap.add_argument("--show-skipped", action="store_true",
                    help="列出跳過的重複題")
    args = ap.parse_args()

    if not os.path.exists(args.json_file):
        print(f"X 找不到 {args.json_file}")
        sys.exit(1)

    if not os.path.exists(args.db):
        print(f"X 找不到 DB {args.db}")
        sys.exit(1)

    # 讀 JSON
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    subject = args.subject or data.get('subject')
    if not subject:
        print("X JSON 沒有 subject 欄位,請用 --subject 指定")
        sys.exit(1)

    questions = data.get('questions', [])
    if not questions:
        print("X JSON 沒有題目")
        sys.exit(1)

    print(f"來源: {args.json_file}")
    print(f"目標 subject: {subject}")
    print(f"JSON 含題數: {len(questions)}")
    print(f"DB: {args.db}")
    print()

    # 連 DB
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # 印目前分佈
    print("=== 匯入前 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")
    print()

    # 建立現有指紋
    print("掃描 DB 現有題目建指紋...")
    existing_fps = load_existing_fingerprints(conn)
    print(f"現有 {len(existing_fps)} 個獨特指紋\n")

    # 比對
    to_insert = []
    skipped = []     # (q, dup_qid, dup_subject, dup_stem)
    fp_in_json = {}  # 防止 JSON 內部自己重複

    for q in questions:
        stem = q.get('stem', '')
        options = q.get('options', {})
        answer = q.get('answer', '')

        if not stem or not options or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
            skipped.append({'reason': '欄位缺失', 'stem': stem[:60]})
            continue

        fp = fingerprint(stem, answer)

        # 跟 DB 比
        if fp in existing_fps:
            dup_qid, dup_subject, dup_stem = existing_fps[fp]
            skipped.append({
                'reason': 'DB 已存在',
                'stem': stem[:60],
                'dup_qid': dup_qid,
                'dup_subject': dup_subject,
                'dup_stem': dup_stem
            })
            continue

        # 跟 JSON 自己比
        if fp in fp_in_json:
            prev = fp_in_json[fp]
            skipped.append({
                'reason': 'JSON 內重複',
                'stem': stem[:60],
                'dup_stem': prev[:60]
            })
            continue
        fp_in_json[fp] = stem

        to_insert.append(q)

    # 報告
    print("=== 比對結果 ===")
    print(f"  即將匯入: {len(to_insert)} 題")
    print(f"  跳過(重複或無效): {len(skipped)} 題")

    # 跳過原因細分
    by_reason = {}
    for s in skipped:
        by_reason[s['reason']] = by_reason.get(s['reason'], 0) + 1
    for reason, n in by_reason.items():
        print(f"    - {reason}: {n}")
    print()

    if args.show_skipped and skipped:
        print("=== 跳過題目清單 ===")
        for i, s in enumerate(skipped[:30]):
            print(f"  [{i+1}] [{s['reason']}] {s['stem']}")
            if s['reason'] == 'DB 已存在':
                print(f"      ↳ 對應 DB #{s['dup_qid']} [{s['dup_subject']}]: {s['dup_stem']}")
        if len(skipped) > 30:
            print(f"  ... 還有 {len(skipped) - 30} 題")
        print()

    # 寫入
    if not args.apply:
        print("⚠ DRY-RUN 模式:沒有寫入 DB")
        print("  確認沒問題後,加 --apply 真正寫入")
        print(f"  例: python tools\\import_json_to_db.py {args.json_file} --apply")
        conn.close()
        return

    if not to_insert:
        print("沒有題目要匯入,結束")
        conn.close()
        return

    # 備份
    backup_path = backup_db(args.db)
    print(f"已備份: {backup_path}\n")

    # 真寫入
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0
    for q in to_insert:
        opts_db = options_to_db_format(q['options'])
        options_json = json.dumps(opts_db, ensure_ascii=False)
        cur.execute("""
            INSERT INTO questions
                (content, options, correct_answer, unit, explanation,
                 difficulty, created_at, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q['stem'],
            options_json,
            q['answer'],
            None,           # unit (這份沒章節)
            None,           # explanation
            None,           # difficulty
            now,
            subject
        ))
        inserted += 1

    conn.commit()
    print(f"✅ 成功寫入 {inserted} 題\n")

    # 印新分佈
    print("=== 匯入後 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")

    conn.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
