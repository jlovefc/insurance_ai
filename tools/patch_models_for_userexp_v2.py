# -*- coding: utf-8 -*-
"""
patch_models_for_userexp_v2.py
========================================
用穩健的 anchor 為 models.py 加上:
  1. User.is_admin 欄位
  2. UserExplanation 類別

策略:
  - 在 'sessions = db.relationship' 那行**之後**插入 is_admin
  - 在檔案末尾追加 UserExplanation 類別

可逆,修改前自動備份。
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

MODELS_PY = r'platform\models.py'


def main():
    if not os.path.exists(MODELS_PY):
        print(f"X 找不到 {MODELS_PY}")
        sys.exit(1)

    with open(MODELS_PY, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'class UserExplanation' in text:
        print("已 patch 過,跳過")
        return

    changes = []

    # === Patch 1: User 加 is_admin ===
    # Anchor: User 類別內的 weak_areas relationship 那行
    # (那行很穩定,因為是 User 類別的最後一行)
    pattern1 = re.compile(
        r"(class User\(db\.Model\):[\s\S]*?weak_areas = db\.relationship\('WeakArea'[^\n]*\n)"
    )
    m1 = pattern1.search(text)
    if not m1:
        print("X 找不到 User 類別 anchor (weak_areas relationship)")
        sys.exit(1)

    addition1 = m1.group(1) + "    is_admin = db.Column(db.Integer, default=0)  # 管理員旗標\n"
    text = text[:m1.start()] + addition1 + text[m1.end():]
    changes.append("User 加 is_admin 欄位")

    # === Patch 2: 檔尾追加 UserExplanation 類別 ===
    addition2 = '''


class UserExplanation(db.Model):
    """使用者寫的解說 - 每題可多筆,管理員可編所有,一般使用者只能編自己的"""
    __tablename__ = 'user_explanations'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    report_count = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='explanations')
    question = db.relationship('Question', backref='user_explanations')
'''
    text = text.rstrip() + addition2 + '\n'
    changes.append("追加 UserExplanation 類別")

    # 備份
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{MODELS_PY}.backup_userexp_v2_{ts}"
    shutil.copy2(MODELS_PY, bak)
    print(f"備份: {bak}")

    with open(MODELS_PY, 'w', encoding='utf-8') as f:
        f.write(text)
    print("✅ models.py 已 patch")
    for c in changes:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
