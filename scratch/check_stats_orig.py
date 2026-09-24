import json
with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    db = json.load(f)
for s in db['subjects']:
    print(f"{s.get('id')} has {len(s.get('items', []))} items.")
