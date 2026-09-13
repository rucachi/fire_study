import json
import re
import glob

def normalize_text(text):
    text = re.sub(r'^\d+\.\s*', '', text) # Strip question number
    text = re.sub(r'[\s\u200b]+', '', text)
    text = re.sub(r'[①②③④❶❷❸❹]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[해설작성자.*?\]', '', text)
    text = re.sub(r'<문제 해설>.*', '', text)
    return text.strip()

def clean_watermarks(text):
    text = re.sub(r'\[해설작성자.*?\]', '', text)
    text = re.sub(r'본 해설집은.*?\n?', '', text)
    text = re.sub(r'해설을 제공해 주신 모든 분들께 감사 드립니다\.', '', text)
    text = re.sub(r'소방설비기사\(전기분야\)', '', text)
    text = re.sub(r'◐.*?◑', '', text)
    text = re.sub(r'전자문제집 CBT : www\.comcbt\.com', '', text)
    text = re.sub(r'기출문제 해설은 최강 자격증 기출문제 전자문제집 CBT : www\.comcbt\.com 통해서 실시간으로 변경됩니다\.', '', text)
    text = re.sub(r'최강 자격증 기출문제 전자문제집 CBT : www\.comcbt\.com', '', text)
    text = re.sub(r'## \?\?\? \d+', '', text)
    text = re.sub(r'<문제 해설>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'^\s*---\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def is_contaminated_question(text):
    watermark_patterns = (
        '최강 자격증 기출문제',
        '전자문제집 CBT',
        '해설달기 프로젝트',
        '실시간으로 변경됩니다',
        'www.comcbt.com',
    )
    return any(pattern in text for pattern in watermark_patterns)

def extract_explanation(text):
    exp = []
    if '[해설작성자' in text:
        parts = text.split('[해설작성자')
        for p in parts[1:]:
            p = p.split(']', 1)[-1]
            exp.append(p.strip())
    
    if '<문제 해설>' in text:
        parts = text.split('<문제 해설>')
        for p in parts[1:]:
            exp.append(p.strip())
            
    return '\n\n'.join(exp)

def parse_anki_txt(fpath):
    db = {}
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            parts = line.split('\t')
            if len(parts) >= 2:
                q = parts[0]
                a = parts[1]
                exp = parts[2] if len(parts) >= 3 else ""
                
                q = re.sub(r'<style>.*?</style>', '', q, flags=re.DOTALL)
                q = re.sub(r'<(?!br\s*/?>)[^>]+>', '', q)
                q = q.replace('<br>', '\n').replace('<br/>', '\n')
                
                exp = re.sub(r'<style>.*?</style>', '', exp, flags=re.DOTALL)
                exp = re.sub(r'<(?!br\s*/?>)[^>]+>', '', exp)
                exp = exp.replace('<br>', '\n').replace('<br/>', '\n')
                
                # Dedup by first line to catch missing boxes
                first_line = q.strip().split('\n')[0]
                nk = normalize_text(first_line)
                item = {'question': q.strip(), 'answer': a.strip(), 'explanation': exp.strip()}
                if nk in db:
                    if len(item['question']) > len(db[nk]['question']):
                        db[nk] = item
                else:
                    db[nk] = item
    return db

def parse_options(q_text):
    lines = q_text.split('\n')
    stem_lines = []
    options = []
    ans_idx = None
    
    for line in lines:
        if re.match(r'^\s*[①②③④❶❷❸❹]\s+', line):
            opts_in_line = re.split(r'(\s*[①②③④❶❷❸❹]\s+)', line)
            current_opt_marker = None
            current_opt_text = ""
            for part in opts_in_line:
                if re.match(r'^\s*[①②③④❶❷❸❹]\s+$', part):
                    if current_opt_marker:
                        options.append((current_opt_marker, current_opt_text.strip()))
                    current_opt_marker = part.strip()
                    current_opt_text = ""
                else:
                    current_opt_text += part
            if current_opt_marker:
                options.append((current_opt_marker, current_opt_text.strip()))
        else:
            if not options:
                stem_lines.append(line)
            else:
                options[-1] = (options[-1][0], options[-1][1] + "\n" + line)
                
    clean_options = []
    for marker, text in options:
        if marker in ['❶', '❷', '❸', '❹']:
            ans_idx = len(clean_options)
        clean_options.append(text)
        
    return '\n'.join(stem_lines), clean_options, ans_idx

FILL_TO_OUT = str.maketrans('❶❷❸❹❺❻❼❽❾❿', '①②③④⑤⑥⑦⑧⑨⑩')

def process_md_question(q_text, theme, themes, txt_db_laws, omr_table):
    norm_key = normalize_text(q_text)
    
    txt_data = None
    if theme == 'theme-3-fire-laws' and norm_key in txt_db_laws:
        txt_data = txt_db_laws[norm_key]
        
    stem, opts, ans_idx = parse_options(q_text)
    stem = clean_watermarks(stem)
    opts = [clean_watermarks(opt) for opt in opts]

    if is_contaminated_question(stem) or any(is_contaminated_question(opt) for opt in opts):
        return
    
    match = re.match(r'^(\d+)\.\s', stem.strip())
    if match:
        num = int(match.group(1))
        if ans_idx is None and num in omr_table:
            ans_idx = omr_table[num]
            
    if txt_data and txt_data.get('answer') and ans_idx is None:
        try:
            val = int(txt_data['answer']) - 1
            if 0 <= val < 4: ans_idx = val
        except: pass
        
    explanations = []
    if txt_data and txt_data.get('explanation'): explanations.append(txt_data['explanation'])
    q_exp = extract_explanation(q_text)
    if q_exp: explanations.append(q_exp)
    
    final_exp = '\n\n'.join(explanations).translate(FILL_TO_OUT).strip()
    
    if stem and opts:
        item = {
            'question': stem.translate(FILL_TO_OUT),
            'options': [o.translate(FILL_TO_OUT) for o in opts],
            'answer': ans_idx,
            'explanation': final_exp
        }
        
        if norm_key not in themes[theme]['unique_items']:
            themes[theme]['unique_items'][norm_key] = item
        else:
            existing = themes[theme]['unique_items'][norm_key]
            
            if item['explanation']:
                if existing['explanation']:
                    if item['explanation'] not in existing['explanation']:
                        existing['explanation'] += '\n\n' + item['explanation']
                else:
                    existing['explanation'] = item['explanation']
            
            if existing['answer'] is None and item['answer'] is not None:
                existing['answer'] = item['answer']
                existing['options'] = item['options']
                existing['question'] = item['question']

def extract_omr(text):
    ans_table = {}
    lines = [line.strip() for line in text.split('\n')]
    for i in range(len(lines) - 20):
        if lines[i] == '1' and lines[i+1] == '2' and lines[i+9] == '10':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '11' and lines[i+1] == '12' and lines[i+9] == '20':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '21' and lines[i+1] == '22' and lines[i+9] == '30':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '31' and lines[i+1] == '32' and lines[i+9] == '40':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '41' and lines[i+1] == '42' and lines[i+9] == '50':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '51' and lines[i+1] == '52' and lines[i+9] == '60':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '61' and lines[i+1] == '62' and lines[i+9] == '70':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
        elif lines[i] == '71' and lines[i+1] == '72' and lines[i+9] == '80':
            for j in range(10):
                if lines[i+10+j] in '①②③④':
                    ans_table[int(lines[i+j])] = '①②③④'.index(lines[i+10+j])
    return ans_table

def parse_md_files(txt_db_laws):
    md_files = glob.glob(r'C:\antigravity\anki\새 폴더\*.md')
    
    themes = {
        'theme-1-fire-principles': {'id': 'theme-1-fire-principles', 'title': '소방원론', 'unique_items': {}},
        'theme-3-fire-laws': {'id': 'theme-3-fire-laws', 'title': '소방관계법규', 'unique_items': {}},
        'theme-4-fire-electrical-facilities': {'id': 'theme-4-fire-electrical-facilities', 'title': '소방전기시설의 구조 및 원리', 'unique_items': {}}
    }
    
    for fpath in md_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        omr_table = extract_omr(content)
            
        lines = content.split('\n')
        current_q_text = []
        current_theme = None
        
        for line in lines:
            if '1과목' in line and '소방원론' in line: current_theme = 'theme-1-fire-principles'
            elif '2과목' in line and '소방전기회로' in line: current_theme = 'theme-2'
            elif '3과목' in line and '소방관계법규' in line: current_theme = 'theme-3-fire-laws'
            elif '4과목' in line and '소방전기시설' in line: current_theme = 'theme-4-fire-electrical-facilities'
            
            m = re.match(r'^(\d+)\.\s', line.strip())
            if m:
                new_num = int(m.group(1))
                
                if current_q_text and current_theme and current_theme != 'theme-2':
                    prev_num = int(re.match(r'^(\d+)\.\s', current_q_text[0].strip()).group(1))
                    process_it = True
                    if current_theme == 'theme-1-fire-principles' and not (1 <= prev_num <= 20): process_it = False
                    if current_theme == 'theme-3-fire-laws' and not (41 <= prev_num <= 60): process_it = False
                    if current_theme == 'theme-4-fire-electrical-facilities' and not (61 <= prev_num <= 80): process_it = False
                    
                    if process_it:
                        process_md_question('\n'.join(current_q_text), current_theme, themes, txt_db_laws, omr_table)
                
                current_q_text = [line]
            elif current_q_text:
                current_q_text.append(line)
                
        if current_q_text and current_theme and current_theme != 'theme-2':
            prev_num = int(re.match(r'^(\d+)\.\s', current_q_text[0].strip()).group(1))
            process_it = True
            if current_theme == 'theme-1-fire-principles' and not (1 <= prev_num <= 20): process_it = False
            if current_theme == 'theme-3-fire-laws' and not (41 <= prev_num <= 60): process_it = False
            if current_theme == 'theme-4-fire-electrical-facilities' and not (61 <= prev_num <= 80): process_it = False
            if process_it:
                process_md_question('\n'.join(current_q_text), current_theme, themes, txt_db_laws, omr_table)
            
    for t_id, t_data in themes.items():
        t_data['items'] = list(t_data['unique_items'].values())
        del t_data['unique_items']
        
    return themes

def build_theme_5(txt_db_anki):
    items = []
    for nk, data in txt_db_anki.items():
        raw_q = data['question']
        clean_q = clean_watermarks(raw_q)
        stem, options, ans_idx = parse_options(clean_q)

        if is_contaminated_question(stem) or any(is_contaminated_question(opt) for opt in options):
            continue
        
        if data.get('answer'):
            ans_str = data['answer'].replace('\"', '')
            match = re.match(r'^\s*(?:\[?정답\]?|답)?\s*:?\s*(?:<br>)?\s*([①②③④❶❷❸❹])', ans_str)
            if not match:
                match = re.search(r'(?:\[?정답\]?|답)\s*:?\s*(?:<br>)?\s*([①②③④❶❷❸❹1234])', ans_str)
            
            if match:
                ans_str = match.group(1)
                if ans_str in '①②③④':
                    ans_idx = '①②③④'.index(ans_str)
                elif ans_str in '❶❷❸❹':
                    ans_idx = '❶❷❸❹'.index(ans_str)
                elif ans_str in '1234':
                    ans_idx = int(ans_str) - 1
            
        explanations = []
        if data.get('explanation'): explanations.append(data['explanation'])
        q_exp = extract_explanation(raw_q)
        if q_exp: explanations.append(q_exp)
        
        final_exp = '\n\n'.join(explanations).translate(FILL_TO_OUT).strip()
        
        if stem and options:
            item = {
                'question': stem.translate(FILL_TO_OUT),
                'options': [o.translate(FILL_TO_OUT) for o in options],
                'answer': ans_idx,
                'explanation': final_exp
            }
            items.append(item)
            
    return {'id': 'theme-5-fire-electrical-anki', 'title': '소방설비기사 전기 Anki', 'items': items}

def main():
    txt_db_laws = parse_anki_txt(r'C:\antigravity\anki\소방설비기사-법규.txt')
    txt_db_anki = parse_anki_txt(r'C:\antigravity\anki\소방설비기사-실기-객관식.txt')
    
    themes = parse_md_files(txt_db_laws)
    theme_5 = build_theme_5(txt_db_anki)
    
    final_subjects = [
        themes['theme-1-fire-principles'],
        themes['theme-3-fire-laws'],
        themes['theme-4-fire-electrical-facilities'],
        theme_5
    ]
    
    for s in final_subjects:
        null_count = sum(1 for i in s['items'] if i['answer'] is None)
        print(f"Subject {s['title']}: {len(s['items'])} items, {null_count} null answers")
        
    out = {'subjects': final_subjects}
    with open(r'C:\antigravity\anki\theme-bank.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
