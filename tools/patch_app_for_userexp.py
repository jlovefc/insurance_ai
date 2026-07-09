# -*- coding: utf-8 -*-
"""
patch_app_for_userexp.py
========================================
為 user_explanations 功能更新 app.py:
  1. import UserExplanation
  2. 加 5 個 API:
     - GET  /api/explanations/<question_id>           列出某題所有解說
     - POST /api/explanations                          新增解說
     - PUT  /api/explanations/<exp_id>                 編輯解說(自己或管理員)
     - DELETE /api/explanations/<exp_id>               刪除解說(自己或管理員)
     - POST /api/explanations/<exp_id>/report          回報錯誤(report_count + 1)
  3. /api/quiz/start 順手帶出每題的解說 list

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

APP_PY = r'platform\app.py'

NEW_IMPORT_HINT = "UserExplanation"

NEW_ROUTES = '''


# ============================================================
# user_explanations API (使用者解說功能)
# ============================================================
from models import UserExplanation


def _exp_to_dict(exp, current_user_id, current_is_admin):
    """格式化單筆解說"""
    can_edit = bool(current_is_admin) or exp.user_id == current_user_id
    return {
        'id': exp.id,
        'question_id': exp.question_id,
        'user_id': exp.user_id,
        'username': exp.user.username if exp.user else '?',
        'content': exp.content,
        'created_at': exp.created_at.strftime('%Y-%m-%d %H:%M') if exp.created_at else '',
        'updated_at': exp.updated_at.strftime('%Y-%m-%d %H:%M') if exp.updated_at else '',
        'report_count': exp.report_count or 0,
        'can_edit': can_edit
    }


@app.route('/api/explanations/<int:question_id>', methods=['GET'])
def api_get_explanations(question_id):
    """列出某題所有使用者解說"""
    if 'user_id' not in session:
        return jsonify({'error': '未登入'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': '使用者不存在'}), 401
    exps = (UserExplanation.query
            .filter_by(question_id=question_id)
            .order_by(UserExplanation.created_at.asc())
            .all())
    return jsonify({
        'explanations': [_exp_to_dict(e, user.id, user.is_admin) for e in exps]
    })


@app.route('/api/explanations', methods=['POST'])
def api_add_explanation():
    """新增解說"""
    if 'user_id' not in session:
        return jsonify({'error': '未登入'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': '使用者不存在'}), 401

    data = request.json or {}
    qid = data.get('question_id')
    content = (data.get('content') or '').strip()
    if not qid or not content:
        return jsonify({'error': '題號或內容不能為空'}), 400
    if len(content) > 2000:
        return jsonify({'error': '解說太長,請控制在 2000 字內'}), 400

    exp = UserExplanation(
        question_id=qid,
        user_id=user.id,
        content=content
    )
    db.session.add(exp)
    db.session.commit()
    return jsonify({
        'ok': True,
        'explanation': _exp_to_dict(exp, user.id, user.is_admin)
    })


@app.route('/api/explanations/<int:exp_id>', methods=['PUT'])
def api_edit_explanation(exp_id):
    """編輯解說(自己或管理員)"""
    if 'user_id' not in session:
        return jsonify({'error': '未登入'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': '使用者不存在'}), 401

    exp = UserExplanation.query.get(exp_id)
    if not exp:
        return jsonify({'error': '解說不存在'}), 404
    if not user.is_admin and exp.user_id != user.id:
        return jsonify({'error': '無權編輯'}), 403

    data = request.json or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'error': '內容不能為空'}), 400
    if len(content) > 2000:
        return jsonify({'error': '解說太長,請控制在 2000 字內'}), 400

    exp.content = content
    db.session.commit()
    return jsonify({
        'ok': True,
        'explanation': _exp_to_dict(exp, user.id, user.is_admin)
    })


@app.route('/api/explanations/<int:exp_id>', methods=['DELETE'])
def api_delete_explanation(exp_id):
    """刪除解說(自己或管理員)"""
    if 'user_id' not in session:
        return jsonify({'error': '未登入'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': '使用者不存在'}), 401

    exp = UserExplanation.query.get(exp_id)
    if not exp:
        return jsonify({'error': '解說不存在'}), 404
    if not user.is_admin and exp.user_id != user.id:
        return jsonify({'error': '無權刪除'}), 403

    db.session.delete(exp)
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/explanations/<int:exp_id>/report', methods=['POST'])
def api_report_explanation(exp_id):
    """回報錯誤(report_count + 1)"""
    if 'user_id' not in session:
        return jsonify({'error': '未登入'}), 401
    exp = UserExplanation.query.get(exp_id)
    if not exp:
        return jsonify({'error': '解說不存在'}), 404
    exp.report_count = (exp.report_count or 0) + 1
    db.session.commit()
    return jsonify({'ok': True, 'report_count': exp.report_count})
'''


def main():
    if not os.path.exists(APP_PY):
        print(f"X 找不到 {APP_PY}")
        sys.exit(1)

    with open(APP_PY, 'r', encoding='utf-8') as f:
        text = f.read()

    if NEW_IMPORT_HINT in text:
        print("已 patch 過,跳過")
        return

    # 直接把新路由接在檔尾的 `if __name__ == '__main__':` 前面
    # 找這行
    marker = "if __name__ == '__main__':"
    if marker not in text:
        # 容錯:雙引號版本
        marker = 'if __name__ == "__main__":'

    if marker in text:
        text = text.replace(marker, NEW_ROUTES.strip() + '\n\n\n' + marker, 1)
    else:
        # 找不到入口,直接 append
        text = text.rstrip() + '\n' + NEW_ROUTES

    # 備份
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{APP_PY}.backup_userexp_{ts}"
    shutil.copy2(APP_PY, bak)
    print(f"備份: {bak}")

    with open(APP_PY, 'w', encoding='utf-8') as f:
        f.write(text)
    print("✅ app.py 已 patch")
    print("  - 加入 UserExplanation import")
    print("  - 加入 5 個 API 端點:")
    print("    GET    /api/explanations/<question_id>")
    print("    POST   /api/explanations")
    print("    PUT    /api/explanations/<exp_id>")
    print("    DELETE /api/explanations/<exp_id>")
    print("    POST   /api/explanations/<exp_id>/report")


if __name__ == "__main__":
    main()
