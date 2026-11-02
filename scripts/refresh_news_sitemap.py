"""Keep News metadata limited to articles published in the last 48 hours.

Regular sitemap and article dates are never changed. An empty News sitemap is valid.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SM='http://www.sitemaps.org/schemas/sitemap/0.9'
NEWS='http://www.google.com/schemas/sitemap-news/0.9'
ET.register_namespace('',SM)
ET.register_namespace('news',NEWS)

def build(now=None):
    now=now or datetime.now(timezone.utc)
    root=ET.Element(f'{{{SM}}}urlset')
    for pattern in ('analysis/*/index.html','uk/analysis/*/index.html'):
        for p in sorted(ROOT.glob(pattern)):
            s=BeautifulSoup(p.read_text(),'html.parser')
            published=s.find('meta',property='article:published_time')
            canonical=s.find('link',rel='canonical')
            if not published or not canonical: continue
            date=datetime.fromisoformat(published['content'].replace('Z','+00:00'))
            if date.tzinfo is None: date=date.replace(tzinfo=timezone.utc)
            if not now-timedelta(days=2)<=date<=now: continue
            url=ET.SubElement(root,f'{{{SM}}}url')
            ET.SubElement(url,f'{{{SM}}}loc').text=canonical['href']
            news=ET.SubElement(url,f'{{{NEWS}}}news')
            publication=ET.SubElement(news,f'{{{NEWS}}}publication')
            ET.SubElement(publication,f'{{{NEWS}}}name').text='Interface Report'
            ET.SubElement(publication,f'{{{NEWS}}}language').text=s.html.get('lang','en')
            ET.SubElement(news,f'{{{NEWS}}}publication_date').text=published['content']
            ET.SubElement(news,f'{{{NEWS}}}title').text=s.h1.get_text(' ',strip=True)
    return root

if __name__=='__main__':
    root=build()
    ET.ElementTree(root).write(ROOT/'news-sitemap.xml',encoding='utf-8',xml_declaration=True)
    print(f'News sitemap: {len(root)} recent articles')
