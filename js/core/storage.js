import { STORAGE_KEYS } from './config.js';

export function loadAnswerRecords() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.answers) || '{}');
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

export function saveAnswerRecords(answerRecords) {
  localStorage.setItem(STORAGE_KEYS.answers, JSON.stringify(answerRecords));
}

export function clearAnswerRecords() {
  localStorage.removeItem(STORAGE_KEYS.answers);
}

export function loadMemorizationMode() {
  try {
    return localStorage.getItem(STORAGE_KEYS.memorizationMode) === 'true';
  } catch {
    return false;
  }
}

export function saveMemorizationMode(enabled) {
  localStorage.setItem(STORAGE_KEYS.memorizationMode, String(enabled));
}

export function loadMarkedQuestions() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.markedQuestions) || '[]');
    if (!Array.isArray(stored)) return new Set();
    return new Set(stored.filter((id) => Number.isInteger(id) && id > 0));
  } catch {
    return new Set();
  }
}

export function saveMarkedQuestions(markedQuestionIds) {
  localStorage.setItem(
    STORAGE_KEYS.markedQuestions,
    JSON.stringify([...markedQuestionIds].sort((first, second) => first - second)),
  );
}
