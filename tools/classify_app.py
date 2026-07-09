# -*- coding: utf-8 -*-
"""
classify_app.py - 科目分類互動介面 (v2)
====================================
修正:
1. SUBJECTS 改用字串替換而非 Jinja tojson,避免 template 解析問題
2. 加上 console.log debug,F12 Console 可以看到執行流程
3. 整段包 try/catch,JS 出錯會在頁面紅框顯示
"""
import argparse
import os
import shutil
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify

DEFAULT_DB = "platform/instance/insurance_exam.db"
SUBJECTS = ['保險實務', '保險法規', '金融市場常識', '職業道德']

RULES = {
    '保險法規': {
        'strong': ['保險法第', '保險業法', '業務員管理規則', '管理規則第',
                   '契約解除', '契約撤銷', '契約效力', '主管機關', '金管會'],
        'medium': ['保險法', '保險利益', '解約金', '保單質借', '保單借款',
                   '指定受益人', '法定繼承', '應繼分', '繼承人',
                   '贈與稅', '遺產稅', '所得稅', '稅法', '稅務', '免稅',
                   '個人資料保護法', '消費者保護法', '保險業', '裁罰', '罰鍰'],
        'weak': ['法律', '法規', '法定', '條款規定']
    },
    '保險實務': {
        'strong': ['失能等級', '失能保險金', '失能給付', '給付比例',
                   '投資型保險', '投資型保單', '保單轉換', '適合度評估',
                   '核保', '理賠', '保額', '保費計算', '保險商品設計',
                   'CRM', '客戶關係管理', '客戶服務'],
        'medium': ['身故保險金', '住院醫療', '傷害保險', '健康保險',
                   '人身保險', '團體保險', '年金保險', '生存保險',
                   '風險自留', '危險自留', '風險管理', '危險管理',
                   '再保險', '分保', '保單', '保費',
                   '理賠審核', '核保流程', '生存保險金', '滿期保險金',
                   '保險商品', '招攬'],
        'weak': ['給付', '保險金', '計算']
    },
    '職業道德': {
        'strong': ['公平對待客戶', '不當銷售', '業務員倫理', '業務員道德',
                   '誠信原則', '利益衝突', '招攬規範'],
        'medium': ['職業道德', '道德', '誠信', '不實陳述', '說明義務',
                   '揭露義務', '個資保護', '保密義務',
                   '消費者保護', '客戶權益'],
        'weak': ['客戶', '消費者']
    },
    '金融市場常識': {
        'strong': ['金融科技', '電子支付', '第三方支付', 'FinTech',
                   '金融服務業', '金融市場', '金融體系',
                   '反洗錢', '洗錢防制'],
        'medium': ['銀行業務', '證券', '基金', '貨幣政策', '利率',
                   '通膨', '通貨膨脹', '股票', '債券', '匯率',
                   '存款保險', '金融創新', '巴塞爾協定',
                   '資本適足率', '金融商品'],
        'weak': ['市場', '金融']
    }
}


def score_content(content):
    scores = {s: 0 for s in SUBJECTS}
    for subject, kws in RULES.items():
        for kw in kws.get('strong', []):
            if kw in content:
                scores[subject] += 3
        for kw in kws.get('medium', []):
            if kw in content:
                scores[subject] += 2
        for kw in kws.get('weak', []):
            if kw in content:
                scores[subject] += 1
    return scores


app = Flask(__name__)
DB_PATH = None
SESSION_SKIPPED = set()
SESSION_HISTORY = []
SUBJECTS_JSON = json.dumps(SUBJECTS, ensure_ascii=False)

HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>科目分類</title>
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
    line-height: 1.85; margin-bottom: 16px;
    font-size: 16px; color: #e4e4e4; min-height: 100px;
}
.buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 6px; }
.btn {
    background: #2a2a2a; color: #d4af37;
    border: 1px solid #555; padding: 20px 12px;
    border-radius: 8px; font-size: 15px;
    cursor: pointer; font-family: inherit;
    position: relative; transition: all 0.15s;
}
.btn:active { transform: scale(0.97); }
.btn:hover { border-color: #d4af37; }
.btn.suggested {
    background: linear-gradient(135deg, #d4af37, #b8941f);
    color: #1a1a1a; border-color: #d4af37; font-weight: 600;
}
.shortcut {
    position: absolute; top: 4px; left: 6px; font-size: 10px;
    opacity: 0.55; background: rgba(0,0,0,0.3);
    padding: 1px 4px; border-radius: 3px;
}
.hint { text-align: center; font-size: 11px; color: #666; margin: 8px 0 12px; }
.aux { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.btn-aux {
    background: transparent; color: #888;
    border: 1px solid #444; padding: 12px;
    border-radius: 8px; font-size: 13px;
    cursor: pointer; font-family: inherit;
}
.scores { font-size: 11px; color: #555; text-align: center; margin: 6px 0; }
.scores span { margin: 0 6px; }
.toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #2a2a2a; color: #d4af37;
    padding: 10px 18px; border-radius: 20px;
    border: 1px solid #d4af37; font-size: 13px;
    opacity: 0; transition: opacity 0.3s; pointer-events: none;
}
.toast.show { opacity: 1; }
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
        <span>已分類 <span id="done">0</span> / <span id="total">0</span></span>
        <span>剩餘 <span id="remaining">0</span></span>
    </div>
    <div class="qid">題號 <span id="qid">-</span></div>
    <div class="question" id="content">載入中…</div>
    <div class="buttons" id="buttons"></div>
    <div class="scores" id="scores"></div>
    <div class="hint">Enter 接受建議  ·  1234 直選  ·  S 跳過  ·  B 撤銷</div>
    <div class="aux">
        <button class="btn-aux" id="btn-skip">跳過 (S)</button>
        <button class="btn-aux" id="btn-undo">撤銷上一題 (B)</button>
    </div>
</div>
<div class="toast" id="toast"></div>

<script>
console.log('[classify] script start');

var SUBJECTS = __SUBJECTS_JSON__;
console.log('[classify] SUBJECTS =', SUBJECTS);

var currentQ = null;

function showError(msg) {
    var box = document.getElementById('errbox');
    box.style.display = 'block';
    box.textContent = String(msg);
    console.error('[classify]', msg);
}

window.addEventListener('error', function(e) {
    showError('JS Error: ' + e.message);
});

function showToast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(function() { t.classList.remove('show'); }, 1400);
}

function load() {
    console.log('[classify] load() start');
    fetch('/api/next')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            console.log('[classify] /api/next ->', data);
            if (data.done) {
                document.getElementById('app').innerHTML =
                    '<div style="text-align:center;padding:60px 20px"><h2 style="color:#d4af37">全部完成</h2>' +
                    '<p style="color:#888">' + data.total + ' 題已分類</p></div>';
                return;
            }
            currentQ = data;
            document.getElementById('content').textContent = data.content;
            document.getElementById('qid').textContent = '#' + data.id;
            document.getElementById('done').textContent = data.done_count;
            document.getElementById('total').textContent = data.total;
            document.getElementById('remaining').textContent = data.remaining;
            document.getElementById('bar').style.width = (data.done_count * 100 / data.total) + '%';

            var btns = document.getElementById('buttons');
            btns.innerHTML = '';
            for (var i = 0; i < SUBJECTS.length; i++) {
                (function(idx) {
                    var s = SUBJECTS[idx];
                    var b = document.createElement('button');
                    b.className = 'btn' + (data.suggestion === s ? ' suggested' : '');
                    b.innerHTML = '<span class="shortcut">' + (idx+1) + '</span>' + s;
                    b.addEventListener('click', function() {
                        console.log('[classify] click:', s);
                        classify(s);
                    });
                    btns.appendChild(b);
                })(i);
            }

            var sc = document.getElementById('scores');
            if (data.scores) {
                var items = [];
                for (var k in data.scores) {
                    if (data.scores[k] > 0) items.push('<span>' + k + '・' + data.scores[k] + '</span>');
                }
                sc.innerHTML = items.length ? items.join('') : '<span style="opacity:0.4">無關鍵字命中</span>';
            } else {
                sc.innerHTML = '';
            }
        })
        .catch(function(err) { showError('load failed: ' + err.message); });
}

function classify(subject) {
    if (!currentQ) { console.warn('[classify] no currentQ'); return; }
    fetch('/api/classify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: currentQ.id, subject: subject})
    })
    .then(function(r) { return r.json(); })
    .then(function() {
        showToast('OK ' + subject);
        load();
    })
    .catch(function(err) { showError('classify failed: ' + err.message); });
}

