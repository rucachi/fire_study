import json
import re

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for s in data['subjects']:
    for i in s['items']:
        if 'explanation' in i and i['explanation']:
            original = i['explanation']
            exp = i['explanation']
            
            # Remove blocks
            if '본 해설집의 저작권은 www.comcbt.com에 있으며' in exp:
                exp = exp.split('본 해설집의 저작권은 www.comcbt.com에 있으며')[0]
                
            if '위 문제는 오류 신고가 접수된' in exp:
                # Can appear multiple times or at the end
                exp = re.sub(r'위 문제는 오류 신고가 접수된 문제입니다\..*?최신 해설을 확인하세요\.', '', exp, flags=re.DOTALL)
                
            if '아래와 같은 오류 신고가' in exp:
                exp = re.sub(r'아래와 같은 오류 신고가 있었습니다\..*?(?:\[해설작성자 :.*?\]|수정합니다\.)', '', exp, flags=re.DOTALL)
                
            # Remove trailing numbers and circle numbers block
            # Match block of lines at the end that contain only numbers, spaces, and circle numbers
            exp = re.sub(r'(?:\n[\d\s①②③④]+)+$', '', exp)
            
            # Remove stray [해설작성자 : ...]
            exp = re.sub(r'\[해설작성자 : .*?\]', '', exp)
            
            exp = exp.strip()
            
            if original != exp:
                i['explanation'] = exp
                count += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Cleaned {count} additional items.')
