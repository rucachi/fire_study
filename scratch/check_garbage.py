import json
import re

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

garbage_keywords = ['본 해설집은', '최강 자격증', '전자문제집 CBT', 'www.comcbt.com', '실시간으로 변경됩니다', '해설작성자 :']

issues = []
for s in data['subjects']:
    for i in s['items']:
        exp = i.get('explanation', '')
        for kw in garbage_keywords:
            if kw in exp:
                issues.append(f"Found '{kw}' in item: {i.get('question', '')[:20]}")

        # check for trailing numbers
        if re.search(r'\n[\d\s]+$', exp):
            issues.append(f"Trailing numbers found in item: {i.get('question', '')[:20]}")

with open('scratch/garbage_issues.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total garbage text issues found: {len(issues)}\n')
    for issue in issues:
        f.write(issue + '\n')
