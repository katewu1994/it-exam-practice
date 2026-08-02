import re
from pathlib import Path

text = Path('tmp/pdfs/questions.txt').read_text(encoding='utf-8')
blocks = re.split(r'(?=^## Q\d+)', text, flags=re.M)
for block in blocks:
    header = re.match(r'## Q(\d+).*?\n', block)
    if not header:
        continue
    body = block[header.end():].split('Which solution', 1)[0].split('Which combination', 1)[0]
    body = re.sub(r'\s+', ' ', body).strip()
    answer = re.search(r'ORIGINAL ANSWER: (.+)', block)
    print(f"{header.group(1):>3} | {answer.group(1) if answer else '?':<5} | {body[:360]}")
