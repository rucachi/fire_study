import json
with open('scratch/theme-bank-head.json', 'r', encoding='utf-16') as f:
    db = json.load(f)
for s in db['subjects']:
    print(f"{s['id']} has {len(s['items'])} items.")
