#!/usr/bin/env python3
"""Fetch codes and laws published on the website of the Mejlis (Parliament) of Turkmenistan,
https://mejlis.gov.tm, in Turkmen (tm) and Russian (ru). Lists come from the site's own JSON
list endpoints (/codes?ajax=true, /laws?ajax=true). Pages cached in _raw/tm/html/."""
import gzip, json, os, sys, time, requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_raw', 'tm')
UA = 'LawCodex/1.0 (+https://github.com/LawCodex)'
KINDS = {'codes': 'single-code', 'laws': 'single-law'}


def get(s, url, **kw):
    for a in range(5):
        try:
            r = s.get(url, timeout=120, **kw)
            if r.status_code == 200:
                return r.text
            print('HTTP', r.status_code, url, file=sys.stderr)
        except Exception as e:
            print('ERR', url, e, file=sys.stderr)
        time.sleep(10 * (a + 1))
    return None


def main():
    os.makedirs(os.path.join(RAW, 'html'), exist_ok=True)
    s = requests.Session(); s.headers['User-Agent'] = UA
    index = []
    for kind, single in KINDS.items():
        for lang in ('tm', 'ru'):
            txt = get(s, f'https://mejlis.gov.tm/{kind}', params={'lang': lang, 'ajax': 'true'})
            items = json.loads(txt)
            if isinstance(items, str):
                items = json.loads(items)
            for it in items:
                index.append({'kind': kind, 'lang': lang, 'id': it['id'],
                              'title': it.get('title_' + lang) or '', 'published_date': it.get('published_date'),
                              'url': f'https://mejlis.gov.tm/{single}/{it["id"]}?lang={lang}'})
            time.sleep(1)
    index.append({'kind': 'constitutional-law', 'lang': 'tm', 'id': 0, 'title': '', 'published_date': None,
                  'url': 'https://mejlis.gov.tm/constitutional-law?lang=tm'})
    index.append({'kind': 'constitutional-law', 'lang': 'ru', 'id': 0, 'title': '', 'published_date': None,
                  'url': 'https://mejlis.gov.tm/constitutional-law?lang=ru'})
    json.dump(index, open(os.path.join(RAW, 'index.json'), 'w'), ensure_ascii=False, indent=0)
    for n, it in enumerate(index):
        out = os.path.join(RAW, 'html', f'{it["kind"]}-{it["id"]}-{it["lang"]}.html.gz')
        if os.path.exists(out):
            continue
        txt = get(s, it['url'])
        if txt:
            with gzip.open(out, 'wt', encoding='utf-8') as f:
                f.write(txt)
        time.sleep(1.5)
        if n % 50 == 0:
            print('progress', n, len(index), flush=True)
    print('done', len(index))


if __name__ == '__main__':
    main()
