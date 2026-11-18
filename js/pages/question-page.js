import { isAnswerCorrect, refreshAnswerRecords } from '../core/answers.js';
import { EXAM } from '../core/config.js';
import { loadStudyData } from '../core/data.js';
import { displayedAnswer, displayedOptionLabel, escapeHtml, formatExplanation } from '../core/format.js';
import {
  clearAnswerRecords,
  loadAnswerRecords,
  loadMarkedQuestions,
  loadMemorizationMode,
  saveAnswerRecords,
  saveMarkedQuestions,
  saveMemorizationMode,
} from '../core/storage.js';

const LEGACY_AMBIGUOUS_QUESTIONS = new Set([64, 85, 119]);

function normalizedAnswer(value) {
  return String(value || '').split('+').filter(Boolean).sort().join('+');
}

function reviewNotices(solution, choices) {
  if (!solution) return '';
  const notices = [];
  if (solution.pdfAnswer && normalizedAnswer(solution.answer) !== normalizedAnswer(solution.pdfAnswer)) {
    notices.push(
      '<p class="review-notice"><strong>独立答案与 PDF 不同：</strong>'
      + '本站独立判断为 <strong>' + displayedAnswer(solution.answer, choices) + '</strong>，'
      + '源 PDF 标注为 <strong>' + displayedAnswer(solution.pdfAnswer, choices) + '</strong>。'
      + '本题按本站的独立答案判分。</p>',
    );
  }
  if (solution.needsConfirmation || (EXAM.slug === 'aws-cip' && LEGACY_AMBIGUOUS_QUESTIONS.has(solution.id))) {
    notices.push('<p class="review-notice ambiguity-notice"><strong>需人工确认：</strong>题干或选项存在解释空间；当前答案为独立判断，建议结合官方资料再确认。</p>');
  }
  return notices.join('');
}

