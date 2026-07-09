# -*- coding: utf-8 -*-
"""
patch_dashboard_show_count.py
自動 patch 兩個檔案,讓 dashboard 選單顯示題數:
  - platform/app.py
  - platform/templates/dashboard.html

特點:
  - 修改前自動備份
  - 找不到目標字串會中止,不會破壞檔案
  - 可逆 (備份檔放在同目錄)

用法:
    cd C:\\insurance_ai
    python tools\\patch_dashboard_show_count.py
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
DASH_HTML = r'platform\templates\dashboard.html'


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{path}.backup_count_{ts}"
    shutil.copy2(path, bak)
    return bak


def patch_app_py():
    """在 app.py 加一段 subject_count 查詢,並傳給 template"""
    print(f"\n== Patch {APP_PY} ==")

    with open(APP_PY, 'r', encoding='utf-8') as f:
        text = f.read()

    # 標記:已 patch 過就跳過
    if 'subject_count' in text:
        print("  已 patch 過,跳過")
        return False

    # 1. 在 subject_units 查詢後加 subject_count
    anchor1 = ('subject_units = (db.session.query(Question.subject, Question.unit)\n'
               '                     .distinct().all())')
    addition1 = ('subject_units = (db.session.query(Question.subject, Question.unit)\n'
                 '                     .distinct().all())\n'
                 '    # 各科題數統計\n'
                 '    from sqlalchemy import func\n'
                 '    _counts = (db.session.query(Question.subject, func.count(Question.id))\n'
                 '               .group_by(Question.subject).all())\n'
                 '    subject_count = {s: n for s, n in _counts if s}')

    if anchor1 not in text:
        print(f"  X 找不到 anchor: subject_units 查詢")
        return False
    text = text.replace(anchor1, addition1)

    # 2. 在 render_template 加 subject_count=subject_count
    anchor2 = 'subject_unit_map=subject_unit_map,'
    addition2 = ('subject_unit_map=subject_unit_map,\n'
                 '                           subject_count=subject_count,')
    if anchor2 not in text:
        print(f"  X 找不到 anchor: subject_unit_map 傳值")
        return False
    text = text.replace(anchor2, addition2)

    # 備份 + 寫入
    bak = backup(APP_PY)
    print(f"  備份: {bak}")
    with open(APP_PY, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  ✅ 已 patch")
    return True


def patch_dashboard_html():
    """改 <option> 顯示題數"""
    print(f"\n== Patch {DASH_HTML} ==")

    with open(DASH_HTML, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'subject_count' in text:
        print("  已 patch 過,跳過")
        return False

    anchor = '<option value="{{ subj }}">{{ subj }}</option>'
    replacement = ('<option value="{{ subj }}">'
                   '{{ subj }} ({{ subject_count.get(subj, 0) }} 題)'
                   '</option>')

    if anchor not in text:
        print(f"  X 找不到 anchor: <option> 標籤")
        return False
    text = text.replace(anchor, replacement)

    bak = backup(DASH_HTML)
    print(f"  備份: {bak}")
    with open(DASH_HTML, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  ✅ 已 patch")
    return True


def main():
    if not os.path.exists(APP_PY):
        print(f"X 找不到 {APP_PY},請在 C:\\insurance_ai 目錄下執行")
        sys.exit(1)
    if not os.path.exists(DASH_HTML):
        print(f"X 找不到 {DASH_HTML}")
        sys.exit(1)

    patch_app_py()
    patch_dashboard_html()

    print("\n完成。請:")
    print("  1. 停掉主 app(視窗 Ctrl+C)")
    print("  2. 重新 python app.py")
    print("  3. 瀏覽器 Ctrl+F5")
    print("  4. dashboard 選單應該變成 '金融市場常識 (504 題)' 格式")
    print("\n出問題的話:備份檔在原檔案旁邊,改回去就好。")


if __name__ == "__main__":
    main()
