import os
import json
import random
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

import anthropic
claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

from models import db, User, Question, QuizSession, UserAnswer, WeakArea, UserQuestionMark

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance_exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ────────────────────────────────────────────────
# ★ Batch A 新增:啟動時自動建立 Humble / Chrisa 兩個免密碼帳號
# ────────────────────────────────────────────────
def seed_default_users():
    """確保 Humble 和 Chrisa 存在;若帳號已存在不動它。"""
    defaults = ['Humble', 'Chrisa']
    for name in defaults:
        existing = User.query.filter_by(username=name).first()
        if not existing:
            user = User(username=name, password_hash=None)
            db.session.add(user)
    db.session.commit()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

        # 帳號若無密碼(快速登入帳號),不接受密碼登入
        if user.password_hash is None:
            return jsonify({'success': False, 'message': '此帳號為快速登入,請從卡片登入'})

        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

    # GET: 把所有快速登入帳號帶到模板顯示為卡片
    quick_users = User.query.filter_by(password_hash=None).order_by(User.id).all()
    return render_template('login.html', quick_users=quick_users)


# ★ Batch A 新增:快速登入(免密碼)
@app.route('/login/quick/<username>', methods=['POST'])
def quick_login(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': '找不到此帳號'}), 404
    if user.password_hash is not None:
        return jsonify({'success': False, 'message': '此帳號需要密碼登入'}), 403
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'success': True, 'redirect': url_for('dashboard')})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'message': '帳號與密碼為必填'})
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '此帳號已被使用'})
    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '此信箱已被使用'})
    user = User(username=username, email=email or None,
                password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'success': True})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])

    # ★ Batch A: 取出所有 (subject, unit) 配對給前端做兩階下拉
    # 內部狀態 subject,不出現在使用者選單
    HIDDEN_SUBJECTS = {'已刪除', '未分類'}
    subject_units = (db.session.query(Question.subject, Question.unit)
                     .filter(~Question.subject.in_(HIDDEN_SUBJECTS))
                     .distinct().all())
    # 各科題數統計
    from sqlalchemy import func
    _counts = (db.session.query(Question.subject, func.count(Question.id))
               .group_by(Question.subject).all())
    subject_count = {s: n for s, n in _counts
                     if s and s not in HIDDEN_SUBJECTS}

    def is_valid_unit(u):
        if not u or len(u.strip()) < 2:
            return False
        import re
        if re.match(r'^[Pp]\d+\.(jpg|png|pdf)$', u.strip(), re.IGNORECASE):
            return False
        if re.match(r'^\d+$', u.strip()):
            return False
        return True

    subject_unit_map = {}
    for subj, unit in subject_units:
        if not is_valid_unit(unit):
            continue
        subj_key = subj or '未分類'
        subject_unit_map.setdefault(subj_key, []).append(unit)
    for subj in subject_unit_map:
        subject_unit_map[subj] = sorted(set(subject_unit_map[subj]))

    units = sorted({u for lst in subject_unit_map.values() for u in lst})

    total_sessions = QuizSession.query.filter_by(user_id=user.id).count()
    total_questions = Question.query.count()

    favorite_count = UserQuestionMark.query.filter_by(
        user_id=user.id, mark_type='favorite').count()
    mastered_count = UserQuestionMark.query.filter_by(
        user_id=user.id, mark_type='mastered').count()

    weak_areas = (WeakArea.query.filter_by(user_id=user.id)
                  .filter(WeakArea.total_count > 0)
                  .order_by(WeakArea.wrong_count.desc()).limit(5).all())
    weak_data = []
    for w in weak_areas:
        acc = round((w.total_count - w.wrong_count) / w.total_count * 100) if w.total_count else 0
        weak_data.append({'unit': w.unit, 'wrong': w.wrong_count, 'total': w.total_count, 'accuracy': acc})

    return render_template('dashboard.html',
                           user=user,
                           units=units,
                           subject_unit_map=subject_unit_map,
                           subject_count=subject_count,
                           total_sessions=total_sessions,
                           total_questions=total_questions,
                           favorite_count=favorite_count,
                           mastered_count=mastered_count,
                           weak_data=weak_data)


@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')


