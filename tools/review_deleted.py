# -*- coding: utf-8 -*-
"""
review_deleted.py - 回顧已刪除題目
===================================
針對 subject='已刪除' 的題目逐一檢視,挑出誤刪的還原。

啟動 (PowerShell):
    cd C:\\insurance_ai
    .\\venv\\Scripts\\activate
    python tools\\review_deleted.py

瀏覽器: http://localhost:5003

操作:
  空白 / ← / K       = 救回(改回未分類)
  D / → / J          = 確認刪除(維持已刪除)
  B                  = 撤銷上一題
"""
import argparse
import os
import shutil
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

DEFAULT_DB = "platform/instance/insurance_exam.db"

app = Flask(__name__)
DB_PATH = None
SESSION_HISTORY = []
SESSION_CONFIRMED_DELETE = set()  # 已確認刪除的 id,避免再次出現


def get_conn():
    return sqlite3.connect(DB_PATH)


HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>回顧已刪除</title>
<style>
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
body {
    background: #1a1a1a; color: #d4af37;
    font-family: "Noto Serif TC", "PingFang TC", serif;
    margin: 0; padding: 16px; max-width: 640px; margin: 0 auto;
    min-height: 100vh;
}
.progress { background: #2a2a2a; height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 6px; }
.bar { background: linear-gradient(90deg, #d4af37, #f1d57a); height: 100%; transition: width 0.4s; }
.stats { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 14px; }
.qid { color: #d4af37; opacity: 0.5; font-size: 11px; margin-bottom: 6px; letter-spacing: 1px; }
.question {
    background: #232323; border: 1px solid #3a3a3a;
    padding: 18px; border-radius: 10px;
    line-height: 1.85; margin-bottom: 12px;
    font-size: 16px; color: #e4e4e4; min-height: 100px;
}
.guide {
    background: #2a1f18; border-left: 3px solid #a07a3a;
    padding: 8px 12px; margin-bottom: 16px;
    font-size: 12px; color: #c8a878;
    border-radius: 4px;
}
.buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.btn {
    border: none; padding: 24px 12px;
    border-radius: 10px; font-size: 17px;
    cursor: pointer; font-family: inherit;
    transition: all 0.15s; user-select: none;
    font-weight: 600;
}
.btn:active { transform: scale(0.97); }
.btn-restore {
    background: linear-gradient(135deg, #d4af37, #b8941f);
    color: #1a1a1a;
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.25);
}
.btn-confirm {
    background: #3a2020; color: #ff8888;
    border: 1px solid #5a3030;
}
.btn .sub { display: block; font-size: 11px; opacity: 0.7; margin-top: 4px; font-weight: 400; }
.aux { display: grid; grid-template-columns: 1fr; gap: 8px; }
.btn-aux {
    background: transparent; color: #888;
    border: 1px solid #444; padding: 12px;
    border-radius: 8px; font-size: 13px;
    cursor: pointer; font-family: inherit;
}
.toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #2a2a2a; color: #d4af37;
    padding: 10px 18px; border-radius: 20px;
    border: 1px solid #d4af37; font-size: 13px;
    opacity: 0; transition: opacity 0.3s; pointer-events: none;
}
.toast.show { opacity: 1; }
.toast.del { color: #ff8888; border-color: #ff8888; }
#errbox {
    background: #4a1a1a; color: #ffaaaa;
    padding: 12px; border-radius: 8px; margin-bottom: 16px;
    font-family: monospace; font-size: 12px;
    display: none; white-space: pre-wrap;
}
</style>
</head>
<body>

<div id="errbox"></div>
<div id="app">
    <div class="progress"><div class="bar" id="bar" style="width:0%"></div></div>
    <div class="stats">
        <span>已回顧 <span id="done">0</span> / <span id="total">0</span></span>
        <span>救回 <span id="restored">0</span>  ·  確認刪除 <span id="confirmed">0</span></span>
    </div>
    <div class="qid">題號 <span id="qid">-</span></div>
    <div class="question" id="content">載入中…</div>

    <div class="guide">
        判斷標準:題目本體在問<b>保險知識</b>(風險管理、保險商品、保費結構…) → <b>救回</b><br>
        題目本體在問<b>教材/考試本身</b>(學習方法、入場證、章節頁碼…) → <b>確認刪除</b>
    </div>

    <div class="buttons">
        <button class="btn btn-restore" id="btn-restore">
            救回<span class="sub">這是真考題  /  空白 ← K</span>
        </button>
        <button class="btn btn-confirm" id="btn-confirm">
            確認刪除<span class="sub">真的是垃圾  /  D → J</span>
        </button>
    </div>

    <div class="aux">
        <button class="btn-aux" id="btn-undo">撤銷上一題 (B)</button>
    </div>
</div>
<div class="toast" id="toast"></div>

<script>
console.log('[review-del] script start');

var currentQ = null;

function showError(msg) {
    var box = document.getElementById('errbox');
    box.style.display = 'block';
    box.textContent = String(msg);
    console.error('[review-del]', msg);
}

window.addEventListener('error', function(e) {
    showError('JS Error: ' + e.message);
});

function showToast(msg, isDel) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    if (isDel) t.classList.add('del');
    else t.classList.remove('del');
    setTimeout(function() { t.classList.remove('show'); }, 1100);
}

function load() {
    fetch('/api/next')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            console.log('[review-del] data:', data);
            if (data.done) {
                document.getElementById('app').innerHTML =
                    '<div style="text-align:center;padding:60px 20px">' +
                    '<h2 style="color:#d4af37">回顧完成</h2>' +
                    '<p style="color:#888;margin:20px 0">' +
                    '救回 ' + data.restored + ' 題 · 確認刪除 ' + data.confirmed + ' 題</p>' +
                    '<p style="color:#666;font-size:13px;margin-top:24px">' +
                    '可以關掉視窗了。</p></div>';
                return;
            }
            currentQ = data;
            document.getElementById('content').textContent = data.content;
            document.getElementById('qid').textContent = '#' + data.id;
            document.getElementById('done').textContent = data.done_count;
            document.getElementById('total').textContent = data.total;
            document.getElementById('restored').textContent = data.restored;
            document.getElementById('confirmed').textContent = data.confirmed;
            document.getElementById('bar').style.width = (data.done_count * 100 / data.total) + '%';
        })
        .catch(function(err) { showError('load failed: ' + err.message); });
}

