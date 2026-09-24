import json

def search():
    with open('theme-bank.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open('scratch/found.txt', 'w', encoding='utf-8') as out:
        for s in data['subjects']:
            for i in s['items']:
                q = i.get('question', '')
                if '3종 연기감지기' in q or '3종' in q:
                    out.write(f"Q: {q}\n")
                    out.write(f"Opts: {i.get('options')}\n")
                    out.write(f"Exp: {i.get('explanation')}\n")
                    out.write("---\n")

search()
