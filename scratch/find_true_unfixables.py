import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

unfixables = []

for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '<fieldset' not in q and '<img' not in q and '![' not in q:
            # specifically looking for "다음 ( ) 안에" etc.
            if '다음' in q and '(' in q and ')' in q:
                if any(x in q for x in ['알맞은', '들어갈', '내용', '기준']):
                    if len(i.get('options', [])) > 0:
                        exp = i.get('explanation', '')
                        if not exp.strip():
                            unfixables.append(q)

with open('scratch/true_unfixables.txt', 'w', encoding='utf-8') as f:
    for u in unfixables:
        f.write(u.replace('\n', ' ') + '\n')

print(f'Found {len(unfixables)} true unfixables.')
