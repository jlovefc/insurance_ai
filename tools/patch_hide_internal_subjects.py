# -*- coding: utf-8 -*-
"""
patch_hide_internal_subjects.py
讓 dashboard 的科目選單不顯示「已刪除」、「未分類」這類內部狀態 subject。

作法:在 app.py 的 dashboard view 過濾 subject_units 和 subject_count。

修改前自動備份。可逆。
"""
import os
import shutil
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

APP_PY = r'platform\app.py'


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{path}.backup_hide_{ts}"
    shutil.copy2(path, bak)
    return bak


def main():
    if not os.path.exists(APP_PY):
        print(f"X 找不到 {APP_PY},請在 C:\\insurance_ai 目錄下執行")
        sys.exit(1)

    with open(APP_PY, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'HIDDEN_SUBJECTS' in text:
        print("已 patch 過,跳過")
        return

    # 在 subject_units 查詢前面加排除清單
    anchor = ('subject_units = (db.session.query(Question.subject, Question.unit)\n'
              '                     .distinct().all())')

    addition = (
        '# 內部狀態 subject,不出現在使用者選單\n'
        "    HIDDEN_SUBJECTS = {'已刪除', '未分類'}\n"
        '    subject_units = (db.session.query(Question.subject, Question.unit)\n'
        '                     .filter(~Question.subject.in_(HIDDEN_SUBJECTS))\n'
        '                     .distinct().all())'
    )

    if anchor not in text:
        print(f"X 找不到 anchor: subject_units 查詢")
        print(f"  app.py 結構可能已改變,中止避免破壞")
        sys.exit(1)

    text = text.replace(anchor, addition)

    # subject_count 也要過濾
    anchor2 = ('_counts = (db.session.query(Question.subject, func.count(Question.id))\n'
               '               .group_by(Question.subject).all())\n'
               '    subject_count = {s: n for s, n in _counts if s}')

    addition2 = ('_counts = (db.session.query(Question.subject, func.count(Question.id))\n'
                 '               .group_by(Question.subject).all())\n'
                 '    subject_count = {s: n for s, n in _counts\n'
                 '                     if s and s not in HIDDEN_SUBJECTS}')

    if anchor2 not in text:
        print(f"X 找不到 anchor: subject_count")
        sys.exit(1)

    text = text.replace(anchor2, addition2)

    bak = backup(APP_PY)
    print(f"備份: {bak}")
    with open(APP_PY, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"✅ 已 patch")

    print("\n完成。請:")
    print("  1. 主 app 視窗按 Ctrl+C")
    print("  2. python app.py 重啟")
    print("  3. 瀏覽器 Ctrl+F5")
    print("  4. dashboard 選單應該只剩 4 個正式科目")


if __name__ == "__main__":
    main()
