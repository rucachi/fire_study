import json

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

count = 0
with open('scratch/check_short_q.txt', 'w', encoding='utf-8') as out:
    for s in data['subjects']:
        for i in s['items']:
            q = i.get('question', '')
            exp = i.get('explanation', '')
            # If question has parens and is short, and explanation is long
            if '( )' in q and '### 그림' not in exp:
                q_lines = q.split('\n')
                if len(q_lines) < 4:
                    out.write(f"ID: {i.get('id')}\nQ: {q}\nOpts: {i.get('options')}\nExp: {exp}\n---\n")
                    count += 1
                    if count > 20: break

print(f"Found {count}")
