import json

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

with open('scratch/check_remaining.txt', 'w', encoding='utf-8') as out:
    for s in data['subjects']:
        for i in s['items']:
            q = i.get('question', '')
            if '73. 비상방송설비' in q or '75. 비상콘센트설비' in q or '73. 소방대상물의' in q:
                out.write(f"ID: {i['id']}\n")
                out.write(f"Q: {q}\n")
                out.write(f"EXP: {i.get('explanation')}\n")
                out.write("==========\n")
