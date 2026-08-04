import argparse
import json
import re
from pathlib import Path

import pdfplumber


SOURCE = Path(__file__).resolve().parent / 'pdf' / 'AIP-C01 128题.pdf'
OUTPUT = Path('data/questions-en.json')


def normalize(text: str) -> str:
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'店铺：学习小店66\s*https://shop63989109\.taobao\.com/', '', text)
    text = re.sub(r'Amazon Web Services - AIP-C01\s*', '', text)
    text = re.sub(r'([A-Za-z])-\n([a-z])', r'\1\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description='Extract questions from an AIP-C01 PDF.')
    parser.add_argument('source', nargs='?', type=Path, default=SOURCE)
    parser.add_argument('output', nargs='?', type=Path, default=OUTPUT)
    args = parser.parse_args()

    with pdfplumber.open(str(args.source)) as pdf:
        pages = [
            page.filter(
                lambda item: item.get('non_stroking_color') == (0.0, 0.0, 0.0)
            ).extract_text() or ''
            for page in pdf.pages
        ]
    document = '\n'.join(pages)
    document = normalize(document)
    matches = list(re.finditer(r'Question #:\s*(\d+)(?:\s*-\s*\[([^\]]+)\])?', document))
    questions = []

    for index, match in enumerate(matches):
        segment = document[match.end():matches[index + 1].start() if index + 1 < len(matches) else None]
        question_text = re.split(r'\nExplanation\b', segment, maxsplit=1)[0].strip()
        lines = [line.strip() for line in question_text.splitlines() if line.strip()]
        choices = []
        body = []
        current_choice = None
        for line in lines:
            marker = re.match(r'^([A-F])\.\s*(.*)', line)
            if marker:
                choice_text = marker.group(2).strip()
                # A page break can leave a bare choice marker at the bottom of
                # one page before the full choice begins on the next page.
                if not choice_text:
                    current_choice = None
                    continue
                current_choice = {'label': marker.group(1), 'text': choice_text}
                choices.append(current_choice)
            elif current_choice:
                current_choice['text'] += ' ' + line
            else:
                body.append(line)
        questions.append({
            'id': int(match.group(1)),
            'category': match.group(2) or '',
            'prompt': ' '.join(body),
            'choices': choices,
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Extracted {len(questions)} questions')
    for question in questions:
        if len(question['choices']) != 4:
            print(f"Question {question['id']}: {len(question['choices'])} choices")


if __name__ == '__main__':
    main()
