import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


SOURCE = Path('data/questions-en.json')
OUTPUT = Path('data/questions-zh.json')
ENDPOINT = 'https://translate.googleapis.com/translate_a/single'


def translate_fields(fields: list[str]) -> list[str]:
    marked = '\n'.join(f'[[FIELD{index}]] {text}' for index, text in enumerate(fields))
    params = urllib.parse.urlencode({
        'client': 'gtx', 'sl': 'en', 'tl': 'zh-CN', 'dt': 't', 'q': marked,
    })
    with urllib.request.urlopen(f'{ENDPOINT}?{params}', timeout=30) as response:
        payload = json.load(response)
    translated = ''.join(part[0] for part in payload[0])
    parts = re.split(r'\[\[FIELD(\d+)\]\]\s*', translated)
    values = {}
    for index in range(1, len(parts), 2):
        values[int(parts[index])] = parts[index + 1].strip()
    if len(values) != len(fields):
        raise ValueError(f'Could not preserve all field boundaries: {translated[:300]!r}')
    return [values[index] for index in range(len(fields))]


def main() -> None:
    questions = json.loads(SOURCE.read_text(encoding='utf-8'))
    translated_questions = []
    if OUTPUT.exists():
        translated_questions = json.loads(OUTPUT.read_text(encoding='utf-8'))
    completed = {question['id'] for question in translated_questions}
    for position, question in enumerate(questions, start=1):
        if question['id'] in completed:
            continue
        fields = [question['category'], question['prompt'], *(choice['text'] for choice in question['choices'])]
        try:
            translations = translate_fields(fields)
        except Exception as error:
            print(f'Question {question["id"]}: splitting translation ({error})', flush=True)
            translations = [translate_fields([field])[0] if field else '' for field in fields]
        translated_questions.append({
            **question,
            'categoryZh': translations[0],
            'promptZh': translations[1],
            'choices': [
                {**choice, 'textZh': translations[index + 2]}
                for index, choice in enumerate(question['choices'])
            ],
        })
        translated_questions.sort(key=lambda item: item['id'])
        OUTPUT.write_text(json.dumps(translated_questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Translated {position}/{len(questions)} (question {question["id"]})', flush=True)
        time.sleep(0.15)
    OUTPUT.write_text(json.dumps(translated_questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