function decide(action) {
    if (!currentQ) return;
    fetch('/api/decide', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: currentQ.id, action: action})
    })
    .then(function(r) { return r.json(); })
    .then(function() {
        showToast(action === 'restore' ? '✓ 救回' : '✗ 確認刪除', action === 'confirm');
        load();
    })
    .catch(function(err) { showError('decide failed: ' + err.message); });
}

function undoQ() {
    fetch('/api/undo', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) { showToast('↶ 已撤銷 #' + data.id); load(); }
            else { showToast('沒有可撤銷的'); }
        });
}

document.getElementById('btn-restore').addEventListener('click', function() { decide('restore'); });
document.getElementById('btn-confirm').addEventListener('click', function() { decide('confirm'); });
document.getElementById('btn-undo').addEventListener('click', undoQ);

document.addEventListener('keydown', function(e) {
    var k = e.key.toLowerCase();
    if (e.key === ' ' || e.key === 'ArrowLeft' || k === 'k') {
        e.preventDefault();
        decide('restore');
    } else if (k === 'd' || e.key === 'ArrowRight' || k === 'j') {
        e.preventDefault();
        decide('confirm');
    } else if (k === 'b') {
        e.preventDefault();
        undoQ();
    }
});

load();
</script>

</body>
</html>'''


def get_candidates_sql():
    excl = ''
    if SESSION_CONFIRMED_DELETE:
        ids = ','.join(str(i) for i in SESSION_CONFIRMED_DELETE)
        excl = f" AND id NOT IN ({ids})"
    return f"""
        SELECT id, content
        FROM questions
        WHERE subject = '已刪除'
        {excl}
        ORDER BY id
    """


@app.route('/')
def index():
    return HTML


@app.route('/api/next')
def api_next():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM ({get_candidates_sql()})")
    remaining = cur.fetchone()[0]

    restored = sum(1 for h in SESSION_HISTORY if h[2] == '未分類')
    confirmed = sum(1 for h in SESSION_HISTORY if h[2] == '已刪除')
    done_count = restored + confirmed
    total = remaining + done_count

    cur.execute(get_candidates_sql() + ' LIMIT 1')
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({
            'done': True,
            'restored': restored, 'confirmed': confirmed
        })

    qid, content = row
    return jsonify({
        'id': qid, 'content': content,
        'done_count': done_count, 'total': total,
        'restored': restored, 'confirmed': confirmed,
        'done': False
    })


@app.route('/api/decide', methods=['POST'])
def api_decide():
    data = request.json
    qid = data['id']
    action = data['action']  # 'restore' or 'confirm'

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT subject FROM questions WHERE id = ?", (qid,))
    old = cur.fetchone()
    old_subject = old[0] if old else '已刪除'

    if action == 'restore':
        # 改回 未分類
        cur.execute("UPDATE questions SET subject = '未分類' WHERE id = ?", (qid,))
        conn.commit()
        SESSION_HISTORY.append((qid, old_subject, '未分類'))
    else:
        # 維持已刪除,記憶體標記避免再出現
        SESSION_CONFIRMED_DELETE.add(qid)
        SESSION_HISTORY.append((qid, old_subject, '已刪除'))

    conn.close()
    return jsonify({'ok': True})


@app.route('/api/undo', methods=['POST'])
def api_undo():
    if not SESSION_HISTORY:
        return jsonify({'ok': False})
    qid, old_subject, new_subject = SESSION_HISTORY.pop()

    if new_subject == '未分類':
        # 是救回的,要改回已刪除
        conn = get_conn()
        conn.execute("UPDATE questions SET subject = '已刪除' WHERE id = ?", (qid,))
        conn.commit()
        conn.close()
    else:
        # 是確認刪除的,從集合移除
        SESSION_CONFIRMED_DELETE.discard(qid)

    return jsonify({'ok': True, 'id': qid})


def backup_db(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = os.path.dirname(db_path)
    basename = os.path.basename(db_path).replace('.db', '')
    backup_path = os.path.join(dirname, f"{basename}.backup_revdel_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--port', type=int, default=5003)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--no-backup', action='store_true')
    args = parser.parse_args()

    DB_PATH = os.path.abspath(args.db)
    if not os.path.exists(DB_PATH):
        print(f"X DB 檔不存在: {DB_PATH}")
        exit(1)

    print(f"DB: {DB_PATH}")
    if not args.no_backup:
        backup = backup_db(DB_PATH)
        print(f"已備份: {backup}")

    conn = sqlite3.connect(DB_PATH)
    n = conn.execute(
        "SELECT COUNT(*) FROM questions WHERE subject = '已刪除'"
    ).fetchone()[0]
    conn.close()
    print(f"\n待回顧題數: {n}")
    print(f"\n啟動: http://localhost:{args.port}")
    print(f"操作: 空白/K/← 救回  ·  D/J/→ 確認刪除  ·  B 撤銷")
    print(f"按 Ctrl+C 結束\n")

    app.run(host=args.host, port=args.port, debug=False)
