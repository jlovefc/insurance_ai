# -*- coding: utf-8 -*-
"""
patch_quiz_userexp.py
======================
為 quiz 頁面加入「使用者解說」UI:
  - 答題後在「官方解析」下方顯示所有使用者解說
  - 「+ 寫下我的解說」按鈕展開輸入框
  - 自己的留言有 [編輯][刪除]
  - 別人的留言有 [回報錯誤](管理員例外,管理員看每則都有編輯/刪除)
  - 編輯解說即時生效

修改:
  1. static/quiz.js - 加 helper / 載入解說 / 渲染 / 編輯互動
  2. static/style.css - 加新樣式

自動備份,可逆。
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
STYLE_CSS = r'platform\static\style.css'


# ============================================================
# 要插入 quiz.js 的程式碼
# ============================================================

# (A) 在 state 物件加 currentUser
STATE_FIELD_ANCHOR = "  wrongCount: 0\n};"
STATE_FIELD_REPLACE = """  wrongCount: 0,
  currentUser: null,  /* user_explanations 用:{id, username, is_admin} */
};"""

# (B) loadQuiz 函式取得 user 資訊
LOAD_USER_ANCHOR = "    state.sessionId = data.session_id;"
LOAD_USER_REPLACE = """    state.sessionId = data.session_id;
    state.currentUser = data.user || null;  /* user_explanations 需要 */"""

# (C) selectAnswer 答對/答錯後載入並渲染解說
# 找這段(quiz_actions 顯示前)
LOAD_EXP_ANCHOR = "  show('quizActions');\n}"
LOAD_EXP_REPLACE = """  show('quizActions');
  /* user_explanations: 載入並渲染 */
  loadExplanations(question.id);
}


/* ============================================================
   user_explanations 顯示與互動
   ============================================================ */

function loadExplanations(qid) {
  fetch('/api/explanations/' + qid)
    .then(function(r) { return r.json(); })
    .then(function(data) {
      renderExplanations(qid, data.explanations || []);
    })
    .catch(function(err) {
      console.warn('載入解說失敗', err);
      renderExplanations(qid, []);
    });
}

function renderExplanations(qid, explanations) {
  var container = document.getElementById('userExpArea');
  if (!container) return;
  container.innerHTML = '';

  /* 標題 */
  var head = document.createElement('div');
  head.className = 'userexp-head';
  head.innerHTML = '<span class="userexp-icon">💬</span>使用者解說 (' + explanations.length + ')';
  container.appendChild(head);

  /* 留言列表 */
  if (explanations.length > 0) {
    var listDiv = document.createElement('div');
    listDiv.className = 'userexp-list';
    explanations.forEach(function(exp) {
      listDiv.appendChild(buildExpItem(exp));
    });
    container.appendChild(listDiv);
  }

  /* + 寫解說 按鈕 + 表單 */
  var formWrap = document.createElement('div');
  formWrap.className = 'userexp-form-wrap';
  formWrap.innerHTML =
    '<button class="userexp-add-btn" onclick="toggleExpForm(' + qid + ', this)">' +
    '+ 寫下我的解說</button>' +
    '<div class="userexp-form hidden" id="userexpForm_' + qid + '">' +
    '<textarea class="userexp-textarea" id="userexpInput_' + qid +
    '" placeholder="寫下你的理解、記憶口訣、或補充說明…" maxlength="2000"></textarea>' +
    '<div class="userexp-form-actions">' +
    '<button class="userexp-cancel" onclick="cancelExpForm(' + qid + ')">取消</button>' +
    '<button class="userexp-submit" onclick="submitExp(' + qid + ')">送出</button>' +
    '</div></div>';
  container.appendChild(formWrap);
}

function buildExpItem(exp) {
  var div = document.createElement('div');
  div.className = 'userexp-item';
  div.dataset.expId = exp.id;

  var canEdit = exp.can_edit;
  var meta = '<div class="userexp-meta">' +
    '<span class="userexp-user">' + escapeHtml(exp.username) + '</span>' +
    '<span class="userexp-time">' + (exp.updated_at || exp.created_at) + '</span>' +
    '</div>';

  var content = '<div class="userexp-content">' + escapeHtml(exp.content).replace(/\\n/g, '<br>') + '</div>';

  var actions = '<div class="userexp-actions">';
  if (canEdit) {
    actions += '<button class="userexp-btn-edit" onclick="startEditExp(' + exp.id + ')">編輯</button>';
    actions += '<button class="userexp-btn-del" onclick="deleteExp(' + exp.id + ')">刪除</button>';
  } else {
    actions += '<button class="userexp-btn-report" onclick="reportExp(' + exp.id + ')">回報錯誤</button>';
  }
  if (exp.report_count > 0) {
    actions += '<span class="userexp-report-badge">⚠ ' + exp.report_count + '</span>';
  }
  actions += '</div>';

  div.innerHTML = meta + content + actions;
  return div;
}

