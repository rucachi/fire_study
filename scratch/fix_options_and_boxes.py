import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

opts_fixed = 0
boxes_fixed = 0

for s in data['subjects']:
    for i in s['items']:
        # 1. Fix >4 options
        opts = i.get('options', [])
        if len(opts) > 4:
            extra_opts = opts[4:]
            i['options'] = opts[:4]
            # append extra options to the beginning of the explanation
            extra_text = '\n'.join(extra_opts)
            if 'explanation' in i:
                i['explanation'] = extra_text + '\n' + i['explanation']
            else:
                i['explanation'] = extra_text
            opts_fixed += 1
            
        # 2. Fix missing condition boxes
        q = i.get('question', '')
        has_parens = '(' in q and ')' in q
        if has_parens and '<img' not in q and '![' not in q and 'fieldset' not in q:
            # simple check: if the question is short (fewer than 4 lines)
            lines = q.split('\n')
            if len(lines) < 4 and q.strip().endswith('?'):
                # Some questions are just simple fill-in-the-blanks that don't need a box.
                # But questions that refer to "다음 ( ) 안에" or "다음 중" with a missing block 
                # usually have the block in the explanation. 
                # We will check if it mentions '다음', '알맞은', '들어갈', '내용', '기준'
                if '다음' in q or '들어갈' in q or '알맞은' in q:
                    exp = i.get('explanation', '')
                    if exp:
                        clean_exp = exp.strip().replace('\n', '<br>')
                        new_q = q + f'\n\n<fieldset style="padding:10px; border:1px solid #ddd; border-radius:5px;"><legend>조건</legend>{clean_exp}</fieldset>'
                        i['question'] = new_q
                        boxes_fixed += 1

with open('theme-bank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Fixed >4 options in {opts_fixed} items.')
print(f'Fixed {boxes_fixed} missing condition boxes.')
