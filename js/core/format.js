export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export function displayedOptionLabel(index) {
  return String.fromCharCode(65 + index);
}

export function displayedAnswer(answer, choices) {
  return answer.split('+').map((label) => {
    const index = choices.findIndex((choice) => choice.label === label.trim());
    return index === -1 ? label.trim() : displayedOptionLabel(index);
  }).join(' + ');
}

export function formatExplanation(value, choices) {
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
