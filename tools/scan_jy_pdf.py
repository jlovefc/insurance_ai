# -*- coding: utf-8 -*-
"""
scan_jy_pdf.py - 掃描 JY-人身保險.pdf,統計題目表格與章節分佈
================================================================
目標:
  1. 找出每頁有無「題號 / 題目 / Ans」題目表格
  2. 從目錄與內文標題追蹤章節
  3. 統計每章題數
  4. 不寫入 DB,只印報表

用法:
    python tools\\scan_jy_pdf.py input\\JY-人身保險.pdf
"""
import argparse
import sys
import os
import re

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def is_question_table(table):
    """判斷 table 是否為題目表格(有 '題號' 'Ans' 等標題)"""
    if not table or len(table) < 2:
        return False
    header = table[0]
    if not header:
        return False
    header_str = ' '.join(str(c) for c in header if c)
    # 標題列含「題號」「題目」「Ans」或「解答」「答案」
    if ('題號' in header_str or '題目' in header_str) and \
       ('Ans' in header_str or '解答' in header_str or '答案' in header_str):
        return True
    return False


def count_questions(table):
    """數題目表格內有幾題(扣掉標題列)"""
    if not table:
        return 0
    return max(0, len(table) - 1)


def detect_chapter(page_text):
    """從頁面文字找章節標題
    範例: '一、 保險中重要的角色'  '十二、 洗錢防制法'
    """
    if not page_text:
        return None
    # 找形如「X、 標題」「X. 標題」的章節標題
    chapter_pattern = re.compile(
        r'^([一二三四五六七八九十廿卅]+[、.\s]+[^\n]{2,40})$',
        re.MULTILINE
    )
    matches = chapter_pattern.findall(page_text)
    if matches:
        # 過濾掉太短的或含亂碼的
        for m in matches:
            cleaned = m.strip()
            # 跳過明顯亂碼(含 @#$%^&*() 等)
            if re.search(r'[@#$%^&*()\[\]{}+_=]', cleaned):
                continue
            if 4 <= len(cleaned) <= 40:
                return cleaned
    return None


def detect_part(page_text):
    """偵測主分類(保險法規 / 保險實務)
    這份 PDF 是兩科合本,前半保險法規後半保險實務
    """
    if not page_text:
        return None
    # 大標題通常在頁首單獨一行
    lines = page_text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line == '保險法規' or line == '【保險法規】':
            return '保險法規'
        if line == '保險實務' or line == '【保險實務】':
            return '保險實務'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"X 找不到 {args.pdf}")
        sys.exit(1)

    try:
        import pdfplumber
    except ImportError:
        print("X 需要 pdfplumber,執行: pip install pdfplumber")
        sys.exit(1)

    print(f"掃描中: {args.pdf}\n")

    chapter_stats = {}  # {chapter_name: question_count}
    page_records = []   # 每頁 (page_num, part, chapter, question_count)
    current_chapter = None
    current_part = None
    total_questions = 0
    pages_with_table = 0

    with pdfplumber.open(args.pdf) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = page.extract_text() or ''

            # 偵測科目(保險法規/保險實務)
            part = detect_part(text)
            if part:
                current_part = part

            # 偵測章節
            chapter = detect_chapter(text)
            if chapter:
                current_chapter = chapter

            # 偵測題目表格
            tables = page.extract_tables()
            page_question_count = 0
            for tbl in tables:
                if is_question_table(tbl):
                    n = count_questions(tbl)
                    page_question_count += n

            if page_question_count > 0:
                pages_with_table += 1
                total_questions += page_question_count
                key = (current_part or '?', current_chapter or '?')
                chapter_stats[key] = chapter_stats.get(key, 0) + page_question_count

            page_records.append((page_num, current_part, current_chapter, page_question_count))

    # ====== 印報表 ======
    print("=" * 70)
    print(f"總頁數: {total_pages}")
    print(f"有題目表格的頁數: {pages_with_table}")
    print(f"找到題目總數: {total_questions}")
    print("=" * 70)

    print("\n【每章題數分佈】")
    print(f"{'科目':<10} {'章節':<40} {'題數':>5}")
    print("─" * 70)
    by_part = {}
    for (part, chapter), n in chapter_stats.items():
        by_part.setdefault(part, []).append((chapter, n))

    for part in sorted(by_part.keys()):
        part_total = 0
        for chapter, n in sorted(by_part[part], key=lambda x: -x[1]):
            print(f"{part:<10} {chapter:<40} {n:>5}")
            part_total += n
        print(f"{'':<10} {'  小計':<40} {part_total:>5}")
        print()

    print("=" * 70)
    print("\n【頁面分佈摘要】 (只印有題目的頁)")
    in_run = False
    run_start = 0
    run_part = None
    run_chapter = None
    run_count = 0
    for page_num, part, chapter, n in page_records:
        if n > 0:
            if not in_run:
                in_run = True
                run_start = page_num
                run_part = part
                run_chapter = chapter
                run_count = n
            elif part == run_part and chapter == run_chapter:
                run_count += n
            else:
                # 切換章節,印出上一段
                print(f"  p.{run_start}-{page_num-1}  [{run_part}] {run_chapter}: {run_count}題")
                run_start = page_num
                run_part = part
                run_chapter = chapter
                run_count = n
        else:
            if in_run:
                print(f"  p.{run_start}-{page_num-1}  [{run_part}] {run_chapter}: {run_count}題")
                in_run = False
                run_count = 0
    if in_run:
        print(f"  p.{run_start}-{total_pages}  [{run_part}] {run_chapter}: {run_count}題")

    print("\n掃描完成。")


if __name__ == "__main__":
    main()
