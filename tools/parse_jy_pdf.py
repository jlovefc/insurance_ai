# -*- coding: utf-8 -*-
"""
parse_jy_pdf.py - JY 人身保險 PDF parser
==========================================
從 input\JY-人身保險.pdf 抽出 321 題,輸出成 JSON。
不直接寫 DB,讓使用者預覽確認。

特性:
  - 追蹤當前 part (保險法規/保險實務) + chapter (章節)
  - 從表格抽題目,避開 PDF 反盜版亂碼浮水印
  - 章節偵測失敗時沿用上一個有效章節
  - 把題幹和 4 個選項拆開存

用法:
    python tools\\parse_jy_pdf.py
    # 預設讀 input\\JY-人身保險.pdf,寫 output\\JY-人身保險.json
"""
import argparse
import sys
import os
import re
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def is_question_table(table):
    if not table or len(table) < 2:
        return False
    header = table[0]
    if not header:
        return False
    header_str = ' '.join(str(c) for c in header if c)
    if ('題號' in header_str or '題目' in header_str) and \
       ('Ans' in header_str or '解答' in header_str or '答案' in header_str):
        return True
    return False


def detect_chapter(page_text):
    """從頁面文字找章節標題"""
    if not page_text:
        return None
    chapter_pattern = re.compile(
        r'^([一二三四五六七八九十廿卅]+[、.\s]+[^\n]{2,40})$',
        re.MULTILINE
    )
    matches = chapter_pattern.findall(page_text)
    if matches:
        for m in matches:
            cleaned = m.strip()
            if re.search(r'[@#$%^&*()\[\]{}+_=]', cleaned):
                continue
            if 4 <= len(cleaned) <= 40:
                return cleaned
    return None


def detect_part(page_text):
    if not page_text:
        return None
    lines = page_text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line == '保險法規' or line == '【保險法規】':
            return '保險法規'
        if line == '保險實務' or line == '【保險實務】':
            return '保險實務'
    return None


def clean_text(s):
    """清理儲存格文字:去除浮水印亂碼、合併多行"""
    if not s:
        return ''
    s = str(s)
    # 去除常見浮水印片段
    junk_patterns = [
        r'警告：[^！]*！',
        r'JY.{0,3}價值筆記',
        r'^[(（]\s*\d+\s*[)）]\s*\d+\s*[)）]\s*[A-Za-z0-9]+',
    ]
    for p in junk_patterns:
        s = re.sub(p, '', s)
    # 合併多行為單行(保留選項分隔)
    s = re.sub(r'\s*\n\s*', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def parse_question_cell(cell):
    """
    把題目儲存格拆成 stem + options
    範例輸入:
      "依洗錢防制法規定,金融機構對於一定金額以上之通貨交易,
       應確認客戶身分及留存客戶之交易紀錄,並應向指定之機構申報。
       所稱一定金額係指新台幣多少錢?
       (1)二百萬元以上 (2)二百五十萬元以上 (3)一百萬元以上 (4)五十萬元以上"

    輸出:
      stem = "依洗錢防制法規定..."
      options = {
        'A': '二百萬元以上',
        'B': '二百五十萬元以上',
        'C': '一百萬元以上',
        'D': '五十萬元以上'
      }
    """
    text = clean_text(cell)
    if not text:
        return None, None

    # 用 (1)(2)(3)(4) 切開
    # 因為亂碼,有時是 (1) 或 (1) ,容錯
    pattern = re.compile(r'[(（]\s*([1234])\s*[)）]')
    parts = pattern.split(text)
    # parts 結構: [stem, '1', opt1_text, '2', opt2_text, '3', opt3_text, '4', opt4_text]

    if len(parts) < 9:
        # 沒找到 4 個選項
        return text, None

    stem = parts[0].strip().rstrip('。').strip()
    options = {}
    letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        num = parts[i]
        opt_text = parts[i+1].strip()
        if num in letter_map:
            # 選項可能後面接了下一個選項的內容,因為我們已經切過,所以這裡是乾淨的
            # 不過末尾可能有殘餘空白或標點
            opt_text = opt_text.strip(' 。、,，')
            options[letter_map[num]] = opt_text

    if len(options) != 4:
        return stem, None

    return stem, options


def parse_answer(cell):
    """解析答案儲存格,回傳 'A'/'B'/'C'/'D'"""
    if not cell:
        return None
    text = clean_text(cell)
    # 找 1234 中的第一個數字
    m = re.search(r'[1234]', text)
    if not m:
        return None
    n = m.group(0)
    return {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}[n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="input/JY-人身保險.pdf")
    ap.add_argument("--out", default="output/JY-人身保險.json")
    ap.add_argument("--preview", type=int, default=5,
                    help="預覽前 N 題到 stdout")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"X 找不到 {args.pdf}")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

    try:
        import pdfplumber
    except ImportError:
        print("X 需要 pdfplumber: pip install pdfplumber")
        sys.exit(1)

    print(f"解析中: {args.pdf}")

    questions = []
    failed = []   # (page, reason, raw)
    current_part = None
    current_chapter = None

    with pdfplumber.open(args.pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = page.extract_text() or ''

            part = detect_part(text)
            if part:
                current_part = part

            chapter = detect_chapter(text)
            if chapter:
                current_chapter = chapter

            tables = page.extract_tables()
            for tbl in tables:
                if not is_question_table(tbl):
                    continue
                for row_idx, row in enumerate(tbl[1:], start=1):
                    if not row or len(row) < 3:
                        continue
                    qid_cell, q_cell, ans_cell = row[0], row[1], row[2]

                    # 跳過空列
                    if not q_cell:
                        continue

                    stem, options = parse_question_cell(q_cell)
                    answer = parse_answer(ans_cell)

                    if not stem or not options or not answer:
                        failed.append({
                            'page': page_num,
                            'row': row_idx,
                            'reason': f'stem={bool(stem)},options={len(options) if options else 0},answer={answer}',
                            'raw_q': str(q_cell)[:200],
                            'raw_ans': str(ans_cell)[:50]
                        })
                        continue

                    questions.append({
                        'page': page_num,
                        'part': current_part,
                        'chapter': current_chapter,
                        'stem': stem,
                        'options': options,
                        'answer': answer
                    })

    # 寫 JSON
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump({
            'source': args.pdf,
            'total': len(questions),
            'failed_count': len(failed),
            'questions': questions,
            'failed': failed
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功解析: {len(questions)} 題")
    print(f"❌ 解析失敗: {len(failed)} 題")
    print(f"📄 輸出: {args.out}")

    # 統計
    print("\n【科目 × 章節題數】")
    from collections import Counter
    counter = Counter((q['part'], q['chapter']) for q in questions)
    by_part = {}
    for (p, c), n in counter.items():
        by_part.setdefault(p, []).append((c, n))
    for p in sorted(by_part.keys(), key=lambda x: (x or '')):
        subtotal = 0
        for c, n in by_part[p]:
            print(f"  [{p}] {c}: {n}")
            subtotal += n
        print(f"  [{p}] 小計: {subtotal}\n")

    if failed:
        print(f"\n【失敗範例(前 3 個)】")
        for f in failed[:3]:
            print(f"  p.{f['page']} 列{f['row']}: {f['reason']}")
            print(f"    原文: {f['raw_q'][:100]}...")
        print(f"  (完整失敗清單在 {args.out} 的 'failed' 欄位)")

    print(f"\n【預覽前 {args.preview} 題】")
    for i, q in enumerate(questions[:args.preview]):
        print(f"\n── 題 {i+1} (p.{q['page']} / {q['part']} / {q['chapter']})")
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")


if __name__ == "__main__":
    main()
