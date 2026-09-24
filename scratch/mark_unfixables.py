import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
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
                            new_q = q + '\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px; background-color:#fff3f3;"><legend style="color:#d9534f; font-weight:bold;">조건 누락</legend>원본 데이터에서 누락되어 자동 복구할 수 없는 조건입니다. 정답을 참고하여 학습하세요.</fieldset>'
                            i['question'] = new_q
                            count += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Marked {count} true unfixables with a placeholder.')
