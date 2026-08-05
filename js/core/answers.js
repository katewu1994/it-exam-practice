export function isAnswerCorrect(answers, solution) {
  const selected = [...answers].sort();
  const expected = (solution?.answer || '').split('+').filter(Boolean).sort();
  return selected.length === expected.length && selected.every((answer, index) => answer === expected[index]);
}

export function refreshAnswerRecords(answerRecords, solutions) {
  Object.entries(answerRecords).forEach(([id, record]) => {
    record.isCorrect = isAnswerCorrect(record.answers, solutions.get(Number(id)));
  });
}
