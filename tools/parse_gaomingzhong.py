# -*- coding: utf-8 -*-
"""
parse_gaomingzhong.py - 人身保險業務員高命中精選題 PDF parser
==============================================================
PDF 特性:
  - 表格結構: [題號, 科目, 解答] 三欄
  - 表頭裡的「科目」欄位會是「保險實務」或「保險法規」,以此判斷該頁所屬科目
  - 題目內容混合兩種題型:
    (a) ABCD 子項 + (1)(2)(3)(4) 組合題
    (b) 直接 (1)(2)(3)(4) 普通題
  - 答案是阿拉伯數字 1-4,要轉成 A-D 跟 DB 一致
  - 沒有反盜版浮水印 ✅

用法:
    python tools\\parse_gaomingzhong.py
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


def clean_text(s):
    if not s:
        return ''
    s = str(s)
    # 把換行壓掉(因為一個儲存格可能跨多行)
    s = re.sub(r'\s*\n\s*', '', s)
    s = re.sub(r'\s+', '', s)
    return s.strip()


def is_question_table(table):
    """判斷是否為題目表格"""
    if not table or len(table) < 2:
        return False
    header = table[0]
    if not header or len(header) < 3:
        return False
    header_str = ' '.join(str(c) for c in header if c)
    # 標題列含「題號」「解答」
    if '題號' in header_str and '解答' in header_str:
        return True
    # 有些頁標題是「題題號號」(重複文字 OCR 殘留)
    if '題號' in header_str.replace('題題號號', '題號'):
        return '解答' in header_str
    return False


def detect_subject_from_header(table):
    """從表頭判斷此頁科目(保險實務 / 保險法規)"""
    if not table or not table[0]:
        return None
    header_str = ' '.join(str(c) for c in table[0] if c)
    if '保險實務' in header_str:
        return '保險實務'
    if '保險法規' in header_str:
        return '保險法規'
    return None


def parse_question_text(text):
    """
    解析題目內容,回傳 (stem, options dict)

    支援兩種格式:
    (a) 組合題:
        題幹?A xxx B xxx C xxx D xxx (1)BC (2)AB (3)AD (4)CD
        → stem = "題幹? A xxx; B xxx; C xxx; D xxx"
          options = {A:'BC', B:'AB', C:'AD', D:'CD'}

    (b) 普通題:
        題幹?(1)xxx(2)xxx(3)xxx(4)xxx
        → stem = "題幹?"
          options = {A:'xxx', B:'xxx', C:'xxx', D:'xxx'}
    """
    if not text:
        return None, None

    text = clean_text(text)

    # 用 (1)(2)(3)(4) 切開
    pattern = re.compile(r'[(()]\s*([1-4])\s*[())]')
    parts = pattern.split(text)
    # parts = [stem_part, '1', opt1, '2', opt2, '3', opt3, '4', opt4]

    if len(parts) < 9:
        return None, None

    stem_part = parts[0].strip()

    # 偵測 stem_part 是否含 A B C D 子項
    # 例:「有關解約金敘述何者正確?A躉繳保單之解約金等於B分期繳費...C躉繳保單之解約金小於D分期繳費...」
    abcd_pattern = re.compile(r'(?<=[?。])([A-D])\s*')
    abcd_matches = list(re.finditer(r'(^|[?。\s])([A-D])\s+', stem_part))

    # 但題幹也可能不含 ABCD 子項,直接是「題幹?」
    # 為了簡化,先抓出題幹的「主問句」,然後把 ABCD 子項(若有)當成題幹的一部分

    stem = stem_part.strip()

    # 收集 4 個選項
    options = {}
    letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    for i in range(1, len(parts) - 1, 2):
        num = parts[i]
        opt_text = parts[i + 1].strip()
        if num in letter_map and opt_text:
            # 去除前後標點
            opt_text = opt_text.strip(' 。、,,.')
            # 末尾可能黏到後續題目開頭,但因為 split 結構,這裡通常乾淨
            # 不過如果題目末尾有句號殘留,清掉
            if opt_text.endswith('。'):
                opt_text = opt_text[:-1]
            options[letter_map[num]] = opt_text

    if len(options) != 4:
        return stem, None

    return stem, options


def parse_answer(cell):
    """答案 cell 是 '1'/'2'/'3'/'4' → 轉成 'A'/'B'/'C'/'D'"""
    if not cell:
        return None
    text = clean_text(cell)
    m = re.search(r'[1-4]', text)
    if not m:
        return None
    return {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}[m.group(0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="input/高命中-人身保險.pdf")
    ap.add_argument("--out", default="output/高命中-人身保險.json")
    ap.add_argument("--preview", type=int, default=5)
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
    current_subject = None  # 從表頭抓出來的科目
    by_subject = {'保險實務': 0, '保險法規': 0}

    with pdfplumber.open(args.pdf) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            tables = page.extract_tables()
            for tbl in tables:
                if not is_question_table(tbl):
                    continue
                # 從表頭抓科目
                page_subject = detect_subject_from_header(tbl)
                if page_subject:
                    current_subject = page_subject

                if not current_subject:
                    continue

                # 逐列解析
                for row_idx, row in enumerate(tbl[1:], start=1):
                    if not row or len(row) < 3:
                        continue
                    qid_cell, q_cell, ans_cell = row[0], row[1], row[2]

                    if not q_cell:
                        continue

                    stem, options = parse_question_text(q_cell)
                    answer = parse_answer(ans_cell)

                    if not stem or not options or not answer:
                        failed.append({
                            'page': page_num,
                            'row': row_idx,
                            'qid_cell': str(qid_cell)[:30],
                            'reason': f'stem={bool(stem)},options={len(options) if options else 0},answer={answer}',
                            'q_preview': clean_text(q_cell)[:150]
                        })
                        continue

                    questions.append({
                        'page': page_num,
                        'subject': current_subject,
                        'qid_in_pdf': clean_text(str(qid_cell)),
                        'stem': stem,
                        'options': options,
                        'answer': answer
                    })
                    by_subject[current_subject] = by_subject.get(current_subject, 0) + 1

    # 寫 JSON
    output = {
        'source': args.pdf,
        'note': '兩科混合,各題依 page subject 標記',
        'total': len(questions),
        'failed_count': len(failed),
        'by_subject': by_subject,
        'questions': questions,
        'failed': failed
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功: {len(questions)} 題")
    print(f"❌ 失敗: {len(failed)} 題")
    print(f"📄 輸出: {args.out}")

    print(f"\n【科目分佈】")
    for s, n in by_subject.items():
        print(f"  {s}: {n}")

    if failed:
        print(f"\n【失敗範例(前 3 個)】")
        for f in failed[:3]:
            print(f"  p.{f['page']} 列{f['row']} ({f['qid_cell']}): {f['reason']}")
            print(f"    {f['q_preview']}")

    print(f"\n【預覽前 {args.preview} 題】")
    for i, q in enumerate(questions[:args.preview]):
        print(f"\n── 題 {i+1} (p.{q['page']} / {q['subject']} / #{q['qid_in_pdf']})")
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")

    # 抽樣每科一題
    impl_questions = [q for q in questions if q['subject'] == '保險實務']
    law_questions = [q for q in questions if q['subject'] == '保險法規']
    if impl_questions:
        print(f"\n【保險實務 末段抽樣】")
        q = impl_questions[-1]
        print(f"── p.{q['page']} #{q['qid_in_pdf']}")
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")
    if law_questions:
        print(f"\n【保險法規 抽樣】")
        q = law_questions[len(law_questions) // 2]
        print(f"── p.{q['page']} #{q['qid_in_pdf']}")
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")


if __name__ == "__main__":
    main()
