import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

boxes_fixed = 0

for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '<fieldset' not in q and '<img' not in q and '![' not in q:
            lines = [l for l in q.split('\n') if l.strip()]
            if len(lines) <= 2 and ('(' in q and ')' in q):
                if any(x in q for x in ['다음', '아래', '알맞은', '들어갈', '내용', '기준']):
                    # Check if it has real options (i.e. not an essay question)
                    if len(i.get('options', [])) > 0:
                        exp = i.get('explanation', '')
                        if exp:
                            clean_exp = exp.strip().replace('\n', '<br>')
                            new_q = q + f'\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px;"><legend>조건</legend>{clean_exp}</fieldset>'
                            i['question'] = new_q
                            boxes_fixed += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Fixed {boxes_fixed} additional missing condition boxes.')
