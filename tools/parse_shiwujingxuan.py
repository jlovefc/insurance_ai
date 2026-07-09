# -*- coding: utf-8 -*-
"""
parse_shiwujingxuan.py - 人身保險業務員(保險實務)精選題包含解析
===============================================================
PDF 特性:
  - 4 欄表格: [題號, 章節名, 解答, 解析]
  - 表頭第 2 欄就是章節名稱 (例:「第一章 風險管理與保險」)
  - 章節隨頁面切換,parser 要追蹤
  - 題目格式混合:ABCD 子項 + (1)(2)(3)(4) 組合 / 純 (1)(2)(3)(4)
  - 答案 1-4,轉成 A-D
  - 解析欄位內容紮實,寫到 DB 的 explanation
  - 沒有反盜版浮水印 ✅

用法:
    python tools\\parse_shiwujingxuan.py
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


def clean_text(s, keep_newline=False):
    """清理儲存格文字"""
    if not s:
        return ''
    s = str(s)
    if keep_newline:
        # 解析欄位:多行內容用空格連接,但保留換行語意
        s = re.sub(r'\n\s*', '\n', s)
        s = re.sub(r'[ \t]+', ' ', s)
    else:
        s = re.sub(r'\s*\n\s*', '', s)
        s = re.sub(r'\s+', '', s)
    return s.strip()


def is_question_table(table):
    if not table or len(table) < 2:
        return False
    header = table[0]
    if not header or len(header) < 4:
        return False
    header_str = ' '.join(str(c) for c in header if c)
    if '解答' not in header_str:
        return False
    if '解析' not in header_str:
        return False
    return True


def detect_chapter_from_header(table):
    """從表頭第 2 欄抓章節名(像「第一章 風險管理與保險」)
    注意:這份 PDF 第一/第二章用康熙部首「⼀⼆」(U+2F00, U+2F01),
    而非標準漢字「一二」,所以兩種都要納入。
    """
    if not table or not table[0] or len(table[0]) < 2:
        return None
    second_cell = str(table[0][1]) if table[0][1] else ''
    second_cell = clean_text(second_cell)
    # 同時支援標準漢字 一二三四五六七八九十 和康熙部首 ⼀⼆⼃⼁⼂⼃⼄⼅⼆⼇
    # 實務上 PDF 只可能用「⼀⼆」(部首一二),所以只加這兩個就夠
    m = re.search(r'第[一二三四五六七八九十⼀⼆]+章\s*([^\n]{2,30})', second_cell)
    if m:
        chap_num = re.match(r'第[一二三四五六七八九十⼀⼆]+章', second_cell[m.start():]).group(0)
        chap_name = m.group(1).strip()
        # 把康熙部首換成標準漢字,讓章節名稱統一
        chap_num = chap_num.replace('⼀', '一').replace('⼆', '二')
        return f"{chap_num} {chap_name}"
    return None


def parse_question_text(text):
    """跟 parse_gaomingzhong 同一邏輯"""
    if not text:
        return None, None

    text = clean_text(text)
    pattern = re.compile(r'[(()]\s*([1-4])\s*[())]')
    parts = pattern.split(text)

    if len(parts) < 9:
        return None, None

    stem = parts[0].strip()
    options = {}
    letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    for i in range(1, len(parts) - 1, 2):
        num = parts[i]
        opt_text = parts[i + 1].strip()
        if num in letter_map and opt_text:
            opt_text = opt_text.strip(' 。、,,.')
            if opt_text.endswith('。'):
                opt_text = opt_text[:-1]
            options[letter_map[num]] = opt_text

    if len(options) != 4:
        return stem, None
    return stem, options


def parse_answer(cell):
    if not cell:
        return None
    text = clean_text(cell)
    m = re.search(r'[1-4]', text)
    if not m:
        return None
    return {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}[m.group(0)]


def parse_explanation(cell):
    """解析欄位:保留換行語意"""
    if not cell:
        return ''
    return clean_text(cell, keep_newline=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="input/實務精選題.pdf")
    ap.add_argument("--out", default="output/實務精選題.json")
    ap.add_argument("--preview", type=int, default=5)
    ap.add_argument("--debug", action="store_true",
                    help="印出每頁表格偵測詳情")
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
    failed = []
    current_chapter = None
    by_chapter = {}

    with pdfplumber.open(args.pdf) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            tables = page.extract_tables()

            if args.debug:
                print(f"\n[DEBUG] p.{page_num}: 找到 {len(tables)} 個表格")
                for ti, tbl in enumerate(tables):
                    header = tbl[0] if tbl else []
                    header_str = ' | '.join(str(c)[:40] if c else '' for c in (header or []))
                    is_q = is_question_table(tbl)
                    chap = detect_chapter_from_header(tbl)
                    print(f"  表{ti}: 列數={len(tbl) if tbl else 0}, 欄數={len(header) if header else 0}, "
                          f"is_q={is_q}, chapter={chap}")
                    print(f"    表頭: {header_str}")

            for tbl in tables:
                if not is_question_table(tbl):
                    continue

                # 從表頭抓章節
                chapter = detect_chapter_from_header(tbl)
                if chapter:
                    current_chapter = chapter

                if not current_chapter:
                    continue

                for row_idx, row in enumerate(tbl[1:], start=1):
                    if not row or len(row) < 4:
                        continue
                    qid_cell, q_cell, ans_cell, expl_cell = row[0], row[1], row[2], row[3]

                    if not q_cell:
                        continue

                    stem, options = parse_question_text(q_cell)
                    answer = parse_answer(ans_cell)
                    explanation = parse_explanation(expl_cell)

                    if not stem or not options or not answer:
                        failed.append({
                            'page': page_num,
                            'row': row_idx,
                            'qid_cell': clean_text(str(qid_cell))[:30],
                            'reason': f'stem={bool(stem)},options={len(options) if options else 0},answer={answer}',
                            'q_preview': clean_text(q_cell)[:150]
                        })
                        continue

                    questions.append({
                        'page': page_num,
                        'subject': '保險實務',
                        'chapter': current_chapter,
                        'qid_in_pdf': clean_text(str(qid_cell)),
                        'stem': stem,
                        'options': options,
                        'answer': answer,
                        'explanation': explanation
                    })
                    by_chapter[current_chapter] = by_chapter.get(current_chapter, 0) + 1

    output = {
        'source': args.pdf,
        'subject': '保險實務',
        'total': len(questions),
        'failed_count': len(failed),
        'by_chapter': by_chapter,
        'questions': questions,
        'failed': failed
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功: {len(questions)} 題")
    print(f"❌ 失敗: {len(failed)} 題")
    print(f"📄 輸出: {args.out}")

    # 章節分佈
    print(f"\n【章節分佈】")
    for ch, n in by_chapter.items():
        print(f"  {ch}: {n}")

    # 解析欄位統計
    with_expl = sum(1 for q in questions if q['explanation'])
    print(f"\n【解析欄位】")
    print(f"  有解析: {with_expl} / {len(questions)} ({with_expl*100//max(1,len(questions))}%)")

    if failed:
        print(f"\n【失敗範例】")
        for f in failed[:3]:
            print(f"  p.{f['page']} 列{f['row']} ({f['qid_cell']}): {f['reason']}")
            print(f"    {f['q_preview'][:120]}")

    print(f"\n【預覽前 {args.preview} 題】")
    for i, q in enumerate(questions[:args.preview]):
        print(f"\n── 題 {i+1} (p.{q['page']} / {q['chapter']} / #{q['qid_in_pdf']})")
        print(f"   題幹: {q['stem'][:150]}{'...' if len(q['stem']) > 150 else ''}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            opt = q['options'].get(letter, '?')
            print(f"   ({letter}) {opt[:80]}{'...' if len(opt) > 80 else ''}{mark}")
        if q['explanation']:
            expl_preview = q['explanation'].replace('\n', ' | ')[:200]
            print(f"   解析: {expl_preview}")

    # 抽樣末段
    if len(questions) > 5:
        print(f"\n【末段抽樣 (#{questions[-1]['qid_in_pdf']})】")
        q = questions[-1]
        print(f"── p.{q['page']} / {q['chapter']}")
        print(f"   題幹: {q['stem'][:150]}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')[:60]}{mark}")
        if q['explanation']:
            print(f"   解析: {q['explanation'].replace(chr(10),' | ')[:200]}")


if __name__ == "__main__":
    main()
