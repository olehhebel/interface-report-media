#!/usr/bin/env python3
"""Publish the October 12, 2026 analyses and surface the October 8 analyses site-wide.

Idempotent: re-running does not duplicate cards, feed items or sitemap entries.
"""
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from articles_20261012 import ARTICLES

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://interfacereport.com'
DATE = '2026-10-12'
DATE_ISO = '2026-10-12T10:30:00+00:00'
RSS_DATE = 'Mon, 12 Oct 2026 10:30:00 GMT'
OCT8_ISO = '2026-10-08T12:00:00+00:00'
OCT8_RSS = 'Thu, 08 Oct 2026 12:00:00 GMT'
TOPIC_NAMES = {
    'ai-agents': 'AI Agents', 'ai-products': 'AI Products', 'design-ux': 'Design & UX',
    'engineering': 'Engineering', 'human-ai': 'Human–AI', 'startups-saas': 'Startups & SaaS',
}

# The October 8 analyses were only listed in the sitemaps.
OCT8 = [
    {'slug': 'undo-is-the-feature-agent-products-are-missing', 'title': 'Undo is the feature agent products still lack',
     'dek': 'Agent interfaces are designed for starting work. Few are designed for stopping it or taking it back, and a single undo button gives false control.',
     'section': 'Human–AI', 'topic': 'human-ai'},
    {'slug': 'design-system-is-an-instruction-file-for-agents', 'title': 'Design systems become agent instruction files',
     'dek': 'Figma has opened its canvas to agents. Skills files turn a design system from a reference document into instructions an agent reads before it edits anything.',
     'section': 'Design & UX', 'topic': 'design-ux'},
    {'slug': 'when-a-prompt-can-ship-an-app-design-review', 'title': 'When prompts ship apps, design moves to review',
     'dek': "Google I/O 2026 showed agents and prompts producing working apps. The designer's job shifts from drawing the first version to deciding what is acceptable.",
     'section': 'AI Products', 'topic': 'ai-products'},
]
# Lists that were lost from the October 8 articles, restored from each article's own sections.
OCT8_LISTS = {
    'undo-is-the-feature-agent-products-are-missing': ('<p>Design for reversal in three layers:</p>', [
        'Roll back what the product controls: drafts, settings and files in a versioned workspace.',
        'Compensate for what has already left the product, with a correction the user approves.',
        'Flag what cannot be reversed before the user confirms the action.']),
    'design-system-is-an-instruction-file-for-agents': ('<p>That changes what a design system is for. Three things follow:</p>', [
        'Rules must be written so an agent can apply them, not only so a person can understand them.',
        'Components and tokens become the vocabulary an agent edits with, so naming and structure matter more.',
        'The design system team becomes responsible for deciding which changes agents may make on their own.']),
    'when-a-prompt-can-ship-an-app-design-review': ('Three review questions matter more now:</p>', [
        'What does the generated app assume about its users, its data and its permissions?',
        'What happens at the edges: empty states, failed requests, other languages and screen readers?',
        'Which agent changed each screen, and what did it assume when it did?']),
}


def e(value: str) -> str:
    return escape(value, quote=True)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


template = read('analysis/undo-is-the-feature-agent-products-are-missing/index.html')
HEADER = re.search(r'<header class="site-head">.*?</header>', template, re.S).group(0)
FOOTER = re.search(r'<footer class="footer">.*?</footer>', template, re.S).group(0)
ORG = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', template, re.S).group(1))['@graph'][:2]


def body_html(blocks) -> str:
    out = []
    for kind, value in blocks:
        if kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{e(i)}</li>' for i in value) + '</ul>')
        else:
            out.append(f'<{kind}>{e(value)}</{kind}>')
    return '\n'.join(out)


