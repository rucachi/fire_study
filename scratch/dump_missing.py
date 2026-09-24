import json
import re

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = []
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if ('()' in q or '( )' in q or '빈칸' in q or '안에' in q or '다음' in q) and '<fieldset' not in q:
            # Maybe it is missing a box if it is short
            lines = [l for l in q.split('\n') if l.strip()]
            if len(lines) <= 3:
                missing.append(i)

with open('scratch/missing_report.md', 'w', encoding='utf-8') as f:
    for m in missing[:50]:
        f.write(f"### ID: {m.get('id')}\n")
        f.write(f"**Q**: {m.get('question')}\n")
        f.write(f"**Opts**: {m.get('options')}\n")
        f.write(f"**Exp**: {m.get('explanation')[:100]}...\n\n")

print(f"Found {len(missing)} possible missing box questions.")
