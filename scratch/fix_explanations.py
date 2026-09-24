import json
import re

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    orig_db = json.load(f)

orig_items = [i for s in orig_db['subjects'] for i in s['items']]

def get_number(q):
    m = re.match(r'^(\d+)\.', q.strip())
    return m.group(1) if m else 'none'

def normalize(t): return re.sub(r'\s+', '', t)

orig_map = {}
for o in orig_items:
    num = get_number(o['question'])
    if num not in orig_map:
        orig_map[num] = []
    orig_map[num].append(o)

matched = 0
fixed_exps = 0
fixed_opts = 0

for s_idx, s in enumerate(db['subjects']):
    # Only touch themes 0, 1, 2 which have multiple choice questions
    if s_idx > 2:
        continue
        
    for i in s['items']:
        raw_curr = i['question'].split('**[ 그림 ]**')[0]
        curr_q = normalize(raw_curr)
        num = get_number(i['question'])
        
        candidates = orig_map.get(num, [])
        if not candidates:
            candidates = orig_items
            
        matches = [o for o in candidates if curr_q in normalize(o['question'])]
        if len(matches) >= 1:
            orig = matches[0]
            matched += 1
            
            orig_q = orig['question']
            
            # 1. Truncate options to 4
            opts = i.get('options', [])
            if len(opts) > 4:
                i['options'] = opts[:4]
                fixed_opts += 1
                
            # 2. Extract explanation from original question
            if '<문제 해설>' in orig_q:
                parts = orig_q.split('<문제 해설>')
                if len(parts) > 1:
                    exp_text = parts[1].strip()
                    # Remove trailing [해설작성자 : ...] if present
                    exp_text = re.sub(r'\[해설작성자\s*:.*?\]', '', exp_text).strip()
                    
                    # Merge with existing explanation (if any, e.g. ### 그림 that I added before)
                    # Wait, in the previous script I appended ### 그림 to `i['question']`, NOT `i['explanation']`!
                    # So `i['explanation']` is mostly empty ("").
                    
                    # Let's also check if orig had an explanation field
                    orig_exp_field = orig.get('explanation', '')
                    # If orig_exp_field has text other than just '### 그림', we can append it.
                    orig_exp_text = re.sub(r'### 그림.*?(\n|$)', '', orig_exp_field, flags=re.DOTALL).strip()
                    if orig_exp_text.startswith("정답은"):
                        orig_exp_text = "" # Often just boilerplate
                        
                    final_exp = exp_text
                    if orig_exp_text:
                        final_exp += '\n\n' + orig_exp_text
                        
                    if final_exp and i.get('explanation') != final_exp:
                        i['explanation'] = final_exp
                        fixed_exps += 1

print(f"Matched: {matched}, Fixed Options: {fixed_opts}, Fixed Explanations: {fixed_exps}")

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
print("Saved to theme-bank.json")
