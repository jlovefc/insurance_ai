# -*- coding: utf-8 -*-
"""
review_junk.py - 二選一 review 介面(保留 / 刪除)
====================================================
針對「疑似教材導讀題」做快速二選一判斷:
  - 保留 → 維持 subject='未分類',之後再用主分類工具分
  - 刪除 → 改 subject='已刪除'(不真的 DELETE,可還原)

啟動 (PowerShell):
    cd C:\\insurance_ai
    .\\venv\\Scripts\\activate
    python tools\\review_junk.py

瀏覽器: http://localhost:5002

操作:
  空白鍵 / ← / K     = 保留(這是真考題)
  D / → / J          = 刪除(這是教材導讀垃圾題)
  B                  = 撤銷上一題
"""
import argparse
import os
import shutil
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify

DEFAULT_DB = "platform/instance/insurance_exam.db"

# 與 restore_and_audit.py 相同的篩選條件,確保看到的是同一批 96 題
JUNK_KEYWORDS = [
    '教材', '本書', '本教材',
    '應試', '備考', '考生',
    '學習方法', '學習步驟', '學習指南',
    '複習', '複習方法', '複習策略',
    '參閱', '參閱章節', '參閱教材',
    '本章', '本節',
]

app = Flask(__name__)
DB_PATH = None
SESSION_HISTORY = []  # (id, old_subject, new_subject)


def get_conn():
    return sqlite3.connect(DB_PATH)


def get_candidates_sql():
    where = ' OR '.join([f"content LIKE '%{k}%'" for k in JUNK_KEYWORDS])
    return f"""
        SELECT id, content
        FROM questions
        WHERE subject = '未分類'
        AND ({where})
        ORDER BY id
    """


HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Review 垃圾題</title>
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
    background: #1f2418; border-left: 3px solid #4a7c3a;
    padding: 8px 12px; margin-bottom: 16px;
    font-size: 12px; color: #8aa078;
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
.btn-keep {
    background: linear-gradient(135deg, #d4af37, #b8941f);
    color: #1a1a1a;
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.25);
}
.btn-delete {
    background: #3a2020; color: #ff8888;
    border: 1px solid #5a3030;
}
.btn .sub { display: block; font-size: 11px; opacity: 0.7; margin-top: 4px; font-weight: 400; }
.aux {
    display: grid; grid-template-columns: 1fr; gap: 8px;
}
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
        <span>已 review <span id="done">0</span> / <span id="total">0</span></span>
        <span>保留 <span id="kept">0</span>  ·  刪除 <span id="deleted">0</span></span>
    </div>
    <div class="qid">題號 <span id="qid">-</span></div>
    <div class="question" id="content">載入中…</div>

    <div class="guide">
        判斷標準:題目本身在問「教材使用、考試流程、應試規則」→ <b>刪除</b><br>
        題目只是用「根據教材...」當開頭,實際在問保險知識 → <b>保留</b>
    </div>

    <div class="buttons">
        <button class="btn btn-keep" id="btn-keep">
            保留<span class="sub">真考題  /  空白 ← K</span>
        </button>
        <button class="btn btn-delete" id="btn-delete">
            刪除<span class="sub">垃圾題  /  D → J</span>
        </button>
    </div>

    <div class="aux">
        <button class="btn-aux" id="btn-undo">撤銷上一題 (B)</button>
    </div>
</div>
<div class="toast" id="toast"></div>

<script>
console.log('[review] script start');

var currentQ = null;

function showError(msg) {
    var box = document.getElementById('errbox');
    box.style.display = 'block';
    box.textContent = String(msg);
    console.error('[review]', msg);
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
            console.log('[review] data:', data);
            if (data.done) {
                document.getElementById('app').innerHTML =
                    '<div style="text-align:center;padding:60px 20px">' +
                    '<h2 style="color:#d4af37">Review 完成</h2>' +
                    '<p style="color:#888;margin:20px 0">' +
                    '保留 ' + data.kept + ' 題 / 刪除 ' + data.deleted + ' 題</p>' +
                    '<p style="color:#666;font-size:13px;margin-top:24px">' +
                    '可以關掉視窗了。<br>已刪題目改為 subject=\\'已刪除\\',需要時可還原。</p></div>';
                return;
            }
            currentQ = data;
            document.getElementById('content').textContent = data.content;
            document.getElementById('qid').textContent = '#' + data.id;
            document.getElementById('done').textContent = data.done_count;
            document.getElementById('total').textContent = data.total;
            document.getElementById('kept').textContent = data.kept;
            document.getElementById('deleted').textContent = data.deleted;
            document.getElementById('bar').style.width = (data.done_count * 100 / data.total) + '%';
        })
        .catch(function(err) { showError('load failed: ' + err.message); });
}