@app.route('/report/<int:session_id>')
@login_required
def report(session_id):
    quiz_session = QuizSession.query.get_or_404(session_id)
    if quiz_session.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    answers = UserAnswer.query.filter_by(session_id=session_id).all()
    weak_areas = (WeakArea.query.filter_by(user_id=session['user_id'])
                  .filter(WeakArea.total_count > 0)
                  .order_by(WeakArea.wrong_count.desc()).limit(5).all())
    weak_data = []
    for w in weak_areas:
        acc = round((w.total_count - w.wrong_count) / w.total_count * 100) if w.total_count else 0
        weak_data.append({'unit': w.unit, 'wrong': w.wrong_count, 'total': w.total_count, 'accuracy': acc})
    return render_template('report.html', quiz_session=quiz_session,
                           answers=answers, weak_data=weak_data)


@app.route('/api/quiz/start', methods=['POST'])
@login_required
def start_quiz():
    data = request.get_json()
    mode = data.get('mode', 'random')
    unit = data.get('unit', 'all')
    subject = data.get('subject', 'all')  # ★ Batch A: 新增科目參數
    count = int(data.get('count', 10))
    focus_weak = data.get('focus_weak', False)
    focus_favorite = data.get('focus_favorite', False)  # ★ 收藏題練習
    uid = session['user_id']

    # ★ Batch A: 抓本使用者已精熟的題目 id,出題時排除
    mastered_ids = {m.question_id for m in
                    UserQuestionMark.query.filter_by(
                        user_id=uid, mark_type='mastered').all()}

    if focus_favorite:
        fav_ids = [m.question_id for m in
                   UserQuestionMark.query.filter_by(
                       user_id=uid, mark_type='favorite').all()]
        questions = Question.query.filter(Question.id.in_(fav_ids)).all() if fav_ids else []
    elif focus_weak:
        weak = (WeakArea.query.filter_by(user_id=uid)
                .order_by(WeakArea.wrong_count.desc()).limit(3).all())
        weak_units = [w.unit for w in weak]
        questions = (Question.query
                     .filter(Question.unit.in_(weak_units))
                     .filter(~Question.id.in_(mastered_ids))
                     .all())
        if len(questions) < count:
            extra = (Question.query
                     .filter(~Question.unit.in_(weak_units))
                     .filter(~Question.id.in_(mastered_ids))
                     .limit(count - len(questions)).all())
            questions.extend(extra)
    else:
        q = Question.query.filter(~Question.id.in_(mastered_ids))
        if subject and subject != 'all':
            q = q.filter(Question.subject == subject)
        if unit and unit != 'all':
            q = q.filter(Question.unit == unit)
        questions = q.all()

    if not questions:
        msg = '題庫為空,請先載入題目'
        if mastered_ids:
            msg = '此範圍內的題目都已精熟,沒有可練習的新題目!\n換個科目/章節看看,或解除部分題目的精熟標記。'
        return jsonify({'error': msg}), 400

    selected = random.sample(questions, min(count, len(questions)))
    quiz_session = QuizSession(user_id=uid, mode=mode,
                               unit_name=unit, total_questions=len(selected))
    db.session.add(quiz_session)
    db.session.commit()

    q_ids = [q.id for q in selected]
    marks = {m.question_id: m.mark_type for m in
             UserQuestionMark.query.filter(
                 UserQuestionMark.user_id == uid,
                 UserQuestionMark.question_id.in_(q_ids)).all()}

    questions_data = []
    for qst in selected:
        try:
            options = json.loads(qst.options)
        except Exception:
            options = [qst.options]
        questions_data.append({
            'id': qst.id,
            'content': qst.content,
            'options': options,
            'unit': qst.unit,
            'subject': qst.subject,
            'correct_answer': qst.correct_answer,
            'mark_type': marks.get(qst.id)
        })
    return jsonify({'session_id': quiz_session.id, 'questions': questions_data})