function toggleExpForm(qid, btn) {
  var form = document.getElementById('userexpForm_' + qid);
  if (!form) return;
  if (form.classList.contains('hidden')) {
    form.classList.remove('hidden');
    btn.textContent = '收起輸入框';
    var ta = document.getElementById('userexpInput_' + qid);
    if (ta) ta.focus();
  } else {
    form.classList.add('hidden');
    btn.textContent = '+ 寫下我的解說';
  }
}

function cancelExpForm(qid) {
  var form = document.getElementById('userexpForm_' + qid);
  var btn = form && form.parentNode.querySelector('.userexp-add-btn');
  var ta = document.getElementById('userexpInput_' + qid);
  if (ta) ta.value = '';
  if (form) form.classList.add('hidden');
  if (btn) btn.textContent = '+ 寫下我的解說';
}

function submitExp(qid) {
  var ta = document.getElementById('userexpInput_' + qid);
  var content = (ta && ta.value || '').trim();
  if (!content) { alert('請先輸入內容'); return; }
  fetch('/api/explanations', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question_id: qid, content: content})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { alert(data.error); return; }
    if (ta) ta.value = '';
    loadExplanations(qid);
  })
  .catch(function(err) { alert('送出失敗: ' + err.message); });
}

function startEditExp(expId) {
  var item = document.querySelector('.userexp-item[data-exp-id="' + expId + '"]');
  if (!item) return;
  var contentDiv = item.querySelector('.userexp-content');
  var actionsDiv = item.querySelector('.userexp-actions');
  var oldText = contentDiv.innerText;

  contentDiv.innerHTML = '<textarea class="userexp-textarea userexp-edit-ta">' +
    escapeHtml(oldText) + '</textarea>';
  actionsDiv.innerHTML =
    '<button class="userexp-submit" onclick="saveEditExp(' + expId + ')">儲存</button>' +
    '<button class="userexp-cancel" onclick="loadExplanations(' + state.questions[state.currentIdx].id + ')">取消</button>';
  var ta = contentDiv.querySelector('textarea');
  if (ta) { ta.focus(); ta.value = oldText; }
}

function saveEditExp(expId) {
  var item = document.querySelector('.userexp-item[data-exp-id="' + expId + '"]');
  if (!item) return;
  var ta = item.querySelector('textarea');
  var newContent = (ta && ta.value || '').trim();
  if (!newContent) { alert('內容不能為空'); return; }

  fetch('/api/explanations/' + expId, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({content: newContent})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { alert(data.error); return; }
    loadExplanations(state.questions[state.currentIdx].id);
  })
  .catch(function(err) { alert('儲存失敗: ' + err.message); });
}

function deleteExp(expId) {
  if (!confirm('確定刪除這則解說?')) return;
  fetch('/api/explanations/' + expId, {method: 'DELETE'})
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { alert(data.error); return; }
    loadExplanations(state.questions[state.currentIdx].id);
  });
}

function reportExp(expId) {
  if (!confirm('回報這則解說有錯?管理員會處理。')) return;
  fetch('/api/explanations/' + expId + '/report', {method: 'POST'})
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { alert(data.error); return; }
    loadExplanations(state.questions[state.currentIdx].id);
  });
}

function escapeHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}"""

# (D) showQuestion 把 userExpArea 容器清空
CLEAR_EXP_ANCHOR = "  document.getElementById('feedbackExplain').classList.add('hidden');"
CLEAR_EXP_REPLACE = """  document.getElementById('feedbackExplain').classList.add('hidden');
  var _userExp = document.getElementById('userExpArea');
  if (_userExp) _userExp.innerHTML = '';"""


# ============================================================
# 要塞進 quiz.html 的容器
# ============================================================
HTML_FILE = r'platform\templates\quiz.html'
HTML_ANCHOR = '<div class="quiz-actions hidden" id="quizActions">'
HTML_INSERT = ('    <div class="userexp-area" id="userExpArea"></div>\n'
               '    <div class="quiz-actions hidden" id="quizActions">')


# ============================================================
# CSS
# ============================================================
CSS_BLOCK = """

/* ============================================================
   user_explanations 樣式
   ============================================================ */
