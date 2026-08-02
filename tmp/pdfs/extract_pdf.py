from pathlib import Path
from pypdf import PdfReader

source = Path("AIP-C01 128题.pdf")
output = Path("tmp/pdfs/pages")
output.mkdir(parents=True, exist_ok=True)
reader = PdfReader(source)
for number, page in enumerate(reader.pages, start=1):
    (output / f"{number:03d}.txt").write_text(page.extract_text() or "", encoding="utf-8")
print(f"Extracted {len(reader.pages)} pages to {output}")
