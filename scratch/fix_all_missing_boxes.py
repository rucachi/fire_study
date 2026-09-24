import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '다음' in q and '(' in q and ')' in q and '내용' in q:
            if '<img' not in q and '![' not in q and 'fieldset' not in q:
                lines = q.split('\n')
                if len(lines) < 4 and '들어갈' in q:
                    exp = i.get('explanation', '')
                    if exp:
                        # Append the explanation text as a condition box to the question
                        # We use the full explanation since it usually contains the law text.
                        # We strip any extra newlines
                        clean_exp = exp.strip().replace('\n', '<br>')
                        new_q = q + f'\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px;"><legend>조건</legend>{clean_exp}</fieldset>'
                        i['question'] = new_q
                        count += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Fixed {count} missing condition boxes.')
