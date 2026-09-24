import json
import re

def rebuild_theme_bank():
    with open('theme-bank-original.json', 'r', encoding='utf-16') as f:
        data = json.load(f)

    fixed_count = 0

    for s in data['subjects']:
        for i in s['items']:
            q = i.get('question', '')
            exp = i.get('explanation', '')
            
            if '### 그림' in exp:
                parts = exp.split('### 그림')
                new_exp = parts[0].strip()
                cond_text = '### 그림'.join(parts[1:]).strip()
                
                # We format cond_text a bit nicely
                if cond_text:
                    cond_injection = f"\n\n**[ 조건 / 그림 ]**\n\n{cond_text}\n\n"
                    
                    # Try to find options (①, ❶, etc.)
                    match = re.search(r'\n\s*[①❶]', q)
                    if match:
                        idx = match.start()
                        new_q = q[:idx] + cond_injection + q[idx:]
                    else:
                        new_q = q + cond_injection
                        
                    i['question'] = new_q
                    i['explanation'] = new_exp
                    fixed_count += 1

    with open('theme-bank.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully rebuilt theme-bank.json from theme-bank-original.json.")
    print(f"Fixed {fixed_count} items with missing conditions/images.")

if __name__ == '__main__':
    rebuild_theme_bank()
