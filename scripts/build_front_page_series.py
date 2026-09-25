"""Build the September 2026 original front-page analysis series."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from bs4 import BeautifulSoup
from front_page_articles import ARTICLES

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://interfacereport.com'
DATE = '2026-09-25'
DATE_ISO = '2026-09-25T15:30:00+00:00'
page = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
header = str(page.select_one('header.site-head'))
footer = str(page.select_one('footer.footer'))
assert header and footer and len(ARTICLES) == 10


def e(value: str) -> str:
    return escape(value, quote=True)


def article_html(a: dict) -> str:
    url = f"{SITE}/analysis/{a['slug']}/"
    desc = a['dek'] + ' Original analysis, primary sources and practical questions for product teams.'
    if len(desc) > 165:
        desc = desc[:164].rsplit(' ', 1)[0].rstrip(' ,;') + '.'
    if len(desc) < 120:
        desc += ' Read the full analysis at Interface Report.'
    assert 120 <= len(desc) <= 165, (a['slug'], len(desc))
    seo_title = a['seo'] + ' | Interface Report'
    if len(seo_title) > 65:
        seo_title = a['seo'][:45].rsplit(' ', 1)[0] + ' | Interface Report'
    image = f"{SITE}/assets/{a['image']}"
    author_url = f'{SITE}/authors/editorial-desk/'
    schema = {'@context':'https://schema.org','@graph':[
        {'@type':'WebPage','@id':url+'#webpage','url':url,'name':a['title'],'inLanguage':'en'},
        {'@type':'Article','@id':url+'#article','mainEntityOfPage':{'@id':url+'#webpage'},
         'headline':a['title'],'description':desc,'datePublished':DATE_ISO,'dateModified':DATE_ISO,
         'author':{'@type':'Organization','name':'Interface Report Editorial Desk','url':author_url},
         'publisher':{'@type':'Organization','name':'Interface Report','url':SITE+'/'},
         'image':image,'articleSection':a['category'],'inLanguage':'en'}]}
    note = ('<strong>Disclosure:</strong> This publication is founded by Oleh Hebel and discusses his own projects. '
            'This is a clearly identified founder portfolio analysis, not a paid third-party endorsement.'
            if a['slug'].startswith('oleh-hebel') else
            '<strong>Editorial note:</strong> Original analysis of the primary source below. No sponsor paid for or reviewed this story.')
    sections = ''.join(f'<h2>{e(h)}</h2><p>{e(p1)}</p><p>{e(p2)}</p>' for h,p1,p2 in a['sections'])
    sources = [(a['source_name'],a['source_url'])] + a.get('extra_sources',[])
    source_html = ''.join(f'<li><a href="{e(link)}" rel="noopener" target="_blank">{e(label)} ↗</a></li>' for label,link in sources)
    qs = ''.join(f'<li>{e(q)}</li>' for q in a['questions'])
    related = [b for b in ARTICLES if b is not a][:2]
    related_html = ''.join(f'<li><a href="/analysis/{e(b["slug"])}/">{e(b["title"])} →</a></li>' for b in related)
    own = ('<div class="portfolio-source-note"><strong>Explore the three products:</strong> '
           '<a href="https://superprompt.pro/" rel="sponsored noopener">Oleh Hebel &amp; Co / SuperPrompt ↗</a> · '
           '<a href="https://interfacereport.com/">Interface Report ↗</a> · '
           '<a href="https://shipindexgrow.top/" rel="sponsored noopener">Ship Index Grow ↗</a> · '
           '<a href="https://www.linkedin.com/in/olehhebel/" rel="noopener">Oleh on LinkedIn ↗</a></div>') if a['slug'].startswith('oleh-hebel') else ''
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(seo_title)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="{url}">
<meta name="author" content="Interface Report Editorial Desk"><link rel="author" href="/authors/editorial-desk/"><meta property="article:published_time" content="{DATE}"><meta property="article:modified_time" content="{DATE}"><meta property="article:section" content="{e(a['category'])}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Interface Report"><meta property="og:title" content="{e(a['title'])}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{image}"><meta property="og:image:alt" content="{e(a['image_alt'])}"><meta property="og:locale" content="en_US"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(a['title'])}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{image}"><meta name="twitter:image:alt" content="{e(a['image_alt'])}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/styles.css"><link rel="alternate" type="application/rss+xml" href="/feed.xml" title="Interface Report RSS"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><a class="skip" href="#main">Skip to content</a>{header}
<main id="main"><section class="article-hero"><div class="wrap"><div class="kicker">{e(a['category'])} · {e(a['kind'])}</div><h1>{e(a['title'])}</h1><p class="article-dek">{e(a['dek'])}</p><div class="article-byline">By <a href="/authors/editorial-desk/">Interface Report Editorial Desk</a> · <time datetime="{DATE}">September 25, 2026</time> · Original analysis</div></div></section>
<figure class="article-image"><img src="/assets/{e(a['image'])}" alt="{e(a['image_alt'])}" width="1600" height="900" decoding="async" fetchpriority="high"></figure>
<div class="wrap article-body"><aside class="aside">{e(a['kind'])}<br>Primary sources linked<br>{'Founder relationship disclosed' if own else 'No sponsor involvement'}</aside><article class="prose"><div class="disclosure">{note}</div><p class="article-intro">{e(a['intro'])}</p>{own}{sections}<h2>Questions to take into your next review</h2><ul>{qs}</ul><h2>Primary sources and further reading</h2><ul>{source_html}</ul><h2>Continue reading</h2><ul>{related_html}</ul></article></div></main>{footer}<script defer src="/assets/site-20260923b.js?v=frontpage10"></script></body></html>'''
    return html

for a in ARTICLES:
    path = ROOT / 'analysis' / a['slug'] / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    html = article_html(a)
    path.write_text(html,encoding='utf-8')
    prose = BeautifulSoup(html,'html.parser').select_one('article.prose')
    words = len(prose.get_text(' ',strip=True).split())
    if words < 700:
        raise ValueError(f"Thin article {a['slug']}: {words}")
    print(f'{a["slug"]}: {words} words')

home_path = ROOT / 'index.html'
html = home_path.read_text()
marker = '<section class="launch-ribbon launch-ribbon-blue"'
assert html.count(marker)==1
html = re.sub(r'<section class="front-page-series".*?</section>\n', '', html, count=1, flags=re.S)
cards = []
for i,a in enumerate(ARTICLES):
    if i == 5:
        cards.append('<div class="series-card series-invite"><span class="series-badge series-badge-sponsored">Sponsored slot</span><span class="series-plus" aria-hidden="true">+</span><h3>Your story could be here.</h3><p>Introduce your project to the Interface Report audience. The launch offer is $9.99/month, subject to editorial review.</p><a href="/advertise/?package=launch-monthly#commercial-intake" data-package="launch-monthly">Add your project ↗</a></div>')
    cards.append(f'<article class="series-card"><span class="series-badge">Analysis</span><span class="series-card-index">{i+1:02d} / 10 · {e(a["category"])}</span><h3>{e(a["title"])}</h3><p>{e(a["dek"])}</p><a href="/analysis/{e(a["slug"])}/">See more <span aria-hidden="true">↗</span></a></article>')
section = ('<section class="front-page-series" id="front-page-series" aria-labelledby="series-title"><div class="wrap series-head"><div><div class="kicker">The Interface Report edit · September 2026</div><h2 id="series-title">Ten ideas shaping what comes next.</h2><p>Original analysis of AI products, agent work and design systems. Swipe or scroll to explore.</p></div><div class="series-controls"><button type="button" data-series-prev aria-label="Scroll stories left">←</button><button type="button" data-series-next aria-label="Scroll stories right">→</button></div></div><div class="series-viewport" tabindex="0" aria-label="Ten featured articles and one sponsored invitation. Scroll horizontally."><div class="series-track"><div class="series-group">'+''.join(cards)+'</div></div></div></section>')
html=html.replace(marker,section+'\n'+marker,1)
if '/assets/front-page-series.css' not in html:
    html=html.replace('<link href="/assets/launch-20260925.css" rel="stylesheet"/>','<link href="/assets/launch-20260925.css" rel="stylesheet"/><link href="/assets/front-page-series.css" rel="stylesheet"/>',1)
if '/assets/front-page-series.js' not in html:
    html=html.replace('<script defer="" src="/assets/site-20260923b.js?v=frontpage10"></script>','<script defer="" src="/assets/site-20260923b.js?v=frontpage10"></script><script defer src="/assets/front-page-series.js"></script>',1)
home_path.write_text(html)

sitemap = ROOT / 'sitemap.xml'
xml=sitemap.read_text()
assert xml.count('</urlset>')==1
for a in ARTICLES:
    xml=re.sub(r'\s*<url><loc>'+re.escape(f'{SITE}/analysis/{a["slug"]}/')+r'</loc>.*?</url>', '', xml, count=1, flags=re.S)
new_urls='\n'.join(f'  <url><loc>{SITE}/analysis/{xml_escape(a["slug"])}/</loc><lastmod>{DATE}</lastmod><image:image><image:loc>{SITE}/assets/{a["image"]}</image:loc></image:image></url>' for a in ARTICLES)
xml=xml.replace('</urlset>',new_urls+'\n</urlset>')
xml=xml.replace('<loc>https://interfacereport.com/</loc><lastmod>2026-09-12</lastmod>',f'<loc>https://interfacereport.com/</loc><lastmod>{DATE}</lastmod>',1)
sitemap.write_text(xml)

feed_path = ROOT / 'feed.xml'
feed = feed_path.read_text()
for a in ARTICLES:
    feed = re.sub(r'<item><title>[^<]*</title><link>'+re.escape(f'{SITE}/analysis/{a["slug"]}/')+r'</link>.*?</item>\s*', '', feed, count=1, flags=re.S)
items = ''.join(f'<item><title>{xml_escape(a["title"])}</title><link>{SITE}/analysis/{a["slug"]}/</link><guid>{SITE}/analysis/{a["slug"]}/</guid><pubDate>Fri, 25 Sep 2026 15:30:00 GMT</pubDate><description>{xml_escape(a["dek"])}</description></item>\n' for a in ARTICLES)
feed = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '<lastBuildDate>Fri, 25 Sep 2026 15:30:00 GMT</lastBuildDate>', feed, count=1)
feed = feed.replace('</lastBuildDate>','</lastBuildDate>\n'+items,1)
feed_path.write_text(feed)

print('Built 10 articles, front-page carousel, sitemap and RSS entries.')
