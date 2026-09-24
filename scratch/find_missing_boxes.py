import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = []
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '다음' in q and '(' in q and ')' in q and '내용' in q:
            if '<img' not in q and '![' not in q and 'fieldset' not in q:
                lines = q.split('\n')
                if len(lines) < 4 and '들어갈' in q:
                    issues.append({
                        'question': q,
                        'explanation': i.get('explanation', ''),
                        'options': i.get('options', [])
                    })

with open('scratch/missing_boxes.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)
