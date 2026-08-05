import { DATA_PATHS } from './config.js';

async function fetchJson(path, errorMessage) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(errorMessage);
  return response.json();
}

export async function loadStudyData() {
  const [questions, solutionData] = await Promise.all([
    fetchJson(DATA_PATHS.questions, '题库数据无法加载。'),
    fetchJson(DATA_PATHS.solutions, '解说数据无法加载。'),
  ]);

  return {
    questions,
    solutions: new Map(solutionData.map((item) => [item.id, item])),
  };
}
