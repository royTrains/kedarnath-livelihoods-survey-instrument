import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

files = ['vulnerability-to-poverty.txt','structural-transformation.txt','multidimensional-poverty-and-sustainable-livelihoods.txt']

quote_open = '“'
timestamp_pat = re.compile(r'^\(\d{1,2}/\d{1,2}/\d{4},\s*\d{1,2}:\d{2}:\d{2}\s*(am|pm)\)$', re.I)

for fn in files:
    print('='*20, fn, '='*20)
    with open(fn, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')

    in_notes = False
    para = []
    seen = set()

    def flush(para):
        if not para:
            return
        p = ' '.join(x.strip() for x in para).strip()
        if not p or p == 'o':
            return
        if p.startswith(quote_open):
            m = re.search(r'\([A-Za-z][^()]{0,60}?,\s*(19|20)\d{2}[^()]{0,25}?\)\s*(.+)$', p)
            if m and m.group(2).strip() and len(m.group(2).strip()) > 15:
                p = m.group(2).strip()
            else:
                return
        if p.startswith('Annotations'):
            return
        if timestamp_pat.match(p):
            return
        if p in ('Notes:', 'Attachments', 'Tags:'):
            return
        key = p[:100]
        if key in seen:
            return
        seen.add(key)
        print('-', p)

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if stripped == 'Notes:':
            in_notes = True
            para = []
            continue
        if stripped == 'Attachments':
            flush(para)
            para = []
            in_notes = False
            continue
        if not in_notes:
            continue
        if stripped == '':
            flush(para)
            para = []
            continue
        para.append(stripped)
    flush(para)
