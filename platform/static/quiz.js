/* ═══════════════════════════════════════════════
   quiz.js v4 (Batch C)
   - 點選項立即公布答案
   - 自動剝除 A./B./C./D. 重複前綴
   - 公布答案後顯示 [⭐收藏] [🎯精熟] [下一題]
   - 即時計分顯示 (✓N · ✗N)
   - 移除 AI 深入解說 (改為純教材原解說)
═══════════════════════════════════════════════ */

const state = {
  sessionId: null,
  questions: [],
  currentIdx: 0,
  answers: [],          // 提交 quiz 用,每筆 {question_id, answer, time_spent, mark_action}
  marks: {},            // 本次測驗中每題的標記:{ question_id: 'favorite' | 'mastered' | null }
  answered: false,
  startTime: null,
  questionStartTime: null,
  timerInterval: null,
  correctCount: 0,
  wrongCount: 0,
  currentUser: null,  /* user_explanations 用:{id, username, is_admin} */
};

window.addEventListener('DOMContentLoaded', async () => {
  const params = JSON.parse(sessionStorage.getItem('quizParams') || '{}');
  if (!params.mode) { window.location.href = '/dashboard'; return; }
  await loadQuiz(params);
});

async function loadQuiz(params) {
  try {
    const res = await fetch('/api/quiz/start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(params)
    });
    const data = await res.json();
    if (data.error) { showError(data.error); return; }
    state.sessionId = data.session_id;
    state.currentUser = data.user || null;  /* user_explanations 需要 */
    state.questions = data.questions;
    // 把每題進來時的標記放進 state.marks (進入測驗時就帶著)
    state.questions.forEach(q => { state.marks[q.id] = q.mark_type || null; });
    state.startTime = Date.now();
    hide('loadingState');
    show('questionArea');
    startTimer();
    showQuestion(0);
  } catch (e) {
    showError('無法連線,請確認伺服器是否已啟動。');
  }
}

// ★ Batch C: 剝除選項文字最前面的 A./B./C./D. 前綴(全形半形都處理)
function stripOptionPrefix(text) {
  if (!text) return '';
  // 處理:A. / B、 / C: / D / (1) / (Ａ) 等等的開頭
  return String(text)
    .replace(/^\s*[（(]?[A-DＡ-Ｄa-d１-４1-4][)）]?\s*[\.、:：．]\s*/, '')
    .replace(/^\s*[（(][A-DＡ-Ｄ1-4１-４][)）]\s*/, '')
    .trim();
}

function showQuestion(idx) {
  const q = state.questions[idx];
  state.currentIdx = idx;
  state.answered = false;
  state.questionStartTime = Date.now();

  const progress = ((idx + 1) / state.questions.length) * 100;
  document.getElementById('progressFill').style.width = progress + '%';
  document.getElementById('progressText').textContent = `第 ${idx + 1} 題 / 共 ${state.questions.length} 題`;
  document.getElementById('questionNum').textContent = `Q${idx + 1}`;
  document.getElementById('questionUnit').textContent = q.unit || '─';
  document.getElementById('questionText').textContent = q.content;

  // 隱藏 feedback / actions
  const feedback = document.getElementById('answerFeedback');
  feedback.className = 'answer-feedback hidden';
  document.getElementById('feedbackExplain').classList.add('hidden');
  var _userExp = document.getElementById('userExpArea');
  if (_userExp) _userExp.innerHTML = '';
  hide('quizActions');

  // 渲染選項 (剝除前綴避免「A. A. 年金保險」這種重複)
  const labels = ['(1)', '(2)', '(3)', '(4)', '(5)']; /* PATCHED_SHOW_NUMBERS */
  const list = document.getElementById('optionsList');
  list.innerHTML = '';
  q.options.forEach((opt, i) => {
    const cleanText = stripOptionPrefix(opt);
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.innerHTML = `<span class="option-label">${labels[i]}</span><span class="option-text"></span>`;
    btn.querySelector('.option-text').textContent = cleanText;
    btn.addEventListener('click', () => selectAnswer(i, btn, q));
    list.appendChild(btn);
  });

  document.getElementById('questionArea').style.animation = 'none';
  requestAnimationFrame(() => {
    document.getElementById('questionArea').style.animation = 'fadeUp 0.35s ease';
  });
}