@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.get_json()
    session_id = data.get('session_id')
    answers = data.get('answers', [])
    uid = session['user_id']

    quiz_session = QuizSession.query.get(session_id)
    if not quiz_session or quiz_session.user_id != uid:
        return jsonify({'error': '無效的測驗'}), 400

    correct_count = 0
    results = []
    for ans in answers:
        question = Question.query.get(ans.get('question_id'))
        if not question:
            continue
        user_answer_str = str(ans.get('answer', '')).strip()
        _letter_to_num = {'A':'1','B':'2','C':'3','D':'4','E':'5'}
        _norm_answer = _letter_to_num.get(user_answer_str.upper(), user_answer_str)
        is_correct = _norm_answer == str(question.correct_answer).strip()
        if is_correct:
            correct_count += 1
        ua = UserAnswer(session_id=session_id, question_id=question.id,
                        user_answer=user_answer_str, is_correct=is_correct,
                        time_spent=ans.get('time_spent', 0))
        db.session.add(ua)

        weak = WeakArea.query.filter_by(user_id=uid, unit=question.unit).first()
        if not weak:
            weak = WeakArea(user_id=uid, unit=question.unit,
                            total_count=0, wrong_count=0)
            db.session.add(weak)
        weak.total_count = (weak.total_count or 0) + 1
        if not is_correct:
            weak.wrong_count = (weak.wrong_count or 0) + 1
        weak.last_tested = datetime.utcnow()

        # ★ Batch A: 更新 UserQuestionMark,實作收藏→精熟自動升級
        mark = UserQuestionMark.query.filter_by(
            user_id=uid, question_id=question.id).first()
        if not mark:
            mark = UserQuestionMark(user_id=uid, question_id=question.id,
                                    mark_type=None, correct_streak=0)
            db.session.add(mark)

        if is_correct:
            mark.correct_streak = (mark.correct_streak or 0) + 1
            if mark.mark_type == 'favorite' and mark.correct_streak >= 3:
                mark.mark_type = 'mastered'
        else:
            mark.correct_streak = 0

        mark_action = ans.get('mark_action')
        if mark_action in ('favorite', 'mastered'):
            mark.mark_type = mark_action
        elif mark_action == 'clear':
            mark.mark_type = None

        mark.last_practiced = datetime.utcnow()

        try:
            options = json.loads(question.options)
        except Exception:
            options = [question.options]
        results.append({
            'question_id': question.id,
            'question': question.content,
            'options': options,
            'user_answer': user_answer_str,
            'correct_answer': question.correct_answer,
            'is_correct': is_correct,
            'explanation': question.explanation or '',
            'unit': question.unit,
            'mark_type': mark.mark_type
        })

    quiz_session.score = correct_count
    quiz_session.end_time = datetime.utcnow()
    db.session.commit()

    total = len(answers)
    pct = round(correct_count / total * 100) if total else 0
    return jsonify({
        'session_id': session_id,
        'score': correct_count,
        'total': total,
        'percentage': pct,
        'results': results
    })


# ★ Batch A 新增:單獨對某題設定標記
@app.route('/api/mark-question', methods=['POST'])
@login_required
def mark_question():
    data = request.get_json()
    question_id = data.get('question_id')
    mark_type = data.get('mark_type')
    uid = session['user_id']

    if not question_id:
        return jsonify({'error': 'question_id 必填'}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': '題目不存在'}), 404

    mark = UserQuestionMark.query.filter_by(
        user_id=uid, question_id=question_id).first()
    if not mark:
        mark = UserQuestionMark(user_id=uid, question_id=question_id,
                                correct_streak=0)
        db.session.add(mark)

    if mark_type in (None, 'clear', ''):
        mark.mark_type = None
    elif mark_type in ('favorite', 'mastered'):
        mark.mark_type = mark_type
    else:
        return jsonify({'error': 'mark_type 必須為 favorite / mastered / clear'}), 400

    mark.last_practiced = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'mark_type': mark.mark_type})


# ★ Batch A 新增:查詢個人收藏/精熟清單
@app.route('/api/my-marks')
@login_required
def my_marks():
    uid = session['user_id']
    mark_type = request.args.get('type', 'favorite')

    marks = (UserQuestionMark.query
             .filter_by(user_id=uid, mark_type=mark_type)
             .order_by(UserQuestionMark.last_practiced.desc())
             .all())
    result = []
    for m in marks:
        q = Question.query.get(m.question_id)
        if not q:
            continue
        result.append({
            'question_id': q.id,
            'content': q.content[:80] + ('...' if len(q.content) > 80 else ''),
            'subject': q.subject,
            'unit': q.unit,
            'correct_streak': m.correct_streak,
            'last_practiced': m.last_practiced.isoformat() if m.last_practiced else None
        })
    return jsonify({'count': len(result), 'marks': result})


@app.route('/api/explanation/<int:question_id>')
@login_required
def get_explanation(question_id):
    q = Question.query.get_or_404(question_id)
    try:
        options = json.loads(q.options)
    except Exception:
        options = [q.options]
    return jsonify({
        'question': q.content, 'options': options,
        'correct_answer': q.correct_answer,
        'explanation': q.explanation or '此題目尚無詳細解說,建議複習相關章節。',
        'unit': q.unit
    })