def article_html(a: dict) -> str:
    url = f"{SITE}/analysis/{a['slug']}/"
    title = f"{a['seo']} | Interface Report"
    assert len(title) <= 65, title
    assert 120 <= len(a['desc']) <= 165, (a['slug'], len(a['desc']))
    image = f"{SITE}/assets/{a['image']}"
    topic_url = f"{SITE}/topics/{a['topic']}/"
    graph = ORG + [
        {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': a['desc'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': url + '#breadcrumb'},
         'datePublished': DATE_ISO, 'dateModified': DATE_ISO, 'inLanguage': 'en'},
        {'@type': 'Article', '@id': url + '#article', 'headline': a['title'], 'description': a['desc'],
         'datePublished': DATE_ISO, 'dateModified': DATE_ISO,
         'author': {'@type': 'Person', 'name': 'Oleh Hebel', 'url': f'{SITE}/authors/oleh-hebel/'},
         'publisher': {'@id': f'{SITE}/#organization'}, 'mainEntityOfPage': {'@id': url + '#webpage'},
         'articleSection': a['section'], 'inLanguage': 'en',
         'image': {'@type': 'ImageObject', 'url': image, 'width': 1600, 'height': 900},
         'citation': [link for _, link in a['sources']]},
        {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Interface Report', 'item': f'{SITE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': a['section'], 'item': topic_url},
            {'@type': 'ListItem', 'position': 3, 'name': a['title'], 'item': url}]},
    ]
    schema = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    related = ''.join(f'<li><a href="/analysis/{s}/">{e(t)}</a></li>' for s, t in a['related'])
    sources = ''.join(f'<li><a href="{e(link)}" rel="noopener noreferrer" target="_blank">{e(label)} ↗</a></li>' for label, link in a['sources'])
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{e(title)}</title><meta name="description" content="{e(a['desc'])}"/><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"/><link rel="canonical" href="{url}"/>
<meta property="og:type" content="article"/><meta property="og:site_name" content="Interface Report"/><meta property="og:title" content="{e(a['title'])}"/><meta property="og:description" content="{e(a['desc'])}"/><meta property="og:url" content="{url}"/><meta property="og:image" content="{image}"/><meta property="og:image:type" content="image/png"/><meta property="og:image:height" content="900"/><meta property="og:image:width" content="1600"/><meta property="og:image:alt" content="{e(a['image_alt'])}"/>
<meta name="twitter:card" content="summary_large_image"/><meta name="twitter:title" content="{e(a['title'])}"/><meta name="twitter:description" content="{e(a['desc'])}"/><meta name="twitter:image" content="{image}"/><meta name="twitter:image:alt" content="{e(a['image_alt'])}"/><meta name="theme-color" content="#F6F6F2"/><meta property="og:locale" content="en_US"/><meta name="author" content="Oleh Hebel"/><meta property="article:published_time" content="{DATE_ISO}"/><meta property="article:modified_time" content="{DATE_ISO}"/><meta property="article:section" content="{e(a['section'])}"/><meta property="article:author" content="{SITE}/authors/oleh-hebel/"/><link rel="author" href="/authors/oleh-hebel/"/>
<link rel="preconnect" href="https://cdn.onlyfonts.ai" crossorigin/><link rel="stylesheet" href="https://cdn.onlyfonts.ai/e-ukraine/font.css"/><link rel="stylesheet" href="/assets/styles.css?v=glass-20260928"/><link rel="alternate" type="application/rss+xml" title="Interface Report RSS" href="/feed.xml"/><link rel="icon" type="image/png" href="/assets/interface-report-mark.png"/>
<script type="application/ld+json">{schema}</script></head>
<body><a class="skip" href="#main">Skip to content</a>{HEADER}<main id="main"><section class="article-hero"><div class="wrap"><div class="kicker"><a href="/topics/{a['topic']}/">{e(a['section'])}</a> · Analysis</div><h1>{e(a['title'])}</h1><p class="article-dek">{e(a['dek'])}</p><div class="article-byline"><span>By <a href="/authors/oleh-hebel/" rel="author">Oleh Hebel</a></span><span>Published <time datetime="{DATE_ISO}">October 12, 2026</time></span></div></div></section>
<figure class="article-image"><img alt="{e(a['image_alt'])}" decoding="async" fetchpriority="high" height="900" src="/assets/{a['image']}" width="1600"/></figure>
<div class="wrap article-body"><aside class="aside">{e(a['section'])}<br/>Independent editorial<br/>No sponsor involvement</aside><article class="prose">
<p class="answer-block"><strong>Direct answer:</strong> {e(a['answer'])}</p>
{body_html(a['body'])}
<h2>Related reading</h2><ul>{related}</ul>
<h2>Sources</h2><ul class="sources">{sources}</ul>
<p class="byline-note"><em>Author: Oleh Hebel. <a href="https://www.linkedin.com/in/olehhebel" rel="noopener noreferrer">LinkedIn</a></em></p>
</article><aside class="right-note">Coverage lane<br/>{e(a['section'])}<br/><br/>Have evidence, a correction or a source we should review?<br/><a href="/contact/">Contact the editorial desk ↗</a></aside></div></main>{FOOTER}<script defer src="/assets/site-20260923b.js?v=glass-20260928"></script></body></html>
'''


def card(a: dict, day: str) -> str:
    return (f'<a class="card" href="/analysis/{a["slug"]}/"><div class="meta"><span>{e(a["section"])}</span><span>{day}</span></div>'
            f'<h3>{e(a["title"])}</h3><p>{e(a["dek"])}</p><div class="arrow">↗</div></a>')


def section(sid: str, kicker: str, heading: str, cards: list[str]) -> str:
    return (f'<section class="section" aria-labelledby="{sid}"><div class="wrap"><div class="section-head"><div>'
            f'<div class="kicker">{kicker}</div><h2 id="{sid}">{heading}</h2></div><a href="/latest/">All stories ↗</a></div>'
            f'<div class="cards">{"".join(cards)}</div></div></section>')


NEW_SECTION = section('analysis-20261012', 'October 12, 2026 · New analysis', 'Specs, security and search for AI products.',
                      [card(a, 'Oct 12') for a in ARTICLES])
OCT8_SECTION = section('analysis-20261008', 'October 8, 2026 · Analysis', 'Reversal, agent-ready design systems and generated apps.',
                       [card(a, 'Oct 8') for a in OCT8])

# 1. Article pages.
for a in ARTICLES:
    path = ROOT / 'analysis' / a['slug'] / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(article_html(a), encoding='utf-8')

# 2. Repair the October 8 pages: missing </head>, duplicate </main>, lost lists, timezone-less dates.
for slug, (anchor, items) in OCT8_LISTS.items():
    p = f'analysis/{slug}/index.html'
    html = read(p)
    if '</head>' not in html:
        html = html.replace('</script>\n<body>', '</script></head>\n<body>', 1)
    html = html.replace('</main></main>', '</main>')
    ul = '<ul>' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>'
    if anchor in html and anchor + ul not in html:
        html = html.replace(anchor, anchor + ul, 1)
    html = html.replace('"2026-10-08"', f'"{OCT8_ISO}"')
    write(p, html)

# 3. Home and Latest: newest first, above the September 28 series.
anchor = '<section class="section" aria-labelledby="multibrand-20260928"'
for p in ('index.html', 'latest/index.html'):
    html = read(p)
    assert html.count(anchor) == 1, p
    add = ''.join(s + '\n' for s, sid in ((NEW_SECTION, 'analysis-20261012'), (OCT8_SECTION, 'analysis-20261008')) if sid not in html)
    write(p, html.replace(anchor, add + anchor, 1))

# 4. Topic pages: a section right after the hero.
by_topic: dict[str, list[str]] = {}
for a in ARTICLES:
    by_topic.setdefault(a['topic'], []).append(card(a, 'Oct 12'))
for a in OCT8:
    by_topic.setdefault(a['topic'], []).append(card(a, 'Oct 8'))
for topic, cards in by_topic.items():
    p = f'topics/{topic}/index.html'
    html = read(p)
    sid = 'october-2026'
    if sid in html:
        continue
    hero_end = html.find('</section>', html.find('class="page-hero"')) + len('</section>')
    html = html[:hero_end] + section(sid, 'October 2026 · New analysis', f'New in {e(TOPIC_NAMES[topic])}.', cards) + html[hero_end:]
    write(p, html)

# 5. Sitemap.
xml = read('sitemap.xml')
for a in ARTICLES:
    loc = f'{SITE}/analysis/{a["slug"]}/'
    if loc not in xml:
        xml = xml.replace('</urlset>', f'<url><loc>{loc}</loc><lastmod>{DATE}</lastmod><image:image><image:loc>{SITE}/assets/{a["image"]}</image:loc></image:image></url>\n</urlset>')
changed_pages = ['', 'latest/'] + [f'topics/{t}/' for t in by_topic]
for page in changed_pages:
    xml = re.sub(r'(<url><loc>' + re.escape(f'{SITE}/{page}') + r'</loc><lastmod>)[^<]*', r'\g<1>' + DATE, xml, count=1)
write('sitemap.xml', xml)

# 6. Google News sitemap.
news = read('news-sitemap.xml')
for a in ARTICLES:
    loc = f'{SITE}/analysis/{a["slug"]}/'
    if loc not in news:
        entry = (f'  <url><loc>{loc}</loc><news:news><news:publication><news:name>Interface Report</news:name><news:language>en</news:language>'
                 f'</news:publication><news:publication_date>{DATE_ISO}</news:publication_date><news:title>{xml_escape(a["title"])}</news:title></news:news></url>\n')
        news = news.replace('</urlset>', entry + '</urlset>')
write('news-sitemap.xml', news)

# 7. RSS feed: newest first.
feed = read('feed.xml')
items = ''
for group, date in ((ARTICLES, RSS_DATE), (OCT8, OCT8_RSS)):
    for a in group:
        loc = f'{SITE}/analysis/{a["slug"]}/'
        if f'<link>{loc}</link>' not in feed:
            items += (f'<item><title>{xml_escape(a["title"])}</title><link>{loc}</link><guid>{loc}</guid>'
                      f'<pubDate>{date}</pubDate><description>{xml_escape(a["dek"])}</description></item>\n')
feed = re.sub(r'<lastBuildDate>.*?</lastBuildDate>\n?', f'<lastBuildDate>{RSS_DATE}</lastBuildDate>\n' + items, feed, count=1, flags=re.S)
write('feed.xml', feed)

print('Published', len(ARTICLES), 'analyses; October 8 analyses surfaced on home, latest, topics and RSS.')
