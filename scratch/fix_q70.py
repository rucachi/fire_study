import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '감지기의 형식승인 및 제품검사의 기술기준에 따라 단독경' in q:
            new_q = q + '\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px;"><legend>조건</legend>내장된 음향장치는 건전지의 성능이 저하되는 등의 상태를 음성 또는 음향으로 경보할 수 있어야 하며, 이 경우 음량은 감지기로부터 ( ⓐ )m 떨어진 위치에서 ( ⓑ )dB 이상, 음성 안내 멘트 또는 음향경보는 ( ⓒ )시간 동안 지속될 것</fieldset>'
            new_q = new_q.replace('단독경\n보형감지기의', '단독경보형감지기의')
            new_q = new_q.replace('들어갈 \n내용으로', '들어갈 내용으로')
            i['question'] = new_q
            print('Fixed question 70')
            break

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
