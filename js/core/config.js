export const DATA_VERSION = 'dual-exams-20261118';

const EXAMS = {
  'aws-cip': {
    slug: 'aws-cip',
    code: 'AIP-C01',
    title: 'AWS AIP-C01 中文题库',
    primaryLanguage: 'zh-CN',
    questionsPath: '../../data/questions-zh.json',
    solutionsPath: '../../data/solutions.json',
    storagePrefix: 'aws-aip-c01',
  },
  'ccar-f': {
    slug: 'ccar-f',
    code: 'CCAR-F',
    title: 'Claude CCAR-F 中文题库',
    primaryLanguage: 'en',
    questionsPath: '../../data/ccar-f/questions-zh.json',
    solutionsPath: '../../data/ccar-f/solutions.json',
    storagePrefix: 'anthropic-ccar-f',
  },
};

const examSlug = document.documentElement.dataset.exam;
export const EXAM = EXAMS[examSlug];

if (!EXAM) throw new Error(`未知题库：${examSlug || '未指定'}`);

function versionedDataUrl(path) {
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', DATA_VERSION);
  return url.href;
}

export const DATA_PATHS = {
  questions: versionedDataUrl(EXAM.questionsPath),
  solutions: versionedDataUrl(EXAM.solutionsPath),
};

export const STORAGE_KEYS = {
  answers: `${EXAM.storagePrefix}-answer-records-v1`,
  markedQuestions: `${EXAM.storagePrefix}-marked-questions-v1`,
  memorizationMode: `${EXAM.storagePrefix}-memorization-mode-v1`,
};
