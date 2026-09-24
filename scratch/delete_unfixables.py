import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

deleted_count = 0

for s in data['subjects']:
    # filter out items that contain the placeholder string
    original_len = len(s['items'])
    s['items'] = [
        i for i in s['items']
        if '조건 누락</legend>' not in i.get('question', '')
    ]
    deleted_count += (original_len - len(s['items']))

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Successfully deleted {deleted_count} unfixable questions.')
