#!/usr/bin/env python3
"""Constitution of Turkmenistan (Russian text) from the State News Agency / government portal
"Turkmenistan: the Golden Age" (https://turkmenistan.gov.tm), section Законодательство:
  - post 27017: Конституция Туркменистана (новая редакция) of 14.09.2016
  - post 36539: Constitutional Law of 25.09.2020 amending the Constitution (bicameral Milli Gengesh)
The Mejlis website (mejlis.gov.tm) only publishes the 2016 constitutional law that approved the new
edition, not the text of the Constitution itself.
"""
import os, re, sys, time, html, requests
from bs4 import BeautifulSoup, NavigableString

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
UA = 'LawCodex/1.0 (+https://github.com/LawCodex)'
RETRIEVED = '2026-10-12'
DOCS = [
    ('27017', 'konstitutsiya-turkmenistana-2016', 'constitution', '2016-09-14',
     'https://turkmenistan.gov.tm/ru/post/27017/konstitutsiya-turkmenistana-(novaya-redaktsiya)'),
    ('36539', 'konstitutsionnyi-zakon-2020-09-25-o-vnesenii-izmenenii-v-konstitutsiyu', 'constitutional_law', '2020-09-25',
     'https://turkmenistan.gov.tm/ru/post/36539/konstitutsionnyi-zakon-turkmenistana-o-vnesenii-izmenenii-i-dopolnenii-v-konstitutsiyu-turkmenistana'),
]
KIND = [('section', re.compile(r'^РАЗДЕЛ\s+[IVXLC]+', re.I)), ('chapter', re.compile(r'^Глава\s+\d+', re.I)),
        ('article', re.compile(r'^Статья\s+\d+', re.I))]


def lines_of(div):
    out, cur, bold = [], [], []
    for d in div.descendants:
        if isinstance(d, NavigableString):
            cur.append(str(d))
            if d.parent.name in ('b', 'strong'):
                bold.append(str(d))
        elif d.name == 'br':
            out.append((''.join(cur), ''.join(bold))); cur, bold = [], []
        elif d.name in ('p', 'div') and cur:
            out.append((''.join(cur), ''.join(bold))); cur, bold = [], []
    out.append((''.join(cur), ''.join(bold)))
    res = []
    for t, b in out:
        t = re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()
        b = re.sub(r'\s+', ' ', b.replace('\xa0', ' ')).strip()
        if t:
            res.append((t, b))
    return res


def main():
    s = requests.Session(); s.headers['User-Agent'] = UA
    for pid, name, typ, date, url in DOCS:
        r = s.get(url, timeout=120)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        title = re.sub(r'\s+', ' ', html.unescape(soup.find('title').get_text())).replace('<br>', ' ').strip().rstrip('*').strip()
        div = soup.select_one('#post .post_text') or soup.select_one('#post')
        out = []
        for t, b in lines_of(div):
            k = next((k for k, p in KIND if p.match(t)), None)
            if k and b and t.startswith(b):
                lvl = {'section': '##', 'chapter': '###', 'article': '####'}[k]
                out.append(f'{lvl} {b}')
                rest = t[len(b):].strip()
                if rest:
                    out.append(rest)
            else:
                t = re.sub(r'^(\d+)([.)]) ', r'\1\\\2 ', t)
                out.append(t)
        fm = ['---', f'title: "{title}"', f'identifier: "turkmenistan.gov.tm/ru/post/{pid}"', f'type: {typ}',
              'jurisdiction: tm', 'language: ru', f'date: {date}',
              'status: in_force' if typ == 'constitution' else 'status: in_force',
              f'source: "{url}"', f'retrieved: {RETRIEVED}', '---', '']
        note = ''
        if typ == 'constitution':
            note = ('> Text of the 2016 edition as published on the government portal. It does not incorporate '
                    'the amendments of 25 September 2020 (see the constitutional law in this directory) and of '
                    '21 January 2023.\n\n')
        md = '\n'.join(fm) + f'\n# {title}\n\n' + note + '\n\n'.join(out) + '\n'
        path = os.path.join(REPO, 'ru', 'konstitutsiya', name + '.md')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8', newline='\n').write(md)
        print('wrote', path)
        time.sleep(2)


if __name__ == '__main__':
    main()
