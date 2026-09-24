import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '<fieldset' not in q and '<img' not in q and '![' not in q:
            if '(' in q and ')' in q:
                if any(x in q for x in ['다음', '아래', '알맞은', '들어갈', '내용', '기준']):
                    if len(i.get('options', [])) > 0:
                        exp = i.get('explanation', '')
                        if not exp:
                            count += 1
                            print(f"Q: {q.strip()}")

print(f'Unfixable candidates (no explanation): {count}')
