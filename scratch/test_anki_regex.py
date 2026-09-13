with open(r'C:\antigravity\anki\새 폴더\소방설비기사-실기-객관식.txt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
questions = re.split(r'\n(?=\d+\.\s)', '\n' + text)
fail = 0
for q in questions[1:]:
    parts = q.split('\t')
    if len(parts) > 1:
        ans_str = parts[1]
        
        match = re.match(r'^\s*(?:\[?정답\]?|답)?\s*:?\s*(?:<br>)?\s*([①②③④❶❷❸❹])', ans_str.replace('\"', ''))
        if not match:
            match = re.search(r'(?:\[?정답\]?|답)\s*:?\s*(?:<br>)?\s*([①②③④❶❷❸❹1234])', ans_str)
        
        if not match:
            fail += 1
            print(repr(ans_str[:30]))
print('Fail:', fail)
