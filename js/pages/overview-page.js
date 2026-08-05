import { isAnswerCorrect } from '../core/answers.js';
import { loadStudyData } from '../core/data.js';
import { escapeHtml } from '../core/format.js';
import { loadAnswerRecords, loadMarkedQuestions } from '../core/storage.js';

function questionLinks(items, status, markedQuestionIds) {
  if (!items.length) return '<p class="empty-status">暂无题目</p>';
  return `<div class="question-status-grid">${items.map((question) => {
    const isMarked = markedQuestionIds.has(question.id);
    return `<a class="question-status ${status}${isMarked ? ' is-marked' : ''}" href="index.html?question=${question.id}" aria-label="打开第 ${question.id} 题${isMarked ? '，已标记' : ''}"><span>${question.id}</span>${isMarked ? '<span class="status-mark" aria-hidden="true">&#9733;</span>' : ''}</a>`;
  }).join('')}</div>`;
}

export function initOverviewPage() {
  const view = document.querySelector('#overview-view');
  const totalCount = document.querySelector('#total-count');
  const unansweredCount = document.querySelector('#unanswered-count');
  const correctCount = document.querySelector('#correct-count');
  const incorrectCount = document.querySelector('#incorrect-count');
  const markedCount = document.querySelector('#marked-count');

  function render(questions, solutions) {
    const answerRecords = loadAnswerRecords();
    const markedQuestionIds = loadMarkedQuestions();
    const grouped = { unanswered: [], correct: [], incorrect: [] };

    questions.forEach((question) => {
      const record = answerRecords[question.id];
      if (!record?.answers.length) grouped.unanswered.push(question);
      else if (isAnswerCorrect(record.answers, solutions.get(question.id))) grouped.correct.push(question);
      else grouped.incorrect.push(question);
    });

    totalCount.textContent = questions.length;
    unansweredCount.textContent = grouped.unanswered.length;
    correctCount.textContent = grouped.correct.length;
    incorrectCount.textContent = grouped.incorrect.length;
    const markedQuestions = questions.filter((question) => markedQuestionIds.has(question.id));
    markedCount.textContent = markedQuestions.length;
    view.innerHTML = [
      ['已标记', 'marked', markedQuestions, '稍后重点查看的题目'],
      ['未作答', 'pending', grouped.unanswered, '尚未开始的题目'],
      ['答错', 'incorrect', grouped.incorrect, '建议优先复习'],
      ['答对', 'correct', grouped.correct, '已掌握的题目'],
    ].map(([title, status, items, description]) => `
      <section class="status-list ${status}" aria-labelledby="${status}-title">
        <header><div><h2 id="${status}-title">${title}</h2><p>${description}</p></div><strong>${items.length} 题</strong></header>
        ${questionLinks(items, status, markedQuestionIds)}
      </section>`).join('');
  }

  loadStudyData()
    .then(({ questions, solutions }) => render(questions, solutions))
    .catch((error) => {
      view.innerHTML = `<p class="error">${escapeHtml(error.message)} 请通过本地 Web 服务器打开此网站。</p>`;
    });
}