function skipQ() {
    if (!currentQ) return;
    fetch('/api/skip', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: currentQ.id})
    }).then(function() { load(); });
}

function undoQ() {
    fetch('/api/undo', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) { showToast('已撤銷 #' + data.id); load(); }
            else { showToast('沒有可撤銷的'); }
        });
}

document.getElementById('btn-skip').addEventListener('click', skipQ);
document.getElementById('btn-undo').addEventListener('click', undoQ);

document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        if (currentQ && currentQ.suggestion) classify(currentQ.suggestion);
        else showToast('沒有建議,請手動選擇');
    } else if (e.key >= '1' && e.key <= '4') {
        e.preventDefault();
        classify(SUBJECTS[parseInt(e.key) - 1]);
    } else if (e.key === 's' || e.key === 'S') {
        e.preventDefault(); skipQ();
    } else if (e.key === 'b' || e.key === 'B') {
        e.preventDefault(); undoQ();
    }
});

console.log('[classify] listeners attached, calling load()');
load();
</script>

</body>
</html>'''


def get_conn():
    return sqlite3.connect(DB_PATH)


@app.route('/')
def index():
    return HTML.replace('__SUBJECTS_JSON__', SUBJECTS_JSON)


@app.route('/api/next')
def api_next():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM questions")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM questions WHERE subject = '未分類'")
    remaining = cur.fetchone()[0]
    done_count = total - remaining

    if SESSION_SKIPPED:
        placeholders = ','.join('?' * len(SESSION_SKIPPED))
        cur.execute(
            f"SELECT id, content FROM questions "
            f"WHERE subject = '未分類' AND id NOT IN ({placeholders}) "
            f"ORDER BY id LIMIT 1",
            list(SESSION_SKIPPED)
        )
    else:
        cur.execute(
            "SELECT id, content FROM questions "
            "WHERE subject = '未分類' ORDER BY id LIMIT 1"
        )
    row = cur.fetchone()
    conn.close()

    if not row:
        if SESSION_SKIPPED and remaining > 0:
            SESSION_SKIPPED.clear()
            return api_next()
        return jsonify({'done': True, 'total': done_count})

    qid, content = row
    scores = score_content(content)
    top = max(scores.items(), key=lambda x: x[1])
    suggestion = top[0] if top[1] > 0 else None

    return jsonify({
        'id': qid, 'content': content,
        'suggestion': suggestion, 'scores': scores,
        'done_count': done_count, 'remaining': remaining,
        'total': total, 'done': False
    })


@app.route('/api/classify', methods=['POST'])
def api_classify():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT subject FROM questions WHERE id = ?", (data['id'],))
    old = cur.fetchone()
    if old:
        SESSION_HISTORY.append((data['id'], old[0], data['subject']))
    cur.execute("UPDATE questions SET subject = ? WHERE id = ?",
                (data['subject'], data['id']))
    conn.commit()
    conn.close()
    SESSION_SKIPPED.discard(data['id'])
    return jsonify({'ok': True})


@app.route('/api/skip', methods=['POST'])
def api_skip():
    data = request.json
    SESSION_SKIPPED.add(data['id'])
    return jsonify({'ok': True})


@app.route('/api/undo', methods=['POST'])
def api_undo():
    if not SESSION_HISTORY:
        return jsonify({'ok': False})
    qid, old_subject, new_subject = SESSION_HISTORY.pop()
    conn = get_conn()
    conn.execute("UPDATE questions SET subject = ? WHERE id = ?",
                 (old_subject, qid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': qid})


def backup_db(db_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = os.path.dirname(db_path)
    basename = os.path.basename(db_path).replace('.db', '')
    backup_path = os.path.join(dirname, f"{basename}.backup_classify_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--port', type=int, default=5001)
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
    cur = conn.cursor()
    cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC")
    print("\n目前 subject 分佈:")
    for s, c in cur.fetchall():
        print(f"  {s}: {c}")
    conn.close()

    print(f"\n啟動: http://localhost:{args.port}")
    print(f"按 Ctrl+C 結束\n")
    app.run(host=args.host, port=args.port, debug=False)
