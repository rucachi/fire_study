import json
import re

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
    orig_db = json.load(f)

# Build a mapping of original items based on normalized question text
orig_map = {}
for s in orig_db['subjects']:
    for i in s['items']:
        q_norm = re.sub(r'\s+', '', i['question'])
        orig_map[q_norm] = i

# 1. Delete "소방설비기사 전기 Anki" subject
original_s_len = len(db['subjects'])
db['subjects'] = [s for s in db['subjects'] if s.get('title') != '소방설비기사 전기 Anki' and s.get('id') != '소방설비기사 전기 Anki']
print(f"Deleted {original_s_len - len(db['subjects'])} subject(s) matching '소방설비기사 전기 Anki'")

# 2. Fix or delete problematic items
def clean_explanation(exp):
    if not exp: return ""
    # Remove useless markers or garbage
    exp = exp.replace('정답 ①', '').replace('정답 ②', '').replace('정답 ③', '').replace('정답 ④', '')
    exp = re.sub(r'^정답 \d\s*', '', exp)
    exp = re.sub(r'^정답\s*', '', exp)
    # if it's just '①' or empty, return empty
    text_only = re.sub(r'<[^>]+>', '', exp).strip()
    if text_only in ['①', '②', '③', '④', '()', '']:
        return ""
    return exp.strip()

total_deleted = 0
total_fixed_options = 0
total_fixed_conditions = 0

for s in db['subjects']:
    new_items = []
    for i in s['items']:
        q = i['question']
        opts = i.get('options', [])
        exp = clean_explanation(i.get('explanation', ''))
        i['explanation'] = exp
        
        q_norm = re.sub(r'\s+', '', q)
        orig = orig_map.get(q_norm)
        
        needs_opts = len(opts) < 4
        
        # Check for missing condition box
        # if there's ( ) but no fieldset and no 보기
        has_missing_box = bool(re.search(r'\(\s*\)', q)) and '<fieldset' not in q and '보기' not in q
        
        # Try to fix options
        if needs_opts:
            if orig and len(orig.get('options', [])) == 4:
                i['options'] = orig['options']
                needs_opts = False
                total_fixed_options += 1
            else:
                # Try to extract from explanation?
                # For now, if we can't get options, it's unfixable.
                pass
                
        # Try to fix condition box
        if has_missing_box:
            if orig and '<fieldset' in orig['question']:
                i['question'] = orig['question']
                has_missing_box = False
                total_fixed_conditions += 1
            else:
                # Can't find in original. Is there a condition in explanation?
                pass
        
        # Now decide whether to keep the item
        # If it STILL needs options (meaning it's less than 4 choices) => delete it
        # If it STILL has a missing condition box and we can't figure it out => delete it (or keep if we must, but user said delete unsalvageable ones)
        if needs_opts:
            total_deleted += 1
            continue
            
        if has_missing_box:
            # Let's delete it if the explanation is also empty, because it means we have no data to fill the ( )
            if not exp:
                total_deleted += 1
                continue
                
        new_items.append(i)
    s['items'] = new_items

print(f"Fixed {total_fixed_options} items with missing options.")
print(f"Fixed {total_fixed_conditions} items with missing condition boxes.")
print(f"Deleted {total_deleted} unfixable items (missing options or missing data).")

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
