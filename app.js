const view = document.querySelector('#question-view');
const search = document.querySelector('#question-search');
const position = document.querySelector('#current-position');
const total = document.querySelector('#total-count');
const answeredCount = document.querySelector('#answered-count');
const correctCount = document.querySelector('#correct-count');
const clearAnswers = document.querySelector('#clear-answers');
const ANSWER_STORAGE_KEY = 'aws-aip-c01-answer-records-v1';

let questions = [];
let solutions = new Map();
let answerRecords = loadAnswerRecords();

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

function formatExplanation(value) {
  return escapeHtml(value)
    .replace(/^【([^】]+)】/gm, '<strong>【$1】</strong>')
    .replace(/^• /gm, '&bull; ')
    .replaceAll('\n', '<br>');
}

function parseReviewExplanations(markdown) {
  const sections = new Map();
  const matches = markdown.matchAll(/^## 第 (\d+) 题[^\n]*\n([\s\S]*?)(?=^## 第 \d+ 题|(?![\s\S]))/gm);

  for (const match of matches) {
    const explanation = match[2]
      .split('\n')
      .filter((line) => !/^- (原 PDF 答案|复核答案|题干关键词)：/.test(line))
      .map((line) => line
        .replace(/^- 关键词如何指向正确答案：/, '【核心判断】')
        .replace(/^### 为什么不是其他选项$/, '【其他选项】')
        .replace(/^- /, '• ')
        .replace(/^最终结论：/, '【结论】'))
      .join('\n')
      .trim();
    sections.set(Number(match[1]), explanation);
  }

  return sections;
}

function parseSiteQuestionMap(text) {
  const mapping = new Map();
  for (const match of text.matchAll(/^site\s+(\d+)\s+-> source\s+(\d+)/gm)) {
    mapping.set(Number(match[1]), Number(match[2]));
  }
  return mapping;
}

function questionUrl(id) {
  return `?question=${id}`;
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
  position.textContent = currentIndex + 1;
  updateAnsweredCount();
  search.value = question.id;
  document.title = `第 ${question.id} 题｜AWS AIP-C01 中文题库`;

  const chineseChoices = question.choices.map((choice) => `
    <button class="choice${recordedAnswers.has(choice.label) ? ' user-selected' : ''}${record.isCorrect === true ? ' user-correct' : record.isCorrect === false ? ' user-incorrect' : ''}" type="button" data-answer="${choice.label}" aria-pressed="${recordedAnswers.has(choice.label)}">
      <span class="choice-label">${choice.label}</span>
      <p>${escapeHtml(choice.textZh)}</p>
    </button>`).join('');
  const englishChoices = question.choices.map((choice) => `<li><strong>${choice.label}.</strong> ${escapeHtml(choice.text)}</li>`).join('');
  const answerFeedback = record.isCorrect === true
    ? '<p class="answer-feedback correct">本题回答正确，已记录。</p>'
    : record.isCorrect === false
      ? '<p class="answer-feedback incorrect">当前选择不正确，已记录；可继续增减选项。</p>'
      : '';
  const reviewNotices = {
    53: '<p class="review-notice"><strong>本轮复核更新：</strong>源 PDF 此题答案仅列 A、D，但题干要求选择三项；站点已按复核结果使用 <strong>A + D + F</strong>。</p>',
    64: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题的选项与题干约束存在解释空间；当前答案为独立判断，暂不将其视为完全确定的结论。</p>',
    85: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题选项的能力边界与组合条件表述不够严谨；当前答案保留为独立判断，建议结合官方题源再确认。</p>',
    119: '<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>本题候选方案均有部分合理性，题干未充分给出取舍条件；当前答案属于暂定判断。</p>',
  };
  const reviewNotice = reviewNotices[question.id] || '';
  const result = solution ? [
    '<details class="result" aria-label="答案">',
    '<summary>查看答案与解析</summary>',
    '<div class="result-content">',
    '<div class="answer-line"><span>答案</span><strong>' + solution.answer + '</strong></div>',
    reviewNotice,
    '<p class="explanation-text">' + formatExplanation(solution.explanationZh) + '</p>',
    '</div></details>'
  ].join('') : '';

  view.innerHTML = `
    <article class="question-card">
      <header class="question-head">
        <div class="eyebrow">
          <span>第 ${question.id} 题</span>
          ${question.categoryZh ? `<span class="badge">${escapeHtml(question.categoryZh)}</span>` : ''}
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
  fetch("pdf/AIP-C01_128题_独立复核分析.md?v=expanded-explanations-20260803").then((response) => {
    if (!response.ok) throw new Error("逐题复核资料无法加载。");
    return response.text();
  }),
  fetch("tmp/pdfs/site_question_map.txt?v=expanded-explanations-20260803").then((response) => {
    if (!response.ok) throw new Error("题目映射资料无法加载。");
    return response.text();
  }),
])
  .then(([questionData, solutionData, reviewMarkdown, mapText]) => {
    questions = questionData;
    solutions = new Map(solutionData.map((item) => [item.id, item]));
    const reviewExplanations = parseReviewExplanations(reviewMarkdown);
    const siteQuestionMap = parseSiteQuestionMap(mapText);
    solutions.forEach((solution, id) => {
      const sourceId = siteQuestionMap.get(id);
      const reviewExplanation = reviewExplanations.get(sourceId);
      // 已独立修正过答案的题目不采用原 PDF 的复核文本，避免解释与当前答案冲突。
      if (reviewExplanation && solution.answer === solution.pdfAnswer) {
        solution.explanationZh = reviewExplanation;
      }
    });
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