function selectAnswer(idx, clickedBtn, question) {
  if (state.answered) return;
  state.answered = true;
  const labels = ['A', 'B', 'C', 'D', 'E'];
  const userAnswer = labels[idx];
    // 支援數字答案(1-4)和字母答案(A-D)
    const _numberToLetter = {'1':'A', '2':'B', '3':'C', '4':'D', '5':'E'};
    const correctNorm = _numberToLetter[String(question.correct_answer)] || String(question.correct_answer);
  const correct = question.correct_answer;
  const isCorrect = userAnswer === correctNorm;
  // PATCHED_SHOW_NUMBERS: 把答案字母轉成數字顯示
  const _letterToNumber = {A:'(1)', B:'(2)', C:'(3)', D:'(4)', E:'(5)'};
  const correctDisplay = _letterToNumber[correct] || correct;
  const timeSpent = Math.round((Date.now() - state.questionStartTime) / 1000);

  // 暫存答案 (mark_action 留待 nextQuestion 時補上)
  state.answers.push({
    question_id: question.id,
    answer: userAnswer,
    time_spent: timeSpent
    // mark_action 在 nextQuestion() 時根據 state.marks[question.id] 填入
  });

  // 即時計分
  if (isCorrect) state.correctCount++;
  else state.wrongCount++;
  document.getElementById('scCorrect').textContent = `✓ ${state.correctCount}`;
  document.getElementById('scWrong').textContent = `✗ ${state.wrongCount}`;

  // 標示選項顏色
  const optionBtns = document.querySelectorAll('.option-btn');
  optionBtns.forEach((btn, i) => {
    btn.disabled = true;
    if (labels[i] === correctNorm) {
      btn.classList.add('correct');
      btn.querySelector('.option-label').textContent = '✓';
    } else if (i === idx && !isCorrect) {
      btn.classList.add('wrong');
      btn.querySelector('.option-label').textContent = '✗';
    }
  });

  // 顯示對錯訊息
  const feedback = document.getElementById('answerFeedback');
  if (isCorrect) {
    feedback.className = 'answer-feedback correct-bg';
    document.getElementById('feedbackResult').innerHTML = `<span style="color:var(--success,#3FB950)">✓ 答對了!</span>`;
    document.getElementById('feedbackCorrect').textContent = '';
  } else {
    feedback.className = 'answer-feedback wrong-bg';
    document.getElementById('feedbackResult').innerHTML = `<span style="color:var(--error,#F85149)">✗ 答錯了</span>`;
    document.getElementById('feedbackCorrect').textContent = `正確答案:${correctDisplay}`;
  }
  feedback.classList.remove('hidden');

  // ★ Batch C: 顯示教材原解說 (如有)
  if (question.explanation && question.explanation.trim()) {
    document.getElementById('feedbackExplainText').textContent = question.explanation;
    document.getElementById('feedbackExplain').classList.remove('hidden');
  }

  // ★ Batch C: 同步顯示已存的收藏/精熟狀態(若這題之前標過,按鈕會 active)
  updateMarkButtons(question.id);

  const isLast = state.currentIdx >= state.questions.length - 1;
  document.getElementById('nextBtn').textContent = isLast ? '查看結果 →' : '下一題 →';
  show('quizActions');
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

  var content = '<div class="userexp-content">' + escapeHtml(exp.content).replace(/\n/g, '<br>') + '</div>';

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
}

// ★ Batch C: 收藏/精熟按鈕 toggle
async function toggleMark(type) {
  const qid = state.questions[state.currentIdx].id;
  const current = state.marks[qid];
  // 點同一個再點 → 取消;點另一個 → 切換
  let newType;
  if (current === type) newType = null;
  else newType = type;

  state.marks[qid] = newType;
  updateMarkButtons(qid);

  // 立刻 call API 同步(失敗也不阻塞使用者)
  try {
    await fetch('/api/mark-question', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        question_id: qid,
        mark_type: newType === null ? 'clear' : newType
      })
    });
  } catch (e) {
    console.warn('mark-question API 失敗', e);
  }
}

function updateMarkButtons(qid) {
  const cur = state.marks[qid];
  const favBtn = document.getElementById('btnFavorite');
  const masBtn = document.getElementById('btnMastered');
  favBtn.classList.toggle('active', cur === 'favorite');
  masBtn.classList.toggle('active', cur === 'mastered');
}

function nextQuestion() {
  // 把本題標記寫入 state.answers 最後一筆的 mark_action
  if (state.answers.length > 0) {
    const last = state.answers[state.answers.length - 1];
    const qid = state.questions[state.currentIdx].id;
    last.mark_action = state.marks[qid] || 'clear';
  }
  if (state.currentIdx >= state.questions.length - 1) submitQuiz();
  else showQuestion(state.currentIdx + 1);
}

async function submitQuiz() {
  stopTimer();
  hide('questionArea');
  show('loadingState');
  document.querySelector('#loadingState .loading-text').textContent = '計算成績中…';
  try {
    const res = await fetch('/api/quiz/submit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ session_id: state.sessionId, answers: state.answers })
    });
    const data = await res.json();
    hide('loadingState');
    showDone(data);
  } catch (e) {
    showError('提交失敗,請稍後再試。');
  }
}

function showDone(data) {
  show('quizDone');
  document.getElementById('doneScore').textContent = data.percentage + '%';
  document.getElementById('doneDetail').textContent = `答對 ${data.score} 題 / 共 ${data.total} 題`;
  document.getElementById('viewReportBtn').dataset.sessionId = data.session_id;
}

function viewReport() {
  window.location.href = `/report/${document.getElementById('viewReportBtn').dataset.sessionId}`;
}

function startTimer() {
  const el = document.getElementById('timer');
  state.timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    el.textContent = `${String(Math.floor(elapsed/60)).padStart(2,'0')}:${String(elapsed%60).padStart(2,'0')}`;
  }, 1000);
}

function stopTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
}

function confirmBack() {
  if (state.answers.length > 0) {
    if (confirm('確定要離開測驗?目前進度將不會儲存。')) {
      stopTimer();
      window.location.href = '/dashboard';
    }
  } else {
    window.location.href = '/dashboard';
  }
}

function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function showError(msg) {
  hide('loadingState');
  document.getElementById('quizBody').innerHTML = `
    <div class="loading-state">
      <div style="font-size:36px">⚠️</div>
      <p style="color:var(--error,#F85149);font-size:16px;text-align:center;padding:0 20px;white-space:pre-line">${msg}</p>
      <button class="btn-secondary" style="max-width:240px" onclick="window.location.href='/dashboard'">回到主控台</button>
    </div>`;
}

