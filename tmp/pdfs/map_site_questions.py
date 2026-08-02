import json
import re
from difflib import SequenceMatcher
from pathlib import Path

site_questions = json.loads(Path('data/questions-en.json').read_text(encoding='utf-8'))
source = Path('tmp/pdfs/questions.txt').read_text(encoding='utf-8')
blocks = re.split(r'(?=^## Q\d+)', source, flags=re.M)
source_questions = []
for block in blocks:
    match = re.match(r'^## Q(\d+) \[.*?\]\n', block)
    if not match:
        continue
    prompt = re.split(r'Which (?:solution|combination).*?\?\s*', block, maxsplit=1, flags=re.S)[0]
    prompt = prompt[match.end():]
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    answer = re.search(r'^ORIGINAL ANSWER: (.+)$', block, flags=re.M).group(1).strip()
    source_questions.append((int(match.group(1)), prompt, answer))

def norm(text):
    return re.sub(r'[^a-z0-9]+', '', text.lower())

for question in site_questions:
    target = norm(question['prompt'])
    scores = sorted(((SequenceMatcher(None, target, norm(prompt)).ratio(), n, answer) for n, prompt, answer in source_questions), reverse=True)
    best, second = scores[:2]
    print(f"site {question['id']:3} -> source {best[1]:3} ({best[0]:.3f}; next {second[1]} {second[0]:.3f}) answer {best[2]}")
