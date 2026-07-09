# -*- coding: utf-8 -*-
"""
import_shiwujingxuan.py - 匯入實務精選題,順便處理:
  1. 章節名稱康熙部首正規化(⼀⼆⼈⾝ → 一二人身)
  2. unit 欄位存章節名
  3. explanation 欄位存解析
  4. 同樣去重邏輯(題幹前 30 字 + 答案)
  5. dry-run 預設

用法:
    python tools\\import_shiwujingxuan.py output\\實務精選題.json
    python tools\\import_shiwujingxuan.py output\\實務精選題.json --apply
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

# 康熙部首 → 標準漢字 對照
RADICAL_MAP = {
    '⼀': '一', '⼆': '二', '⼈': '人', '⾝': '身',
    '⾦': '金', '⾸': '首', '⾷': '食', '⾺': '馬',
    '⽇': '日', '⽉': '月', '⽔': '水', '⽕': '火',
    '⽊': '木', '⼟': '土', '⼥': '女', '⼦': '子',
    '⼩': '小', '⼤': '大', '⼯': '工', '⼸': '弓',
    '⼿': '手', '⼼': '心', '⼝': '口', '⾔': '言',
    '⾞': '車', '⾨': '門', '⽴': '立', '⽣': '生',
    '⽤': '用', '⽥': '田', '⽯': '石', '⽰': '示',
    '⽻': '羽', '⾁': '肉', '⾃': '自', '⾄': '至',
    '⾎': '血', '⾏': '行', '⾺': '馬', '⿂': '魚',
    '⿃': '鳥', '⿈': '黃', '⿊': '黑',
}


def normalize_radicals(s):
    """把康熙部首換成標準漢字"""
    if not s:
        return s
    for radical, std in RADICAL_MAP.items():
        s = s.replace(radical, std)
    return s


def normalize_for_hash(s):
    if not s:
        return ''
    s = normalize_radicals(s)
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
    backup_path = os.path.join(dirname, f"{basename}.backup_shiwu_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    subject = data.get('subject', '保險實務')

    print(f"來源: {args.json_file}")
    print(f"目標 subject: {subject}")
    print(f"JSON 題數: {len(questions)}")
    print()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    print("=== 匯入前 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")
    print()

    print("掃描 DB 現有題目建指紋(套用部首正規化)...")
    existing_fps = load_existing_fingerprints(conn)
    print(f"現有 {len(existing_fps)} 個獨特指紋\n")

    to_insert = []
    skipped = []
    fp_in_json = {}

    for q in questions:
        stem = q.get('stem', '')
        options = q.get('options', {})
        answer = q.get('answer', '')
        chapter = q.get('chapter', '')
        explanation = q.get('explanation', '')

        if not stem or not options or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
            skipped.append({'reason': '欄位缺失', 'stem': stem[:60]})
            continue

        fp = fingerprint(stem, answer)

        if fp in existing_fps:
            dup_qid, dup_subject, dup_stem = existing_fps[fp]
            skipped.append({
                'reason': 'DB 已存在',
                'stem': stem[:60],
                'dup_qid': dup_qid,
                'dup_subject': dup_subject
            })
            continue

        if fp in fp_in_json:
            skipped.append({'reason': 'JSON 內重複', 'stem': stem[:60]})
            continue
        fp_in_json[fp] = stem

        # 章節名正規化(標題用,題幹保留原樣以維持原文)
        clean_chapter = normalize_radicals(chapter)

        to_insert.append({
            'stem': stem,
            'options': options,
            'answer': answer,
            'chapter': clean_chapter,
            'explanation': explanation
        })

    print("=== 比對結果 ===")
    print(f"  即將匯入: {len(to_insert)} 題")
    print(f"  跳過: {len(skipped)} 題")
    by_reason = {}
    for s in skipped:
        by_reason[s['reason']] = by_reason.get(s['reason'], 0) + 1
    for reason, n in by_reason.items():
        print(f"    - {reason}: {n}")

    # 章節分佈
    chap_dist = {}
    for q in to_insert:
        chap_dist[q['chapter']] = chap_dist.get(q['chapter'], 0) + 1
    print(f"\n  章節分佈:")
    for c, n in chap_dist.items():
        print(f"    {c}: {n}")
    print()

    if not args.apply:
        print("⚠ DRY-RUN 模式:沒有寫入 DB")
        print(f"  確認後加 --apply 真寫入")
        # 顯示跳過的範例
        dup_skipped = [s for s in skipped if s['reason'] == 'DB 已存在']
        if dup_skipped:
            print(f"\n=== 跳過範例(DB 已存在的前 5 個) ===")
            for s in dup_skipped[:5]:
                print(f"  #{s['dup_qid']} [{s['dup_subject']}]: {s['stem']}")
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
            q['chapter'],     # unit = 章節名
            q['explanation'],  # explanation = 解析
            None,
            now,
            subject
        ))

    conn.commit()
    print(f"✅ 成功寫入 {len(to_insert)} 題\n")

    print("=== 匯入後 subject 分佈 ===")
    for s, n in cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")

    print("\n=== 保險實務章節分佈 ===")
    for s, n in cur.execute(
        "SELECT unit, COUNT(*) FROM questions WHERE subject='保險實務' GROUP BY unit ORDER BY 2 DESC"
    ):
        print(f"  {s}: {n}")

    conn.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
