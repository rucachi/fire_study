import json
with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '다음' in q and ('()' in q or '( )' in q) and '<fieldset' not in q:
            if i.get('options') and len(i.get('options')) > 0:
                print(f"ID: {i.get('id')} - {q[:50]}")
