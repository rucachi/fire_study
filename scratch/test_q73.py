import json
import re

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

for s in data['subjects']:
    for i in s['items']:
        if i['id'] == 'theme-4-fire-electrical-facilities-0355':
            q = i.get('question', '')
            match = re.search(r'\n\s*[①❶]', q)
            print("MATCH:", match)
            if match:
                idx = match.start()
                new_q = q[:idx] + "\n\n[INJECTED]\n\n" + q[idx:]
                print(repr(new_q))
            break
