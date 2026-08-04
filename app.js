const view = document.querySelector('#question-view');
const search = document.querySelector('#question-search');
const position = document.querySelector('#current-position');
const total = document.querySelector('#total-count');
const answeredCount = document.querySelector('#answered-count');
const correctCount = document.querySelector('#correct-count');
const clearAnswers = document.querySelector('#clear-answers');
const ANSWER_STORAGE_KEY = 'aws-aip-c01-answer-records-v1';
const MARKED_STORAGE_KEY = 'aws-aip-c01-marked-questions-v1';

let questions = [];
let solutions = new Map();
let answerRecords = loadAnswerRecords();
let markedQuestionIds = loadMarkedQuestions();
// Keep one random order while the user is answering a question. A refresh or a
// new visit creates another order, so the correct answer cannot be memorized by position.
const choiceOrders = new Map();

function loadAnswerRecords() {
  try {
    const stored = JSON.parse(localStorage.getItem(ANSWER_STORAGE_KEY) || '{}');
    if (!stored || typeof stored !== 'object' || Array.isArray(stored)) return {};
    return Object.fromEntries(Object.entries(stored)
      .filter(([id, record]) => /^\d+$/.test(id) && (Array.isArray(record) || (record && typeof record === 'object' && Array.isArray(record.answers))))
      .map(([id, record]) => {
        const answers = Array.isArray(record) ? record : record.answers;
        return [id, {
          answers: [...new Set(answers.filter((answer) => typeof answer === 'string'))],
          isCorrect: typeof record?.isCorrect === 'boolean' ? record.isCorrect : null,
        }];
      }));
  } catch {
    return {};
  }
}

function saveAnswerRecords() {
  localStorage.setItem(ANSWER_STORAGE_KEY, JSON.stringify(answerRecords));
}

function loadMarkedQuestions() {
  try {
    const stored = JSON.parse(localStorage.getItem(MARKED_STORAGE_KEY) || '[]');
    if (!Array.isArray(stored)) return new Set();
    return new Set(stored.filter((id) => Number.isInteger(id) && id > 0));
  } catch {
    return new Set();
  }
}

function saveMarkedQuestions() {
  localStorage.setItem(MARKED_STORAGE_KEY, JSON.stringify([...markedQuestionIds].sort((a, b) => a - b)));
}

function updateAnsweredCount() {
  const records = Object.values(answerRecords);
  answeredCount.textContent = records.filter((record) => record.answers.length > 0).length;
  correctCount.textContent = records.filter((record) => record.isCorrect === true).length;
}

