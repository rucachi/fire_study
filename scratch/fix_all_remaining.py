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
                        if exp:
                            clean_exp = exp.strip().replace('\n', '<br>')
                            new_q = q + f'\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px;"><legend>조건</legend>{clean_exp}</fieldset>'
                            i['question'] = new_q
                            count += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Fixed {count} more by removing line count restriction.')