function decide(action) {
    if (!currentQ) return;
    console.log('[review] decide:', currentQ.id, '->', action);
    fetch('/api/decide', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: currentQ.id, action: action})
    })
    .then(function(r) { return r.json(); })
    .then(function() {
        showToast(action === 'keep' ? '✓ 保留' : '✗ 刪除', action === 'delete');
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

document.getElementById('btn-keep').addEventListener('click', function() { decide('keep'); });
document.getElementById('btn-delete').addEventListener('click', function() { decide('delete'); });
document.getElementById('btn-undo').addEventListener('click', undoQ);

document.addEventListener('keydown', function(e) {
    var k = e.key.toLowerCase();
    if (e.key === ' ' || e.key === 'ArrowLeft' || k === 'k') {
        e.preventDefault();
        decide('keep');
    } else if (k === 'd' || e.key === 'ArrowRight' || k === 'j') {
        e.preventDefault();
        decide('delete');
    } else if (k === 'b') {
        e.preventDefault();
        undoQ();
    }
});

load();
</script>

</body>
</html>'''


@app.route('/')
def index():
    return HTML


@app.route('/api/next')
def api_next():
    conn = get_conn()
    cur = conn.cursor()

    # 計算總候選數(含已 review 的,固定不變)
    # 因為 review 後 subject 會變,所以「總數」要用所有歷史 + 剩餘
    cur.execute(f"SELECT COUNT(*) FROM ({get_candidates_sql()})")
    remaining = cur.fetchone()[0]

    # 已 review = SESSION_HISTORY 數量
    kept = sum(1 for h in SESSION_HISTORY if h[2] == '未分類')
    deleted = sum(1 for h in SESSION_HISTORY if h[2] == '已刪除')
    done_count = kept + deleted
    total = remaining + done_count

    # 找下一題
    cur.execute(get_candidates_sql() + ' LIMIT 1')
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({
            'done': True,
            'kept': kept, 'deleted': deleted
        })

    qid, content = row
    return jsonify({
        'id': qid, 'content': content,
        'done_count': done_count, 'total': total,
        'kept': kept, 'deleted': deleted,
        'done': False
    })


@app.route('/api/decide', methods=['POST'])
def api_decide():
    data = request.json
    qid = data['id']
    action = data['action']
    new_subject = '未分類' if action == 'keep' else '已刪除'

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT subject FROM questions WHERE id = ?", (qid,))
    old = cur.fetchone()

    # 保留的話雖然 subject 不變(本來就是未分類),但仍寫一筆 history 以便撤銷
    # 且要標記為已 review,避免下次又出現 → 用 subject='已 review 保留' 嗎?不行,這樣
    # 主分類工具看不到它了。改用記憶體 set 排除。
    if action == 'keep':
        # 維持未分類,但加進 SESSION_REVIEWED_KEEP,避免重複出現
        SESSION_REVIEWED_KEEP.add(qid)
        if old:
            SESSION_HISTORY.append((qid, old[0], '未分類'))
        conn.close()
        return jsonify({'ok': True})

    # action == 'delete'
    if old:
        SESSION_HISTORY.append((qid, old[0], '已刪除'))
    cur.execute("UPDATE questions SET subject = '已刪除' WHERE id = ?", (qid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# 修改 get_candidates_sql 排除已保留的
SESSION_REVIEWED_KEEP = set()


def get_candidates_sql():
    where = ' OR '.join([f"content LIKE '%{k}%'" for k in JUNK_KEYWORDS])
    excl = ''
    if SESSION_REVIEWED_KEEP:
        ids = ','.join(str(i) for i in SESSION_REVIEWED_KEEP)
        excl = f" AND id NOT IN ({ids})"
    return f"""
        SELECT id, content
        FROM questions
        WHERE subject = '未分類'
        AND ({where})
        {excl}
        ORDER BY id
    """


@app.route('/api/undo', methods=['POST'])
def api_undo():
    if not SESSION_HISTORY:
        return jsonify({'ok': False})
    qid, old_subject, new_subject = SESSION_HISTORY.pop()

    if new_subject == '已刪除':
        # 還原到 DB
        conn = get_conn()
        conn.execute("UPDATE questions SET subject = ? WHERE id = ?",
                     (old_subject, qid))
        conn.commit()
        conn.close()
    else:
        # 是「保留」的撤銷,從 SESSION_REVIEWED_KEEP 移除
        SESSION_REVIEWED_KEEP.discard(qid)

    return jsonify({'ok': True, 'id': qid})


def backup_db(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = os.path.dirname(db_path)
    basename = os.path.basename(db_path).replace('.db', '')
    backup_path = os.path.join(dirname, f"{basename}.backup_review_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--port', type=int, default=5002)
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

    # 預先統計候選數
    conn = sqlite3.connect(DB_PATH)
    where = ' OR '.join([f"content LIKE '%{k}%'" for k in JUNK_KEYWORDS])
    n = conn.execute(
        f"SELECT COUNT(*) FROM questions WHERE subject='未分類' AND ({where})"
    ).fetchone()[0]
    conn.close()
    print(f"\n待 review 候選題數: {n}")
    print(f"\n啟動: http://localhost:{args.port}")
    print(f"操作: 空白/K/← 保留  ·  D/J/→ 刪除  ·  B 撤銷")
    print(f"按 Ctrl+C 結束\n")

    app.run(host=args.host, port=args.port, debug=False)