function currentId() {
  const legacyMatch = location.hash.match(/^#\/question\/(\d+)$/);
  return Number(new URLSearchParams(location.search).get("question")) || Number(legacyMatch?.[1]) || 1;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatExplanation(value, choices) {
  const optionLabels = new Map(choices.map((choice, index) => [choice.label, displayedOptionLabel(index)]));
  // 题库解析使用的是原始选项标签；选项随机排序后，需要把独立的 A-F
  // 同步换成当前页面上的显示标签。字母数字中的字符（例如 A2I）不会匹配。
  const explanationWithDisplayedLabels = String(value).replace(/(^|[^A-Za-z0-9])([A-F])(?=$|[^A-Za-z0-9])/gm, (match, prefix, label) => {
    return prefix + (optionLabels.get(label) || label);
  });

  return escapeHtml(explanationWithDisplayedLabels)
    .replace(/^【([^】]+)】/gm, '<strong>【$1】</strong>')
    .replace(/^• /gm, '&bull; ')
    .replaceAll('\n', '<br>');
}

function questionUrl(id) {
  return `?question=${id}`;
}

function choicesInRandomOrder(question) {
  if (!choiceOrders.has(question.id)) {
    const shuffled = [...question.choices];
    for (let index = shuffled.length - 1; index > 0; index -= 1) {
      const randomIndex = Math.floor(Math.random() * (index + 1));
      [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
    }
    choiceOrders.set(question.id, shuffled);
  }
  return choiceOrders.get(question.id);
}

function displayedOptionLabel(index) {
  return String.fromCharCode(65 + index);
}

function displayedAnswer(answer, choices) {
  return answer.split('+').map((label) => {
    const index = choices.findIndex((choice) => choice.label === label.trim());
    return index === -1 ? label.trim() : displayedOptionLabel(index);
  }).join(' + ');
}

function render() {
  const requestedId = currentId();
  const question = questions.find((item) => item.id === requestedId) ?? questions[0];
  if (!question) return;

  if (requestedId !== question.id) location.replace(questionUrl(question.id));
  const currentIndex = questions.findIndex((item) => item.id === question.id);
  const previous = questions[currentIndex - 1];
  const next = questions[currentIndex + 1];
  const solution = solutions.get(question.id);
  const record = answerRecords[question.id] || { answers: [], isCorrect: null };
  const recordedAnswers = new Set(record.answers);
  const isMarked = markedQuestionIds.has(question.id);
  const displayedChoices = choicesInRandomOrder(question);
  position.textContent = currentIndex + 1;
  updateAnsweredCount();
  search.value = question.id;
  document.title = `第 ${question.id} 题｜AWS AIP-C01 中文题库`;

  const chineseChoices = displayedChoices.map((choice, index) => `
    <button class="choice${recordedAnswers.has(choice.label) ? ' user-selected' : ''}${record.isCorrect === true ? ' user-correct' : record.isCorrect === false ? ' user-incorrect' : ''}" type="button" data-answer="${choice.label}" aria-pressed="${recordedAnswers.has(choice.label)}">
      <span class="choice-label">${displayedOptionLabel(index)}</span>
      <p>${escapeHtml(choice.textZh)}</p>
    </button>`).join('');
  const englishChoices = displayedChoices.map((choice, index) => `<li><strong>${displayedOptionLabel(index)}.</strong> ${escapeHtml(choice.text)}</li>`).join('');
  const answerFeedback = record.isCorrect === true
    ? '<p class="answer-feedback correct">本题回答正确，已记录。</p>'
    : record.isCorrect === false
      ? '<p class="answer-feedback incorrect">当前选择不正确，已记录；可继续增减选项。</p>'
      : '';
  const reviewNotices = {
    53: '<p class="review-notice"><strong>本轮复核更新：</strong>源 PDF 此题答案仅列两项，但题干要求选择三项；站点已按复核结果使用 <strong>' + displayedAnswer('A+D+F', displayedChoices) + '</strong>。</p>',
    64: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题的选项与题干约束存在解释空间；当前答案为独立判断，暂不将其视为完全确定的结论。</p>',
    85: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题选项的能力边界与组合条件表述不够严谨；当前答案保留为独立判断，建议结合官方题源再确认。</p>',
    119: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题候选方案均有部分合理性，题干未充分给出取舍条件；当前答案属于暂定判断。</p>',
  };
  const reviewNotice = reviewNotices[question.id] || '';
  const result = solution ? [
    '<details class="result" aria-label="答案">',
    '<summary>查看答案与解析</summary>',
    '<div class="result-content">',
    '<div class="answer-line"><span>答案</span><strong>' + displayedAnswer(solution.answer, displayedChoices) + '</strong></div>',
    reviewNotice,
    '<p class="explanation-text">' + formatExplanation(solution.explanationZh, displayedChoices) + '</p>',
    '</div></details>'
  ].join('') : '';

  view.innerHTML = `
    <article class="question-card">
      <header class="question-head">
        <div class="eyebrow">
          <div class="question-meta">
            <span>第 ${question.id} 题</span>
            ${question.categoryZh ? `<span class="badge">${escapeHtml(question.categoryZh)}</span>` : ''}
          </div>
          <button class="mark-question${isMarked ? ' is-marked' : ''}" type="button" data-mark-question aria-pressed="${isMarked}" aria-label="${isMarked ? '取消标记' : '标记'}第 ${question.id} 题">
            <span class="mark-icon" aria-hidden="true">${isMarked ? '&#9733;' : '&#9734;'}</span>
            <span>${isMarked ? '已标记' : '标记此题'}</span>
          </button>
        </div>
        <h1>${escapeHtml(question.promptZh)}</h1>
      </header>
      <section class="choices" aria-label="中文选项">${chineseChoices}</section>
      ${answerFeedback}
      <details>
        <summary>显示英文原题与选项</summary>
        <div class="english">
          ${question.category ? `<h2>${escapeHtml(question.category)}</h2>` : ''}
          <p>${escapeHtml(question.prompt)}</p>
          <ul>${englishChoices}</ul>
        </div>
      </details>
      ${result}
      <nav class="nav" aria-label="题目切换">
        <button type="button" data-target="${previous?.id ?? ''}" ${previous ? '' : 'disabled'}>← 上一题</button>
        <button type="button" data-target="${next?.id ?? ''}" ${next ? '' : 'disabled'}>下一题 →</button>
      </nav>
    </article>`;

  view.querySelectorAll('[data-target]').forEach((button) => {
    button.addEventListener('click', () => { location.href = questionUrl(button.dataset.target); });
  });

  const markButton = view.querySelector('[data-mark-question]');
  markButton.addEventListener('click', () => {
    const willBeMarked = !markedQuestionIds.has(question.id);
    if (willBeMarked) markedQuestionIds.add(question.id);
    else markedQuestionIds.delete(question.id);
    saveMarkedQuestions();
    markButton.classList.toggle('is-marked', willBeMarked);
    markButton.setAttribute('aria-pressed', String(willBeMarked));
    markButton.setAttribute('aria-label', `${willBeMarked ? '取消标记' : '标记'}第 ${question.id} 题`);
    markButton.querySelector('.mark-icon').innerHTML = willBeMarked ? '&#9733;' : '&#9734;';
    markButton.lastElementChild.textContent = willBeMarked ? '已标记' : '标记此题';
  });

  view.querySelectorAll('[data-answer]').forEach((choice) => {
    choice.addEventListener('click', () => {
      const answers = new Set(answerRecords[question.id]?.answers || []);
      const label = choice.dataset.answer;
      if (answers.has(label)) answers.delete(label);
      else answers.add(label);
      if (answers.size > 0) {
        const selected = [...answers].sort();
        const expected = (solution?.answer || '').split('+').filter(Boolean).sort();
        const isCorrect = selected.length === expected.length && selected.every((answer, index) => answer === expected[index]);
        answerRecords[question.id] = { answers: selected, isCorrect };
      } else {
        delete answerRecords[question.id];
      }
      saveAnswerRecords();
      render();
    });
  });
}

search.addEventListener('change', () => {
  const question = questions.find((item) => item.id === Number(search.value));
  if (question) location.href = questionUrl(question.id);
  else search.value = currentId();
});

clearAnswers.addEventListener('click', () => {
  if (!Object.keys(answerRecords).length) return;
  if (!window.confirm('确定要清空全部题目的作答记录吗？此操作无法恢复。')) return;
  answerRecords = {};
  localStorage.removeItem(ANSWER_STORAGE_KEY);
  render();
});

window.addEventListener('hashchange', render);

Promise.all([
  fetch("data/questions-zh.json?v=expanded-explanations-20260803").then((response) => {
    if (!response.ok) throw new Error("题库数据无法加载。");
    return response.json();
  }),
  fetch("data/solutions.json?v=expanded-explanations-20260803").then((response) => {
    if (!response.ok) throw new Error("解说数据无法加载。");
    return response.json();
  }),
])
  .then(([questionData, solutionData]) => {
    questions = questionData;
    solutions = new Map(solutionData.map((item) => [item.id, item]));
    Object.entries(answerRecords).forEach(([id, record]) => {
      const expected = (solutions.get(Number(id))?.answer || '').split('+').filter(Boolean).sort();
      const selected = [...record.answers].sort();
      record.isCorrect = selected.length === expected.length && selected.every((answer, index) => answer === expected[index]);
    });
    saveAnswerRecords();
    total.textContent = questions.length;
    render();
  })
  .catch((error) => { view.innerHTML = '<p class="error">' + escapeHtml(error.message) + ' 请通过本地 Web 服务器打开此网站。</p>'; });
