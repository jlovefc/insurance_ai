# -*- coding: utf-8 -*-
"""
patch_quiz_show_numbers.py
讓 quiz 頁面顯示 (1)(2)(3)(4) 而非 A./B./C./D.
DB 不動、答題比對邏輯不動,只動顯示。

修改項目:
  1. quiz.js 顯示用 labels 陣列(從亂碼或 A/B 改成 (1)(2)(3)(4))
  2. 「正解是 X」改成「正解是 (X)」對應數字

修改前自動備份。
"""
import os
import re
import shutil
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

QUIZ_JS = r'platform\static\quiz.js'


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{path}.backup_show_numbers_{ts}"
    shutil.copy2(path, bak)
    return bak


def main():
    if not os.path.exists(QUIZ_JS):
        print(f"X 找不到 {QUIZ_JS},請在 C:\\insurance_ai 目錄下執行")
        sys.exit(1)

    with open(QUIZ_JS, 'r', encoding='utf-8') as f:
        text = f.read()

    if '/* PATCHED_SHOW_NUMBERS */' in text:
        print("已 patch 過,跳過")
        return

    changes = []

    # === 修改 1:顯示用的 labels 陣列(showQuestion 函式內的那個) ===
    # 原始程式碼:
    #   const labels = ['嚗?', '嚗?', '嚗?', '嚗?', '嚗?'];   ← 顯示用
    #   const list = document.getElementById('optionsList');
    # 這是亂碼但結構固定,用 regex 抓
    pattern1 = re.compile(
        r"const labels = \[[^\]]+\];\s*\n\s*const list = document\.getElementById\('optionsList'\);"
    )
    replacement1 = (
        "const labels = ['(1)', '(2)', '(3)', '(4)', '(5)']; /* PATCHED_SHOW_NUMBERS */\n"
        "  const list = document.getElementById('optionsList');"
    )

    m1 = pattern1.search(text)
    if not m1:
        print("X 找不到顯示用 labels 陣列,中止")
        sys.exit(1)
    text = pattern1.sub(replacement1, text)
    changes.append("顯示用 labels: ['A',...] → ['(1)',...]")

    # === 修改 2:正解顯示「正解是: X」→ 把 ${correct} 換成數字對應 ===
    # 原:`正解是:${correct}` 之類的(中文亂碼但 ${correct} 一定在)
    # 我們的策略:在 selectAnswer 開頭加一個轉換函式,把 A→(1)、B→(2) 等
    # 直接在程式碼開頭插入 helper,並改用它
    pattern2 = re.compile(
        r"(function selectAnswer\(idx, clickedBtn, question\) \{[\s\S]*?const isCorrect = userAnswer === correct;)"
    )
    replacement2 = (
        r"\1\n"
        "  // PATCHED_SHOW_NUMBERS: 把答案字母轉成數字顯示\n"
        "  const _letterToNumber = {A:'(1)', B:'(2)', C:'(3)', D:'(4)', E:'(5)'};\n"
        "  const correctDisplay = _letterToNumber[correct] || correct;"
    )

    m2 = pattern2.search(text)
    if not m2:
        print("X 找不到 selectAnswer 函式,中止")
        sys.exit(1)
    text = pattern2.sub(replacement2, text)

    # 接著把 ${correct} 在 feedbackCorrect 那行替換成 ${correctDisplay}
    # 那行長這樣:
    #   document.getElementById('feedbackCorrect').textContent = `...${correct}`;
    pattern3 = re.compile(
        r"(document\.getElementById\('feedbackCorrect'\)\.textContent = `[^`]*)\$\{correct\}(`)"
    )
    m3 = pattern3.search(text)
    if not m3:
        print("X 找不到 feedbackCorrect 那行,中止")
        sys.exit(1)
    text = pattern3.sub(r"\1${correctDisplay}\2", text)
    changes.append("正解顯示: 字母 → 數字")

    # === 修改 3:選項按鈕標籤(答錯/答對時被替換成 ✓ ✗ ) ===
    # 原邏輯維持就好,因為 ✓ ✗ 兩個符號跟字母/數字無關
    # 但要注意 button.querySelector('.option-label').textContent = '??';
    # 中文亂碼裡可能是 ✓ ✗,維持原樣

    # 備份 + 寫入
    bak = backup(QUIZ_JS)
    print(f"備份: {bak}")
    with open(QUIZ_JS, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ 已 patch:")
    for c in changes:
        print(f"  - {c}")

    print("\n完成。請:")
    print("  1. 主 app 視窗按 Ctrl+C 停掉")
    print("  2. python app.py 重啟")
    print("  3. 瀏覽器 Ctrl+F5 強制重整")
    print("  4. 進測驗,選項應該顯示 (1)(2)(3)(4)")
    print("\n注意:JS 是瀏覽器執行的,重啟 Flask 不一定能讓新 JS 生效,")
    print("      務必 Ctrl+F5(強制重整,清掉舊 JS cache)。")


if __name__ == "__main__":
    main()
