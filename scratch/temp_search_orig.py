import json

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

count = 0
with open('scratch/found_orig.txt', 'w', encoding='utf-8') as out:
    for s in data['subjects']:
        for i in s['items']:
            q = i.get('question', '')
            if '3종 연기감지기' in q or '설치기준 중 다음' in q:
                out.write(f"ID: {i.get('id')}\nQ: {q}\nOpts: {i.get('options')}\nExp: {i.get('explanation')}\n---\n")
                count += 1

print(f"Found {count} questions.")
