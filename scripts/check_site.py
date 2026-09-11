from pathlib import Path
from bs4 import BeautifulSoup
import json
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

root = Path('.')
base = 'https://interfacereport.com/'
errors = []
pages = []
canonical_urls = set()

for p in root.rglob('*.html'):
    if '.git' in p.parts or '.bootstrap' in p.parts:
        continue
    pages.append(p)
    rel = p.as_posix()
    s = BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser')
    h = s.head
    if not h:
        errors.append(f'{rel}: missing head')
        continue

    robots = h.find('meta', attrs={'name': 'robots'})
    canonical = h.find('link', rel='canonical')

    if rel == '404.html':
        if not robots or 'noindex' not in robots.get('content', ''):
            errors.append(f'{rel}: must be noindex')
        if canonical:
            errors.append(f'{rel}: must not have canonical')
    else:
        if not canonical or not canonical.get('href', '').startswith(base):
            errors.append(f'{rel}: canonical')
        else:
            href = canonical.get('href', '')
            if href in canonical_urls:
                errors.append(f'{rel}: duplicate canonical {href}')
            canonical_urls.add(href)
        if not robots or 'index' not in robots.get('content', '') or 'noindex' in robots.get('content', ''):
            errors.append(f'{rel}: indexability')

    if not s.title or not h.find('meta', attrs={'name': 'description'}):
        errors.append(f'{rel}: title/description')
    if not h.find('meta', attrs={'property': 'og:image'}) or not h.find('meta', attrs={'name': 'twitter:image'}):
        errors.append(f'{rel}: social image')
    if not h.find('meta', attrs={'property': 'og:locale'}):
        errors.append(f'{rel}: og locale')

    for x in h.find_all('script', attrs={'type': 'application/ld+json'}):
        try:
            json.loads(x.string or '')
        except Exception:
            errors.append(f'{rel}: invalid JSON-LD')

    if rel.startswith('analysis/'):
        if len(s.title.get_text()) > 65:
            errors.append(f'{rel}: title too long')
        desc = h.find('meta', attrs={'name': 'description'}).get('content', '')
        if not 120 <= len(desc) <= 165:
            errors.append(f'{rel}: description length {len(desc)}')
        if not h.find('meta', attrs={'name': 'author'}) or not h.find('link', rel='author'):
            errors.append(f'{rel}: author metadata')
        if not h.find('meta', attrs={'property': 'og:image:alt'}) or not h.find('meta', attrs={'name': 'twitter:image:alt'}):
            errors.append(f'{rel}: social image alt')
        prose = s.select_one('article.prose')
        if not prose or len(prose.get_text(' ', strip=True).split()) < 700:
            errors.append(f'{rel}: thin article')

    # Local internal link integrity.
    for a in s.find_all('a', href=True):
        href = a['href']
        if not href.startswith('/') or href.startswith('//') or href.startswith('/#'):
            continue
        path = href.split('#')[0].split('?')[0]
        if path in ('', '/'):
            target = root / 'index.html'
        elif path.endswith('/'):
            target = root / path.lstrip('/') / 'index.html'
        else:
            target = root / path.lstrip('/')
        if not target.exists():
            errors.append(f'{rel}: broken internal link {href}')

robots_text = Path('robots.txt').read_text(encoding='utf-8')
if 'User-agent: OAI-SearchBot' not in robots_text or 'Allow: /' not in robots_text:
    errors.append('robots: OAI-SearchBot')
if 'User-agent: GPTBot' not in robots_text or 'Disallow: /' not in robots_text:
    errors.append('robots: GPTBot policy')
if 'Sitemap: https://interfacereport.com/sitemap.xml' not in robots_text:
    errors.append('robots: canonical sitemap URL')

# Parse sitemap instead of relying on string presence alone.
try:
    sitemap_root = ET.parse('sitemap.xml').getroot()
    ns = {
        'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'image': 'http://www.google.com/schemas/sitemap-image/1.1',
    }
    sitemap_urls = {
        loc.text.strip()
        for loc in sitemap_root.findall('sm:url/sm:loc', ns)
        if loc.text and loc.text.strip()
    }
    missing = canonical_urls - sitemap_urls
    extra = sitemap_urls - canonical_urls
    for url in sorted(missing):
        errors.append(f'sitemap: missing canonical {url}')
    for url in sorted(extra):
        errors.append(f'sitemap: URL has no indexable canonical page {url}')
    if any('404' in url for url in sitemap_urls):
        errors.append('sitemap: 404 URL included')

    for image_loc in sitemap_root.findall('.//image:loc', ns):
        if not image_loc.text:
            errors.append('sitemap: empty image URL')
            continue
        image_url = image_loc.text.strip()
        parsed = urlparse(image_url)
        if parsed.scheme != 'https' or parsed.netloc != 'interfacereport.com':
            errors.append(f'sitemap: non-canonical image URL {image_url}')
            continue
        local_image = root / parsed.path.lstrip('/')
        if not local_image.exists():
            errors.append(f'sitemap: missing image file {image_url}')
except Exception as exc:
    errors.append(f'sitemap: invalid XML ({exc})')

# RSS/feed must stay well-formed for discovery and subscribers.
try:
    ET.parse('feed.xml')
except Exception as exc:
    errors.append(f'feed.xml: invalid XML ({exc})')

for f in [
    'assets/agent-control-surface.png',
    'assets/patterns.png',
    'assets/trust.png',
    'assets/og-default.png',
    'feed.xml',
    '60a759d8d9915a4816e0dafdc1128b86.txt',
]:
    if not Path(f).exists():
        errors.append(f'missing {f}')

print(f'HTML files checked: {len(pages)}')
print(f'Canonical URLs checked: {len(canonical_urls)}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('All internal links, canonical/meta, JSON-LD, sitemap/image, feed, crawler and indexing checks passed.')