@app.route('/api/rich-explanation/<int:question_id>')
@login_required
def get_rich_explanation(question_id):
    """用 Claude AI 生成多媒體動畫解說內容"""
    q = Question.query.get_or_404(question_id)
    try:
        options = json.loads(q.options)
    except Exception:
        options = [q.options]

    options_text = '\n'.join(options)

    content_prompt = f"""你是台灣最受歡迎的保險考照補習班名師。請針對以下題目,用口語化的方式生成教學內容。

題目:{q.content}
選項:
{options_text}
正確答案:{q.correct_answer}
教材解說:{q.explanation or '(無)'}
所屬單元:{q.unit}

請依序提供以下內容,每個項目用【】標記:

【核心概念】一句話(15字內)說明這題的考試重點或陷阱

【重點1標題】
【重點1內容】具體說明為什麼答案是{q.correct_answer},分析錯誤選項的陷阱

【重點2標題】
【重點2內容】考生最常犯的錯誤觀念,為什麼那樣想是錯的

【重點3標題】
【重點3內容】這個概念的關鍵規定或數字,要非常具體

【心智圖中心】3-5個字的核心關鍵詞
【分支1】正確的法規規定
【分支1細節】兩個具體規定,用逗號分隔
【分支2】常見的錯誤觀念
【分支2細節】兩個錯誤觀念,用逗號分隔
【分支3】記憶訣竅
【分支3細節】兩個記憶方法,用逗號分隔

【生活場景emoji】一個emoji
【生活場景名稱】5字以內的場景描述
【生活比喻】用台灣人熟悉的真實生活場景比喻(便利商店、捷運、租屋、醫院、夜市等),口語化像朋友解釋,100字以內

【真實案例】舉一個台灣實際發生的保險相關案例或新聞,說明這個概念的重要性,60字以內

【記憶口訣】設計一個押韻或諧音的口訣,幫助記住答案是{q.correct_answer}的原因。必須要有創意,可以用:數字諧音、押韻句子、首字縮寫等。不能只寫「答案是X」,要讓人覺得有趣好背。

【語音朗讀】用輕鬆的補習班老師口吻朗讀這題的解說,包含重點、比喻和口訣"""

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": content_prompt}]
        )
        raw_text = response.content[0].text.strip()
        print(f"✅ Claude 回應長度:{len(raw_text)} 字")

        def extract(tag, text):
            import re
            pattern = rf'【{tag}】\s*(.*?)(?=【|\Z)'
            m = re.search(pattern, text, re.DOTALL)
            return m.group(1).strip() if m else ''

        summary = extract('核心概念', raw_text)
        kp1_title = extract('重點1標題', raw_text)
        kp1_content = extract('重點1內容', raw_text)
        kp2_title = extract('重點2標題', raw_text)
        kp2_content = extract('重點2內容', raw_text)
        kp3_title = extract('重點3標題', raw_text)
        kp3_content = extract('重點3內容', raw_text)

        mm_center = extract('心智圖中心', raw_text)
        b1_label = extract('分支1', raw_text)
        b1_children = [x.strip() for x in extract('分支1細節', raw_text).split(',') if x.strip()]
        b2_label = extract('分支2', raw_text)
        b2_children = [x.strip() for x in extract('分支2細節', raw_text).split(',') if x.strip()]
        b3_label = extract('分支3', raw_text)
        b3_children = [x.strip() for x in extract('分支3細節', raw_text).split(',') if x.strip()]

        analogy_emoji = extract('生活場景emoji', raw_text) or '💡'
        analogy_title = extract('生活場景名稱', raw_text)
        analogy = extract('生活比喻', raw_text)
        real_example = extract('真實案例', raw_text)
        memory_tip = extract('記憶口訣', raw_text)
        tts_text = extract('語音朗讀', raw_text)

        rich_data = {
            'question': q.content,
            'options': options,
            'correct_answer': q.correct_answer,
            'unit': q.unit,
            'summary': summary or f'{q.unit}的核心考點',
            'key_points': [
                {'icon': '🎯', 'title': kp1_title or '答題關鍵', 'content': kp1_content or q.explanation or ''},
                {'icon': '⚠️', 'title': kp2_title or '常見錯誤', 'content': kp2_content or ''},
                {'icon': '📌', 'title': kp3_title or '必記規則', 'content': kp3_content or ''},
            ],
            'mind_map': {
                'center': mm_center or q.unit[:5],
                'branches': [
                    {'label': b1_label or '正確規定', 'color': '#3FB950', 'children': b1_children or [q.correct_answer]},
                    {'label': b2_label or '常見陷阱', 'color': '#F85149', 'children': b2_children or ['注意混淆']},
                    {'label': b3_label or '記憶方法', 'color': '#C9A243', 'children': b3_children or ['口訣聯想']},
                ]
            },
            'analogy_emoji': analogy_emoji,
            'analogy_title': analogy_title or '生活比喻',
            'analogy': analogy or '',
            'real_example': real_example or '',
            'memory_tip': memory_tip or '',
            'tts_text': tts_text or f'這題答案是{q.correct_answer}。{q.explanation or ""}'
        }

        return jsonify({'success': True, 'data': rich_data})

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Claude API 錯誤: {error_msg}")
        return jsonify({
            'success': True,
            'data': {
                'question': q.content, 'options': options,
                'correct_answer': q.correct_answer, 'unit': q.unit,
                'summary': f'⚠️ 生成失敗,請重試',
                'key_points': [
                    {'icon': '📌', 'title': '正確答案', 'content': q.correct_answer},
                    {'icon': '📖', 'title': '解說', 'content': q.explanation or '請參閱教材'}
                ],
                'mind_map': {'center': q.unit[:5], 'branches': [
                    {'label': '正確答案', 'color': '#C9A243', 'children': [q.correct_answer]}
                ]},
                'analogy_emoji': '📚', 'analogy_title': '教材說明',
                'analogy': q.explanation or '請參閱相關教材章節',
                'real_example': '', 'memory_tip': f'答案:{q.correct_answer}',
                'tts_text': f'題目:{q.content}。正確答案是{q.correct_answer}。{q.explanation or ""}'
            }
        })


