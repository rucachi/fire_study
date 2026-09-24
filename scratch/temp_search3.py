import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('scratch/found_70.txt', 'w', encoding='utf-8') as out:
    for s in data['subjects']:
        for i in s['items']:
            q = i.get('question', '')
            if '설치기준 중 다음' in q:
                out.write(f"ID: {i.get('id')}\nQ: {q}\nOpts: {i.get('options')}\nExp: {i.get('explanation')}\n---\n")
