import json

with open('theme-bank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for s in data['subjects']:
    for i in s['items']:
        q = i.get('question', '')
        if '<fieldset' not in q and '<img' not in q and '![' not in q:
            # We want to match any phrase that strongly suggests a missing box.
            # e.g., '다음 ( )', '( ) 안에', '( )에', '( ) 안의'
            # But ONLY if the question text itself is short and doesn't contain the box text.
            lines = [l for l in q.split('\n') if l.strip()]
            if len(lines) <= 2 and ('(' in q and ')' in q):
                if any(x in q for x in ['다음', '아래', '알맞은', '들어갈', '내용', '기준']):
                    # Check if it has real options (i.e. not an essay question)
                    if len(i.get('options', [])) > 0:
                        count += 1
                        print(f"Q: {q.strip()}")
print(f'Total candidates: {count}')