@app.route('/api/weak-areas')
@login_required
def get_weak_areas():
    areas = (WeakArea.query.filter_by(user_id=session['user_id'])
             .filter(WeakArea.total_count > 0)
             .order_by(WeakArea.wrong_count.desc()).all())
    return jsonify([{
        'unit': w.unit, 'wrong_count': w.wrong_count, 'total_count': w.total_count,
        'accuracy': round((w.total_count - w.wrong_count) / w.total_count * 100) if w.total_count else 0
    } for w in areas])


@app.route('/api/load-questions', methods=['POST'])
@login_required
def load_questions():
    """自動掃描 output 目錄下所有 question_bank*.json,用 (subject + content) 雙鍵去重。"""
    output_dir = Path(r'C:\insurance_ai\output')

    if not output_dir.exists():
        return jsonify({'error': f'找不到輸出資料夾:{output_dir}'}), 404

    json_files = sorted(output_dir.glob('question_bank*.json'))
    if not json_files:
        return jsonify({'error': f'在 {output_dir} 找不到任何 question_bank*.json 檔案'}), 404

    total_loaded = 0
    total_skipped = 0
    per_file_stats = []

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except Exception as e:
            per_file_stats.append({'file': json_file.name, 'error': str(e)})
            continue

        loaded = 0
        skipped = 0
        for q_data in questions_data:
            content = q_data.get('question', q_data.get('content', '')).strip()
            if not content:
                continue

            subject = q_data.get('subject', '未分類').strip()

            if Question.query.filter_by(subject=subject, content=content).first():
                skipped += 1
                continue

            raw_options = q_data.get('options', {})
            if isinstance(raw_options, dict):
                options = [f"{k}. {v}" for k, v in raw_options.items()]
            else:
                options = raw_options
            question = Question(
                subject=subject,
                content=content,
                options=json.dumps(options, ensure_ascii=False),
                correct_answer=str(q_data.get('answer', q_data.get('correct_answer', 'A'))),
                unit=q_data.get('unit', q_data.get('topic', q_data.get('source_file', '未分類'))),
                explanation=q_data.get('explanation', ''),
                difficulty=q_data.get('difficulty', 'medium')
            )
            db.session.add(question)
            loaded += 1

        per_file_stats.append({
            'file': json_file.name,
            'loaded': loaded,
            'skipped': skipped,
        })
        total_loaded += loaded
        total_skipped += skipped

    db.session.commit()
    return jsonify({
        'success': True,
        'loaded': total_loaded,
        'skipped': total_skipped,
        'files': per_file_stats,
    })


@app.route('/api/stats')
@login_required
def get_stats():
    uid = session['user_id']
    sessions = QuizSession.query.filter_by(user_id=uid).all()
    if not sessions:
        return jsonify({'total_sessions': 0, 'avg_score': 0, 'best_score': 0})
    scores = [s.score / s.total_questions * 100 for s in sessions if s.total_questions > 0]
    return jsonify({
        'total_sessions': len(sessions),
        'avg_score': round(sum(scores) / len(scores)) if scores else 0,
        'best_score': round(max(scores)) if scores else 0
    })


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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_users()  # ★ Batch A: 確保 Humble / Chrisa 存在
        print('✅ 資料庫初始化完成')
        print('✅ 已確保 Humble / Chrisa 帳號存在')
    app.run(debug=True, host='0.0.0.0', port=5000)

