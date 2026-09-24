import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['subjects']:
    for i in s['items']:
        if i['id'] == 'theme-4-fire-electrical-facilities-0355':
            with open('scratch/q73_output.txt', 'w', encoding='utf-8') as out:
                out.write(i.get('question'))
            break
