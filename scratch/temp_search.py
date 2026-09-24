import json

with open('theme-bank-original.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '3종 연기감지기' in q:
            print(f"Q: {q}")
            print(f"Explanation: {i.get('explanation', '')}")
            print("---")
            count += 1

print(f"Found {count} questions.")
