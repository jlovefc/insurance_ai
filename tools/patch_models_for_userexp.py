# -*- coding: utf-8 -*-
"""
patch_models_for_userexp.py
========================================
為 user_explanations 功能更新 models.py:
  1. User 加 is_admin 欄位
  2. 新增 UserExplanation 類別

可逆,修改前自動備份。
"""
import os
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

    # === Patch 1: User 加 is_admin ===
    anchor1 = "    created_at = db.Column(db.DateTime, default=datetime.utcnow)\n    sessions = db.relationship('QuizSession'"
    addition1 = ("    is_admin = db.Column(db.Integer, default=0)  # 管理員旗標\n"
                 "    created_at = db.Column(db.DateTime, default=datetime.utcnow)\n"
                 "    sessions = db.relationship('QuizSession'")

    if anchor1 not in text:
        print("X 找不到 User 類別 anchor")
        sys.exit(1)
    text = text.replace(anchor1, addition1)

    # === Patch 2: 在檔尾加 UserExplanation 類別 ===
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

    text = text.rstrip() + addition2

    # 備份
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{MODELS_PY}.backup_userexp_{ts}"
    shutil.copy2(MODELS_PY, bak)
    print(f"備份: {bak}")

    with open(MODELS_PY, 'w', encoding='utf-8') as f:
        f.write(text)
    print("✅ models.py 已 patch")
    print("  - User 加 is_admin 欄位")
    print("  - 新增 UserExplanation 類別")


if __name__ == "__main__":
    main()
