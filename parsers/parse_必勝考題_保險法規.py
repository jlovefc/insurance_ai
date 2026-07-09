"""
parse_必勝考題_保險法規.py  (v2)
=================================
把「必勝考題_保險法規.pdf」轉成平台用的 JSON 題庫。

放置位置:   C:\\insurance_ai\\parsers\\parse_必勝考題_保險法規.py
執行方式:   (venv) C:\\insurance_ai> python parsers\\parse_必勝考題_保險法規.py

輸入:
   C:\\insurance_ai\\source_pdfs\\必勝考題_保險法規.pdf

輸出:
   C:\\insurance_ai\\output\\question_bank_必勝考題_保險法規.json

v2 變更:
- 新增「中文字之間偽空白」清理(處理 PDF 內部換行造成的 "轉保 險" 之類問題)
- 章節名的空白保留(例如「第一章 人身保險契約」中間的空白)

PDF 結構特徵:
- 表格 3 欄: [題號, 題目本文, 解答]
- 題號格式 X-Y (例如 1-1, 5-67)
- 章節列: 第 1 欄是章名,後兩欄為 None
- 答案為阿拉伯數字 1/2/3/4,腳本會轉成 A/B/C/D
- 選項標記為 (1)(2)(3)(4) 或全形 （1）（2）（3）（4）
"""

import pdfplumber
import re
import json
import sys
from pathlib import Path

# === 設定 ===
PDF_PATH = Path(r"C:\insurance_ai\source_pdfs\必勝考題_保險法規.pdf")
OUTPUT_PATH = Path(r"C:\insurance_ai\output\question_bank_必勝考題_保險法規.json")
SUBJECT = "保險法規"
SOURCE_FILE_LABEL = "必勝考題_保險法規.pdf"


def clean_text(text, fix_chinese_spaces=False):
    """
    清理文字。
    fix_chinese_spaces=True: 移除中文字之間的偽空白 (PDF 內部換行造成)
                              用於題幹、選項文字
    fix_chinese_spaces=False: 只合併連續空白,保留結構性空白
                              用於章節名 (例如「第一章 人身保險契約」)
    """
    if not text:
        return ""
    # 全形空格也算
    text = re.sub(r'[\s\u3000]+', ' ', text).strip()
    if fix_chinese_spaces:
        # 中文字之間的空白通常是 PDF 內部換行造成的偽空白,移除
        # \u4e00-\u9fff 是 CJK 統一漢字基本區
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
        # 多跑一次處理重疊情況(例如 "中 文 字" 三個字之間都有空白)
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text


def parse_question_body(text):
    """
    把題目本文拆成題幹 + 4 個選項。
    從尾巴反向定位 (4)(3)(2)(1),避免題幹內若有 (1) 字眼被誤判。
    找不到 4 個選項時回傳 (清理過的全文, {})
    """
    text_flat = text.replace('\n', ' ').strip()

    option_pattern = re.compile(r'[（\(]([1234１２３４])[）\)]')
    fullwidth_map = {'１': '1', '２': '2', '３': '3', '４': '4'}

    positions = {}
    end_search = len(text_flat)
    for num in ['4', '3', '2', '1']:
        last_pos = None
        for m in option_pattern.finditer(text_flat[:end_search]):
            n = fullwidth_map.get(m.group(1), m.group(1))
            if n == num:
                last_pos = (m.start(), m.end())
        if last_pos is None:
            return clean_text(text_flat, fix_chinese_spaces=True), {}
        positions[num] = last_pos
        end_search = last_pos[0]

    # 題幹
    stem = clean_text(text_flat[:positions['1'][0]], fix_chinese_spaces=True)

    # 4 個選項
    options = {}
    letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    nums_ordered = ['1', '2', '3', '4']
    for i, num in enumerate(nums_ordered):
        opt_start = positions[num][1]
        opt_end = positions[nums_ordered[i + 1]][0] if i + 1 < len(nums_ordered) else len(text_flat)
        opt_text = clean_text(text_flat[opt_start:opt_end], fix_chinese_spaces=True)
        options[letter_map[num]] = opt_text

    return stem, options


def parse_pdf(pdf_path):
    questions = []
    current_unit = None
    skip_log = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    col1, col2, col3 = (row + [None, None, None])[:3]

                    if col1 == '題號':
                        continue

                    # 章節列
                    if col1 and col2 is None and col3 is None:
                        # 章節名保留空白結構
                        current_unit = clean_text(col1, fix_chinese_spaces=False)
                        continue

                    # 題目列
                    if col1 and re.match(r'^\d+-\d+$', col1.strip()):
                        q_num = col1.strip()
                        body = col2 or ''
                        ans_num = (col3 or '').strip()

                        ans_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
                        answer = ans_map.get(ans_num, '?')

                        stem, options = parse_question_body(body)

                        if not options or answer == '?':
                            skip_log.append({
                                'q_num': q_num,
                                'page': page_idx + 1,
                                'reason': 'no_options' if not options else 'bad_answer',
                                'preview': body[:80].replace('\n', ' '),
                            })
                            continue

                        questions.append({
                            'subject': SUBJECT,
                            'unit': current_unit or '未分類',
                            'question_number': q_num,
                            'question': stem,
                            'options': options,
                            'answer': answer,
                            'explanation': '',
                            'difficulty': 'medium',
                            'source_file': SOURCE_FILE_LABEL,
                            'source_page': page_idx + 1,
                        })

    return questions, skip_log


def main():
    pdf_path = PDF_PATH
    output_path = OUTPUT_PATH
    if len(sys.argv) >= 2:
        pdf_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])

    print("=" * 60)
    print(" PDF Parser v2: 必勝考題_保險法規.pdf")
    print("=" * 60)

    if not pdf_path.exists():
        print(f"\n[X] 找不到 PDF: {pdf_path}")
        sys.exit(1)

    print(f"\n[i] 來源: {pdf_path}")
    print(f"[i] 科目: {SUBJECT}")

    questions, skip_log = parse_pdf(pdf_path)

    print(f"\n[OK] 成功解析: {len(questions)} 題")
    print(f"[i]  跳過: {len(skip_log)} 題")

    if skip_log:
        print(f"\n跳過明細:")
        for s in skip_log:
            print(f"  P{s['page']} {s['q_num']} [{s['reason']}]: {s['preview']}")

    print(f"\n各章節題數:")
    unit_counts = {}
    for q in questions:
        unit_counts[q['unit']] = unit_counts.get(q['unit'], 0) + 1
    for unit, cnt in unit_counts.items():
        print(f"  {unit}: {cnt} 題")

    print(f"\n答案分佈:")
    ans_dist = {}
    for q in questions:
        ans_dist[q['answer']] = ans_dist.get(q['answer'], 0) + 1
    for ans in sorted(ans_dist):
        print(f"  {ans}: {ans_dist[ans]} 題")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 已寫入: {output_path}")
    print(f"     檔案大小: {output_path.stat().st_size / 1024:.1f} KB")

    print("\n" + "=" * 60)
    print(" 完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
