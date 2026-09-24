import json

db = json.load(open('theme-bank.json', encoding='utf-8'))
for s in db['subjects']:
    for i in s['items']:
        opts = i.get('options', [])
        if len(opts) > 4:
            print(f"Q: {i['question'][:30]}... Opts count: {len(opts)}")
