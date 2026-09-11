from pathlib import Path
from bs4 import BeautifulSoup
import json,sys
root=Path('.'); errors=[]; pages=[]
for p in root.rglob('*.html'):
    if '.git' in p.parts or '.bootstrap' in p.parts: continue
    pages.append(p)
    rel=p.as_posix(); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); h=s.head
    if not h: errors.append(f'{rel}: missing head'); continue
    robots=h.find('meta',attrs={'name':'robots'}); canonical=h.find('link',rel='canonical')
    if rel=='404.html':
        if not robots or 'noindex' not in robots.get('content',''): errors.append(f'{rel}: must be noindex')
        if canonical: errors.append(f'{rel}: must not have canonical')
    else:
        if not canonical or not canonical.get('href','').startswith('https://interfacereport.com/'): errors.append(f'{rel}: canonical')
        if not robots or 'index' not in robots.get('content',''): errors.append(f'{rel}: indexability')
    if not s.title or not h.find('meta',attrs={'name':'description'}): errors.append(f'{rel}: title/description')
    if not h.find('meta',attrs={'property':'og:image'}) or not h.find('meta',attrs={'name':'twitter:image'}): errors.append(f'{rel}: social image')
    if not h.find('meta',attrs={'property':'og:locale'}): errors.append(f'{rel}: og locale')
    for x in h.find_all('script',attrs={'type':'application/ld+json'}):
        try: json.loads(x.string or '')
        except Exception: errors.append(f'{rel}: invalid JSON-LD')
    if rel.startswith('analysis/'):
        if len(s.title.get_text())>65: errors.append(f'{rel}: title too long')
        desc=h.find('meta',attrs={'name':'description'}).get('content','')
        if not 120<=len(desc)<=165: errors.append(f'{rel}: description length {len(desc)}')
        if not h.find('meta',attrs={'name':'author'}) or not h.find('link',rel='author'): errors.append(f'{rel}: author metadata')
        if not h.find('meta',attrs={'property':'og:image:alt'}) or not h.find('meta',attrs={'name':'twitter:image:alt'}): errors.append(f'{rel}: social image alt')
        prose=s.select_one('article.prose')
        if not prose or len(prose.get_text(' ',strip=True).split())<700: errors.append(f'{rel}: thin article')
    # Local internal link integrity.
    for a in s.find_all('a',href=True):
        href=a['href']
        if not href.startswith('/') or href.startswith('//') or href.startswith('/#'): continue
        path=href.split('#')[0].split('?')[0]
        if path in ('','/'): target=root/'index.html'
        elif path.endswith('/'): target=root/path.lstrip('/')/'index.html'
        else: target=root/path.lstrip('/')
        if not target.exists(): errors.append(f'{rel}: broken internal link {href}')
robots=Path('robots.txt').read_text(encoding='utf-8')
sitemap=Path('sitemap.xml').read_text(encoding='utf-8')
if 'User-agent: OAI-SearchBot' not in robots or 'Allow: /' not in robots: errors.append('robots: OAI-SearchBot')
if 'User-agent: GPTBot' not in robots or 'Disallow: /' not in robots: errors.append('robots: GPTBot policy')
if 'https://interfacereport.com/' not in sitemap or '404.html' in sitemap: errors.append('sitemap')
for f in ['assets/agent-control-surface.png','assets/patterns.png','assets/trust.png','assets/og-default.png','feed.xml','60a759d8d9915a4816e0dafdc1128b86.txt']:
    if not Path(f).exists(): errors.append(f'missing {f}')
print(f'HTML files checked: {len(pages)}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('All internal links, canonical/meta, JSON-LD, article depth, crawler and indexing checks passed.')
