#!/usr/bin/env python3
"""Convert Mejlis of Turkmenistan pages (_raw/tm/html/*.html.gz, from tm_fetch.py) to Markdown."""
import gzip, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
RAW = os.path.abspath(os.path.join(REPO, '..', '_raw', 'tm'))
RETRIEVED = '2026-10-12'

DIRS = {'tk': {'codes': 'kodeksler', 'laws': 'kanunlar', 'constitutional-law': 'konstitusion-kanunlar'},
        'ru': {'codes': 'kodeksy', 'laws': 'zakony', 'constitutional-law': 'konstitutsionnye-zakony'}}
TYPES = {'codes': 'code', 'laws': 'act', 'constitutional-law': 'constitutional_law'}

KINDS = ['part', 'section', 'chapter', 'paragraph', 'article']
PAT = {
    'part': re.compile(r'^((umumy|aýratyn|ýörite)\s+bölüm|(общая|особенная)\s+часть|часть\s+[IVXLC\d]+\b)', re.I),
    'section': re.compile(r'^([IVXLC\d]+\.?\s*[-‑]?\w{0,5}\s+bölüm\b|bölüm\s+[IVXLC\d]+|[a-zýüöäňçşž]+\s+bölüm$|раздел\b)', re.I),
    'chapter': re.compile(r'^([IVXLC\d]+\.?\s*[-‑]?\w{0,5}\s+bap\b|bap\s+[IVXLC\d]+|глава\b)', re.I),
    'paragraph': re.compile(r'^(§\s*\d|\d+[-‑]?\w{0,5}\s+paragraf\b|параграф\b)', re.I),
    'article': re.compile(r'^(\d+(\.\d+)?\s*[-‑]?\s*\w{0,5}\s+madda\b|madda\s+\d|статья\s+\d)', re.I),
}


def kind_of(t):
    for k in KINDS:
        if PAT[k].match(t.strip()):
            return k
    return None


def clean(t):
    t = t.replace('\xa0', ' ')
    t = re.sub(r'[ \t\r\f\v]+', ' ', t)
    return t.strip()


def md_escape(t):
    t = re.sub(r'^(#+)', r'\\\1', t)
    t = re.sub(r'^(\d+)([.)]) ', r'\1\\\2 ', t)
    t = re.sub(r'^([-+*>]) ', r'\\\1 ', t)
    return t


def ptext(p):
    out = []
    for d in p.descendants:
        if isinstance(d, NavigableString):
            out.append(str(d))
        elif d.name == 'br':
            out.append('\n')
    return '\n'.join(clean(l) for l in ''.join(out).split('\n') if clean(l))


def is_bold(p, txt):
    b = ''.join(ptext(x) for x in p.find_all(['strong', 'b']))
    return clean(b.replace('\n', ' ')) == clean(txt.replace('\n', ' ')) and txt != ''


def table_md(tbl):
    rows = []
    for tr in tbl.find_all('tr'):
        cells = [clean(ptext(td)).replace('\n', '<br>').replace('|', '\\|') for td in tr.find_all(['td', 'th'])]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ''
    n = max(len(r) for r in rows)
    rows = [r + [''] * (n - len(r)) for r in rows]
    return '\n'.join(['| ' + ' | '.join(rows[0]) + ' |', '|' + ' --- |' * n] +
                     ['| ' + ' | '.join(r) + ' |' for r in rows[1:]])


def convert(content):
    blocks = []
    for el in content.find_all(['p', 'table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'], recursive=True):
        if el.find_parent('table') is not None and el.name != 'table':
            continue
        if el.name == 'table':
            m = table_md(el)
            if m:
                blocks.append(['raw', m])
            continue
        if el.name == 'p' and el.find_parent('li') is not None:
            continue
        txt = ptext(el)
        if not txt:
            continue
        bold = is_bold(el, txt) or el.name.startswith('h')
        one = txt.replace('\n', ' ')
        k = kind_of(one) if bold else None
        if k:
            blocks.append(['h', k, one])
        elif bold and blocks and blocks[-1][0] == 'h' and blocks[-1][1] in KINDS and len(one) < 300:
            blocks[-1][2] += ' ' + one
        elif bold:
            blocks.append(['b', one])
        else:
            for ln in txt.split('\n'):
                blocks.append(['p', ln])
    return blocks


def render(blocks):
    present = [k for k in KINDS if any(b[0] == 'h' and b[1] == k for b in blocks)]
    level = {k: min(2 + i, 6) for i, k in enumerate(present)}
    out = []
    for b in blocks:
        if b[0] == 'h':
            out.append('#' * level[b[1]] + ' ' + b[2])
        elif b[0] == 'b':
            out.append('**' + b[1] + '**')
        elif b[0] == 'p':
            out.append(md_escape(b[1]))
        else:
            out.append(b[1])
    return '\n\n'.join(out) + '\n'


TR = {'ç': 'ch', 'ş': 'sh', 'ž': 'zh', 'ý': 'y', 'ü': 'u', 'ö': 'o', 'ä': 'a', 'ň': 'n'}
TRC = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
               ['a', 'b', 'v', 'g', 'd', 'e', 'yo', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
                'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu', 'ya']))


def slug(s, n=70):
    s = s.lower()
    s = ''.join(TR.get(c, TRC.get(c, c)) for c in s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:n].rstrip('-')


def yq(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    index = json.load(open(os.path.join(RAW, 'index.json')))
    stats = {}
    for it in index:
        fn = os.path.join(RAW, 'html', f'{it["kind"]}-{it["id"]}-{it["lang"]}.html.gz')
        if not os.path.exists(fn):
            continue
        soup = BeautifulSoup(gzip.open(fn, 'rt', encoding='utf-8').read(), 'lxml')
        tb = soup.select_one('.text_block')
        content = tb.select_one('.text_content') if tb else None
        if content is None:
            content = soup.select_one('.right_side') or soup.select_one('.constitutional_law')
        if content is None:
            print('no content', fn, file=sys.stderr)
            continue
        h = tb.select_one('.text_title') if tb else None
        title = clean(h.get_text(' ')) if h else clean(it['title'])
        if not title:
            title = 'Konstitusion kanun' if it['lang'] == 'tm' else 'Конституционный закон'
        title = title.rstrip('*').strip()
        blocks = convert(content)
        if not blocks:
            print('empty', fn, file=sys.stderr)
            continue
        lang = 'tk' if it['lang'] == 'tm' else 'ru'
        date = (it.get('published_date') or '')[:10] or None
        sub = DIRS[lang][it['kind']]
        name = slug(title) + (f'-{it["id"]}' if it['id'] else '')
        if it['kind'] == 'laws' and date:
            rel = os.path.join(lang, sub, date[:4], name + '.md')
        else:
            rel = os.path.join(lang, sub, name + '.md')
        fm = ['---', f'title: {yq(title)}', f'identifier: "mejlis:{it["kind"]}/{it["id"]}"',
              f'type: {TYPES[it["kind"]]}', 'jurisdiction: tm', f'language: {lang}']
        if date:
            fm.append(f'date: {date}  # date shown on mejlis.gov.tm (adoption / publication)')
        fm += ['status: unknown', f'source: "{it["url"]}"', f'retrieved: {RETRIEVED}', '---', '']
        md = '\n'.join(fm) + f'\n# {title}\n\n' + render(blocks)
        out = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(md)
        stats[(lang, it['kind'])] = stats.get((lang, it['kind']), 0) + 1
    print(stats)


if __name__ == '__main__':
    main()
