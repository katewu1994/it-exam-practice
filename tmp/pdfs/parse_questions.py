import re
from pathlib import Path

page_dir = Path("tmp/pdfs/pages")
pages = [path.read_text(encoding="utf-8") for path in sorted(page_dir.glob("*.txt"))]
raw = "\n".join(pages)
raw = re.sub(r"店铺：学习小店66\s*店铺：学习小店66\s*https://shop63989109\.taobao\.com/", "", raw)
raw = re.sub(r"Amazon Web Services - AIP-C01", "", raw)
raw = re.sub(r"\n\s*[ABCD]\.\s*\n", "\n", raw)
Path("tmp/pdfs/aip_clean.txt").write_text(raw, encoding="utf-8")
pattern = re.compile(r"Question #:(\d+)(?: - \[(.*?)\])?(.*?)(?=Question #:\d+|\Z)", re.S)
items=[]
for number, category, content in pattern.findall(raw):
    answer = re.search(r"\bAnswer:\s*([A-E](?:\s+[A-E])*)\b", content)
    stem_options = content[:answer.start()] if answer else content
    items.append((int(number), category or "Uncategorized in source", stem_options.strip(), answer.group(1) if answer else "?"))
lines=[]
for number, category, question, answer in items:
    lines += [f"## Q{number} [{category}]", question, f"ORIGINAL ANSWER: {answer}", ""]
Path("tmp/pdfs/questions.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"Found {len(items)} questions")
print("Missing answers:", [n for n,_,_,a in items if a=='?'])