.userexp-area {
  margin: 20px 0;
  padding: 16px;
  background: rgba(212, 175, 55, 0.04);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 10px;
}
.userexp-head {
  font-size: 14px;
  color: #d4af37;
  margin-bottom: 12px;
  font-weight: 500;
}
.userexp-icon { margin-right: 6px; }
.userexp-list { margin-bottom: 12px; }
.userexp-item {
  background: rgba(0,0,0,0.2);
  border-left: 3px solid #d4af37;
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 6px;
}
.userexp-meta {
  font-size: 11px;
  color: #888;
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
}
.userexp-user { color: #d4af37; font-weight: 500; }
.userexp-content {
  font-size: 14px;
  color: #e4e4e4;
  line-height: 1.6;
  white-space: pre-wrap;
}
.userexp-actions {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  align-items: center;
}
.userexp-btn-edit, .userexp-btn-del, .userexp-btn-report,
.userexp-submit, .userexp-cancel {
  background: transparent;
  color: #888;
  border: 1px solid #444;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  font-family: inherit;
}
.userexp-btn-edit:hover, .userexp-submit:hover { color: #d4af37; border-color: #d4af37; }
.userexp-btn-del:hover, .userexp-btn-report:hover { color: #ff8888; border-color: #ff8888; }
.userexp-cancel:hover { color: #ccc; border-color: #666; }
.userexp-report-badge {
  font-size: 10px;
  color: #ff8888;
  margin-left: auto;
}
.userexp-add-btn {
  background: transparent;
  color: #d4af37;
  border: 1px dashed #d4af37;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
  width: 100%;
}
.userexp-add-btn:hover { background: rgba(212, 175, 55, 0.08); }
.userexp-form { margin-top: 10px; }
.userexp-textarea {
  width: 100%;
  min-height: 80px;
  background: rgba(0,0,0,0.3);
  color: #e4e4e4;
  border: 1px solid #555;
  border-radius: 6px;
  padding: 10px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
}
.userexp-textarea:focus { outline: none; border-color: #d4af37; }
.userexp-form-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.userexp-edit-ta { min-height: 60px; }
/* user_explanations 樣式 結束 */
"""


def backup(path, suffix):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{path}.backup_{suffix}_{ts}"
    shutil.copy2(path, bak)
    return bak


def patch_quiz_js():
    if not os.path.exists(QUIZ_JS):
        print(f"X 找不到 {QUIZ_JS}")
        return False
    with open(QUIZ_JS, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'loadExplanations' in text:
        print("  quiz.js 已 patch,跳過")
        return False

    # 找四個 anchor
    if STATE_FIELD_ANCHOR not in text:
        print("X quiz.js anchor 1 (state field) 找不到")
        return False
    if LOAD_USER_ANCHOR not in text:
        print("X quiz.js anchor 2 (load user) 找不到")
        return False
    if LOAD_EXP_ANCHOR not in text:
        print("X quiz.js anchor 3 (load exp) 找不到")
        return False
    if CLEAR_EXP_ANCHOR not in text:
        print("X quiz.js anchor 4 (clear exp) 找不到")
        return False

    text = text.replace(STATE_FIELD_ANCHOR, STATE_FIELD_REPLACE, 1)
    text = text.replace(LOAD_USER_ANCHOR, LOAD_USER_REPLACE, 1)
    text = text.replace(LOAD_EXP_ANCHOR, LOAD_EXP_REPLACE, 1)
    text = text.replace(CLEAR_EXP_ANCHOR, CLEAR_EXP_REPLACE, 1)

    bak = backup(QUIZ_JS, 'userexp')
    print(f"  備份: {bak}")
    with open(QUIZ_JS, 'w', encoding='utf-8') as f:
        f.write(text)
    print("  ✅ quiz.js 已 patch")
    return True


def patch_quiz_html():
    if not os.path.exists(HTML_FILE):
        print(f"X 找不到 {HTML_FILE}")
        return False
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'userExpArea' in text:
        print("  quiz.html 已 patch,跳過")
        return False
    if HTML_ANCHOR not in text:
        print("X quiz.html anchor 找不到")
        return False

    text = text.replace(HTML_ANCHOR, HTML_INSERT, 1)
    bak = backup(HTML_FILE, 'userexp')
    print(f"  備份: {bak}")
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(text)
    print("  ✅ quiz.html 已 patch")
    return True


def patch_style_css():
    if not os.path.exists(STYLE_CSS):
        print(f"X 找不到 {STYLE_CSS}")
        return False
    with open(STYLE_CSS, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'userexp-area' in text:
        print("  style.css 已 patch,跳過")
        return False

    bak = backup(STYLE_CSS, 'userexp')
    print(f"  備份: {bak}")
    with open(STYLE_CSS, 'a', encoding='utf-8') as f:
        f.write(CSS_BLOCK)
    print("  ✅ style.css 已 patch")
    return True


def main():
    print("== Patch quiz.js ==")
    patch_quiz_js()
    print("\n== Patch quiz.html ==")
    patch_quiz_html()
    print("\n== Patch style.css ==")
    patch_style_css()
    print("\n完成。請:")
    print("  1. 主 app 視窗按 Ctrl+C")
    print("  2. python app.py 重啟")
    print("  3. 瀏覽器 Ctrl+F5 強制重整")
    print("  4. 進測驗答完一題,應該看到「使用者解說」區塊")


if __name__ == "__main__":
    main()