function currentId() {
  const legacyMatch = location.hash.match(/^#\/question\/(\d+)$/);
  return Number(new URLSearchParams(location.search).get('question')) || Number(legacyMatch?.[1]) || 1;
}

function questionUrl(id) {
  return `?question=${id}`;
}

function createQuestionOrder(question, choiceOrders) {
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

export function initQuestionPage() {
  const view = document.querySelector('#question-view');
  const search = document.querySelector('#question-search');
  const position = document.querySelector('#current-position');
  const total = document.querySelector('#total-count');
  const answeredCount = document.querySelector('#answered-count');
  const correctCount = document.querySelector('#correct-count');
  const clearAnswers = document.querySelector('#clear-answers');
  const memorizationToggle = document.querySelector('#memorization-mode');
  const state = {
    questions: [],
    solutions: new Map(),
    answerRecords: loadAnswerRecords(),
    markedQuestionIds: loadMarkedQuestions(),
    choiceOrders: new Map(),
    memorizationMode: loadMemorizationMode(),
  };
  memorizationToggle.checked = state.memorizationMode;

  function updateAnsweredCount() {
    const records = Object.values(state.answerRecords);
    answeredCount.textContent = records.filter((record) => record.answers.length > 0).length;
    correctCount.textContent = records.filter((record) => record.isCorrect === true).length;
  }

  function render() {
    const requestedId = currentId();
    const question = state.questions.find((item) => item.id === requestedId) ?? state.questions[0];
    if (!question) return;

    if (requestedId !== question.id) location.replace(questionUrl(question.id));
    const currentIndex = state.questions.findIndex((item) => item.id === question.id);
    const previous = state.questions[currentIndex - 1];
    const next = state.questions[currentIndex + 1];
    const solution = state.solutions.get(question.id);
    // 背题版只改变显示，不将正确答案写入实际作答记录。
    const record = state.memorizationMode
      ? { answers: (solution?.answer || '').split('+').map((label) => label.trim()).filter(Boolean), isCorrect: solution ? true : null }
      : state.answerRecords[question.id] || { answers: [], isCorrect: null };
    const recordedAnswers = new Set(record.answers);
    const isMarked = state.markedQuestionIds.has(question.id);
    const displayedChoices = createQuestionOrder(question, state.choiceOrders);
    const reviewNotice = reviewNotices(solution, displayedChoices);
    position.textContent = currentIndex + 1;
    updateAnsweredCount();
    search.value = question.id;
    document.title = `第 ${question.id} 题｜${EXAM.title}`;

    const englishFirst = EXAM.primaryLanguage === 'en';
    const secondaryLanguage = englishFirst ? 'zh-CN' : 'en';
    const primaryCategory = englishFirst ? question.category : question.categoryZh;
    const secondaryCategory = englishFirst ? question.categoryZh : question.category;
    const primaryChoices = displayedChoices.map((choice, index) => `
      <button class="choice${recordedAnswers.has(choice.label) ? ' user-selected' : ''}${record.isCorrect === true ? ' user-correct' : record.isCorrect === false ? ' user-incorrect' : ''}" type="button" data-answer="${choice.label}" aria-pressed="${recordedAnswers.has(choice.label)}" ${state.memorizationMode ? 'disabled' : ''}>
        <span class="choice-label">${displayedOptionLabel(index)}</span>
        <p lang="${EXAM.primaryLanguage}">${escapeHtml(englishFirst ? choice.text : choice.textZh)}</p>
      </button>`).join('');
    const secondaryChoices = displayedChoices.map((choice, index) => `<li><strong>${displayedOptionLabel(index)}.</strong> ${escapeHtml(englishFirst ? choice.textZh : choice.text)}</li>`).join('');
    const answerFeedback = state.memorizationMode
      ? '<p class="answer-feedback">背题版：直接显示题库答案，不计入作答记录。</p>'
      : record.isCorrect === true
      ? '<p class="answer-feedback correct">本题回答正确，已记录。</p>'
      : record.isCorrect === false
        ? '<p class="answer-feedback incorrect">当前选择不正确，已记录；可继续增减选项。</p>'
        : '';
    const result = solution ? [
      `<details class="result" aria-label="答案"${state.memorizationMode ? ' open' : ''}>`,
      '<summary>查看答案与解析</summary>',
      '<div class="result-content">',
      '<div class="answer-line"><span>答案</span><strong>' + displayedAnswer(solution.answer, displayedChoices) + '</strong></div>',
      reviewNotice,
      '<p class="explanation-text">' + formatExplanation(solution.explanationZh, displayedChoices) + '</p>',
      '</div></details>',
    ].join('') : '';

    view.innerHTML = `
      <article class="question-card">
        <header class="question-head">
          <div class="eyebrow">
            <div class="question-meta">
              <span>第 ${question.id} 题</span>
              ${primaryCategory ? `<span class="badge" lang="${EXAM.primaryLanguage}">${escapeHtml(primaryCategory)}</span>` : ''}
            </div>
            <button class="mark-question${isMarked ? ' is-marked' : ''}" type="button" data-mark-question aria-pressed="${isMarked}" aria-label="${isMarked ? '取消标记' : '标记'}第 ${question.id} 题">
              <span class="mark-icon" aria-hidden="true">${isMarked ? '&#9733;' : '&#9734;'}</span>
              <span>${isMarked ? '已标记' : '标记此题'}</span>
            </button>
          </div>
          <h1 lang="${EXAM.primaryLanguage}">${escapeHtml(englishFirst ? question.prompt : question.promptZh)}</h1>
        </header>
        <section class="choices" aria-label="${englishFirst ? '英文' : '中文'}选项">${primaryChoices}</section>
        ${answerFeedback}
        <details>
          <summary>${englishFirst ? '显示中文题目与选项' : '显示英文原题与选项'}</summary>
          <div class="translation" lang="${secondaryLanguage}">
            ${secondaryCategory ? `<h2>${escapeHtml(secondaryCategory)}</h2>` : ''}
            <p>${escapeHtml(englishFirst ? question.promptZh : question.prompt)}</p>
            <ul>${secondaryChoices}</ul>
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
      const willBeMarked = !state.markedQuestionIds.has(question.id);
      if (willBeMarked) state.markedQuestionIds.add(question.id);
      else state.markedQuestionIds.delete(question.id);
      saveMarkedQuestions(state.markedQuestionIds);
      markButton.classList.toggle('is-marked', willBeMarked);
      markButton.setAttribute('aria-pressed', String(willBeMarked));
      markButton.setAttribute('aria-label', `${willBeMarked ? '取消标记' : '标记'}第 ${question.id} 题`);
      markButton.querySelector('.mark-icon').innerHTML = willBeMarked ? '&#9733;' : '&#9734;';
      markButton.lastElementChild.textContent = willBeMarked ? '已标记' : '标记此题';
    });

    view.querySelectorAll('[data-answer]').forEach((choice) => {
      choice.addEventListener('click', () => {
        if (state.memorizationMode) return;
        const answers = new Set(state.answerRecords[question.id]?.answers || []);
        const label = choice.dataset.answer;
        if (answers.has(label)) answers.delete(label);
        else answers.add(label);

        if (answers.size > 0) {
          const selected = [...answers].sort();
          state.answerRecords[question.id] = {
            answers: selected,
            isCorrect: isAnswerCorrect(selected, solution),
          };
        } else {
          delete state.answerRecords[question.id];
        }
        saveAnswerRecords(state.answerRecords);
        render();
      });
    });
  }

  search.addEventListener('change', () => {
    const question = state.questions.find((item) => item.id === Number(search.value));
    if (question) location.href = questionUrl(question.id);
    else search.value = currentId();
  });

  memorizationToggle.addEventListener('change', () => {
    state.memorizationMode = memorizationToggle.checked;
    saveMemorizationMode(state.memorizationMode);
    render();
  });

  clearAnswers.addEventListener('click', () => {
    if (!Object.keys(state.answerRecords).length) return;
    if (!window.confirm('确定要清空全部题目的作答记录吗？此操作无法恢复。')) return;
    state.answerRecords = {};
    clearAnswerRecords();
    render();
  });

  window.addEventListener('hashchange', render);

  loadStudyData()
    .then(({ questions, solutions }) => {
      state.questions = questions;
      state.solutions = solutions;
      refreshAnswerRecords(state.answerRecords, state.solutions);
      saveAnswerRecords(state.answerRecords);
      total.textContent = state.questions.length;
      render();
    })
    .catch((error) => {
      view.innerHTML = '<p class="error">' + escapeHtml(error.message) + ' 请通过本地 Web 服务器打开此网站。</p>';
    });
}
