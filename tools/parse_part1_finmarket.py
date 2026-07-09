# -*- coding: utf-8 -*-
"""
parse_part1_finmarket.py - Part I 金融市場常識 PDF parser
=========================================================
這份 PDF 格式單純:純文字 + 規律題目結構
  (答案) 題號 題幹(1)選項1(2)選項2(3)選項3(4)選項4

策略:
  1. 串接所有頁面文字
  2. 用 regex 切出每一題
  3. 拆 (1)(2)(3)(4) 選項
  4. 輸出 JSON 預覽

用法:
    python tools\\parse_part1_finmarket.py
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


# Q_HEADER 抓「(答案) 題號 」開頭
# 答案: 1-4 一位數
# 題號: 1-3 位數
Q_HEADER_PATTERN = re.compile(r'\((\d)\)\s+(\d{1,3})\s+', re.MULTILINE)


def clean_inline(s):
    """清理段內文字:壓縮空白、修標點"""
    if not s:
        return ''
    # 換行壓成空白
    s = re.sub(r'\s*\n\s*', '', s)
    # 連續空白壓成一個
    s = re.sub(r'\s+', '', s)
    return s.strip()


def parse_question_block(qid, ans_num, body):
    """
    body 例:
        '下列何者不是金融市場的主要功能?(1)提供金融工具交易的場所(2)擔任資金需求者與
         供給者的橋樑(3)促進投資活動的效率,提升經濟發展(4)提供交易者投機的場所'

    回傳 dict 或 None
    """
    body = clean_inline(body)

    # 用 (1)(2)(3)(4) 切開
    # 注意: 題幹中可能有 (1)(2) 等引用,但通常選項是「結尾」的部分,從第一個 (1) 之後
    # 用 split 之後處理
    pattern = re.compile(r'[(（]\s*([1-4])\s*[)）]')
    parts = pattern.split(body)
    # parts = [stem, '1', opt1, '2', opt2, '3', opt3, '4', opt4]

    if len(parts) < 9:
        return None

    stem = parts[0].strip().rstrip('。?').strip()
    if not stem:
        return None

    options = {}
    letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    seen_nums = set()
    for i in range(1, len(parts) - 1, 2):
        num = parts[i]
        opt_text = parts[i + 1].strip()
        if num in seen_nums:
            # 已經抓到該選項,後面 (1)(2) 可能是後續題目開頭,但 Q_HEADER 已經切過
            # 這裡如果重複,代表 body 內有引用 (1)(2),忽略後續
            break
        if num in letter_map and opt_text:
            options[letter_map[num]] = opt_text.strip(' 。、,,')
            seen_nums.add(num)

    if len(options) != 4:
        return None

    # 答案
    if ans_num not in letter_map:
        return None
    answer = letter_map[ans_num]

    return {
        'qid_in_pdf': int(qid),
        'stem': stem,
        'options': options,
        'answer': answer
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="input/PartI-金融市場常識.pdf")
    ap.add_argument("--out", default="output/PartI-金融市場常識.json")
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

    # 1. 串接所有頁面文字
    full_text = ''
    with pdfplumber.open(args.pdf) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ''
            # 去頁碼(每頁底部單獨一行的數字)
            t = re.sub(r'\n\s*\d+\s*$', '\n', t)
            # 去頁首大標題
            t = re.sub(r'^Part I[^\n]*\n', '', t)
            t = re.sub(r'^答案\s+題號\s+題目\s*\n', '', t)
            full_text += '\n' + t

    # 2. 找所有題目位置
    matches = list(Q_HEADER_PATTERN.finditer(full_text))
    print(f"找到題目開頭數量: {len(matches)}")

    # 3. 切題目區塊並解析
    questions = []
    failed = []
    for i, m in enumerate(matches):
        ans_num = m.group(1)
        qid = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[start:end]

        q = parse_question_block(qid, ans_num, body)
        if q:
            questions.append(q)
        else:
            failed.append({
                'qid_in_pdf': int(qid),
                'ans_num': ans_num,
                'body_preview': clean_inline(body)[:200]
            })

    # 4. 寫 JSON
    output = {
        'source': args.pdf,
        'subject': '金融市場常識',  # 整份都標這個科目
        'total': len(questions),
        'failed_count': len(failed),
        'questions': questions,
        'failed': failed
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功: {len(questions)} 題")
    print(f"❌ 失敗: {len(failed)} 題")
    print(f"📄 輸出: {args.out}")

    # 統計題號連續性
    if questions:
        qids = sorted(q['qid_in_pdf'] for q in questions)
        print(f"\n題號範圍: {qids[0]} ~ {qids[-1]}")
        # 找缺號
        expected = set(range(qids[0], qids[-1] + 1))
        actual = set(qids)
        missing = sorted(expected - actual)
        if missing:
            print(f"缺號({len(missing)}個): {missing[:20]}{'...' if len(missing) > 20 else ''}")
        else:
            print("題號完整連續 ✓")

    # 失敗範例
    if failed:
        print(f"\n【失敗範例(前 3 個)】")
        for f in failed[:3]:
            print(f"  #{f['qid_in_pdf']} ans={f['ans_num']}")
            print(f"    {f['body_preview'][:150]}")

    # 預覽
    print(f"\n【預覽前 {args.preview} 題】")
    for i, q in enumerate(questions[:args.preview]):
        print(f"\n── 題 {i+1} (PDF #{q['qid_in_pdf']})")
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")

    # 抽樣後面的
    if len(questions) > 100:
        print(f"\n【抽樣中段 (PDF #{questions[len(questions)//2]['qid_in_pdf']})】")
        q = questions[len(questions) // 2]
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")

    if len(questions) > 5:
        print(f"\n【抽樣末段 (PDF #{questions[-1]['qid_in_pdf']})】")
        q = questions[-1]
        print(f"   題幹: {q['stem']}")
        for letter in ['A', 'B', 'C', 'D']:
            mark = ' ✓' if letter == q['answer'] else ''
            print(f"   ({letter}) {q['options'].get(letter, '?')}{mark}")


if __name__ == "__main__":
    main()
