"""Publish two original bilingual analyses without rebuilding historical articles."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import format_datetime
import html
import json
import math
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://interfacereport.com'
DATE = '2026-11-02T21:00:00+02:00'
SM = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XH = 'http://www.w3.org/1999/xhtml'
ET.register_namespace('', SM)
ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
ET.register_namespace('xhtml', XH)
posts = json.loads((ROOT / 'scripts/editorial_20261102.json').read_text())
template = (ROOT / 'analysis/ai-product-discovery-story-before-seo-hype/index.html').read_text()
entries = []

def meta(s, key, value):
    attr = 'property' if ':' in key and not key.startswith('twitter:') else 'name'
    tag = s.head.find('meta', attrs={attr: key})
    if tag is None:
        tag = s.new_tag('meta', attrs={attr: key})
        s.head.append(tag)
    tag['content'] = value

for post in posts:
    slug = post['slug']
    urls = {lang: BASE + ('/uk' if lang == 'uk' else '') + '/analysis/' + slug + '/' for lang in ('en', 'uk')}
    topic = 'Design & UX' if post['topic'] == 'design-ux' else 'Engineering'
    for lang in ('en', 'uk'):
        d = post[lang]
        s = BeautifulSoup(template, 'html.parser')
        s.html['lang'] = lang
        s.title.string = d['title'] + ' | Interface Report'
        s.head.find('link', rel='canonical')['href'] = urls[lang]
        image = BASE + '/assets/' + slug + '.png'
        alt = ('Interface Report editorial framework: status, control, recovery.' if post['topic'] == 'design-ux'
               else 'Interface Report editorial framework: page, endpoint, delivery.')
        for key, val in {'description':d['description'], 'og:title':s.title.string, 'twitter:title':s.title.string,
                         'og:description':d['description'], 'twitter:description':d['description'],
                         'og:url':urls[lang], 'og:image':image, 'twitter:image':image,
                         'og:image:alt':alt, 'twitter:image:alt':alt,
                         'og:locale':'uk_UA' if lang == 'uk' else 'en_US',
                         'article:published_time':DATE,'article:modified_time':DATE,'article:section':topic}.items():
            meta(s,key,str(val))
        for code, url in {**urls, 'x-default':urls['en']}.items():
            s.head.append(s.new_tag('link', rel='alternate', hreflang=code, href=url))
        s.h1.string = d['title']
        s.select_one('.article-dek').string = d['dek']
        kicker = s.select_one('.article-hero .kicker')
        kicker.clear()
        a = s.new_tag('a', href='/topics/' + post['topic'] + '/')
        a.string = topic
        kicker.append(a)
        kicker.append(' · ' + ('Аналіз' if lang == 'uk' else 'Analysis'))
        prose = s.select_one('article.prose')
        prose.clear()
        lead = ('Авторський аналіз і практичні рекомендації. Приклади умовні; платного замовника немає.' if lang == 'uk'
                else 'Original analysis and practical recommendations. Examples are hypothetical; no sponsor commissioned this article.')
        intro = '<p class="disclosure">' + lead + '</p>'
        intro += '<nav aria-label="' + ('Зміст' if lang == 'uk' else 'On this page') + '"><strong>' + ('Зміст' if lang == 'uk' else 'On this page') + '</strong><ol>'
        for i, sec in enumerate(d['sections']):
            intro += f'<li><a href="#section-{i+1}">{html.escape(sec[0])}</a></li>'
        intro += '</ol></nav>'
        for i, sec in enumerate(d['sections']):
            intro += f'<h2 id="section-{i+1}">{html.escape(sec[0])}</h2>'
            intro += ''.join('<p>' + html.escape(p) + '</p>' for p in sec[1:])
        intro += '<h2>' + ('Джерела та метод' if lang == 'uk' else 'Sources and method') + '</h2><p>'
        intro += ('Перевірено 2 листопада 2026 року. Рекомендації редакції слід перевірити у власному продукті. ' if lang == 'uk'
                  else 'Sources checked November 2, 2026. Editorial recommendations require validation in your own product. ')
        intro += ' · '.join(f'<a href="{html.escape(url)}">{html.escape(label)}</a>' for label,url in post['sources']) + '</p>'
        intro += '<p>' + ('Пов’язаний матеріал: ' if lang == 'uk' else 'Related analysis: ')
        other = next(p for p in posts if p['slug'] != slug)
        intro += f'<a href="{("/uk" if lang=="uk" else "")}/analysis/{other["slug"]}/">{html.escape(other[lang]["title"])}</a></p>'
        intro += '<div class="note-box">' + ('Маєш AI-продукт або дизайн-студію? ' if lang=='uk' else 'Building an AI product or design studio? ')
        intro += '<a href="/advertise/">' + ('Подай проєкт на розгляд для рекламної історії' if lang=='uk' else 'Apply for a clearly labeled sponsored story') + '</a>.</div>'
        prose.append(BeautifulSoup(intro,'html.parser'))
        words = len(prose.get_text(' ',strip=True).split())
        minutes = math.ceil(words/180)
        s.select_one('.article-byline').clear()
        s.select_one('.article-byline').append(BeautifulSoup(f'<span><a href="/authors/oleh-hebel/">Oleh Hebel</a></span><span><time datetime="{DATE}">{"2 листопада 2026" if lang=="uk" else "November 2, 2026"}</time></span><span>{minutes} {"хв читання" if lang=="uk" else "min read"}</span>', 'html.parser'))
        s.select_one('.article-image img')['src'] = '/assets/' + slug + '.png'
        s.select_one('.article-image img')['alt'] = alt
        s.figcaption.string = ('Авторська схема Interface Report; не результати вимірювань.' if lang=='uk' else 'Original Interface Report framework; not measured performance data.')
        s.select_one('.aside').string = topic + ' · ' + ('Авторський аналіз' if lang=='uk' else 'Original analysis')
        switch = s.new_tag('nav', attrs={'aria-label':'Мова статті' if lang=='uk' else 'Article language', 'class':'article-language'})
        switch['style'] = 'display:flex;gap:16px;margin:16px 0;font-weight:600'
        for code in ('en','uk'):
            a = s.new_tag('a', href=urls[code], hreflang=code, lang=code)
            a.string = 'УКР' if code=='uk' else 'EN'
            if code==lang: a['aria-current']='page'
            switch.append(a)
        s.select_one('.article-hero .wrap').append(switch)
        data = json.loads(s.find('script', type='application/ld+json').string)
        for node in data['@graph']:
            typ = node['@type']
            if typ in ('WebPage','Article','BreadcrumbList'):
                old = BASE+'/analysis/ai-product-discovery-story-before-seo-hype/'
                # Replace identifiers and nested links without touching historical source files.
                node.update(json.loads(json.dumps(node,ensure_ascii=False).replace(old,urls[lang])))
            if typ in ('WebPage','Article'):
                node.update(datePublished=DATE,dateModified=DATE,inLanguage=lang)
            if typ=='WebPage': node.update(url=urls[lang],name=str(s.title.string),description=d['description'])
            if typ=='Article':
                node.update(headline=d['title'],description=d['description'],articleSection=topic,
                            citation=[v for _,v in post['sources']],wordCount=words,timeRequired=f'PT{minutes}M',
                            keywords=['AI accessibility','streaming UX'] if post['topic']=='design-ux' else ['static hosting','contact forms','website migration'])
                node['image'].update(url=image,caption=alt)
            if typ=='BreadcrumbList':
                node['itemListElement'][1].update(name=topic,item=BASE+'/topics/'+post['topic']+'/')
                node['itemListElement'][2].update(name=d['title'],item=urls[lang])
        s.find('script',type='application/ld+json').string=json.dumps(data,ensure_ascii=False)
        if lang=='uk':
            translations={'Skip to content':'До вмісту','Latest':'Останнє','AI Products':'AI-продукти','Human–AI':'Людина–ШІ','Agents':'Агенти','Design & UX':'Дизайн та UX','Commercial Deck ↗':'Рекламна пропозиція ↗','Publication':'Видання','About':'Про нас','Contact':'Контакти','Standards':'Стандарти','Editorial Guidelines':'Редакційні принципи','Corrections':'Виправлення','Sponsored Content':'Рекламні матеріали','Submissions':'Подати матеріал','Business':'Співпраця','Advertise':'Реклама','Media Kit':'Медіакіт','Privacy':'Приватність','Terms':'Умови'}
            for text in list(s.find_all(string=True)):
                if text.parent.name not in ('script','style') and str(text).strip() in translations:
                    text.replace_with(translations[str(text).strip()])
            s.select_one('.right-note').clear()
            s.select_one('.right-note').append(BeautifulSoup('Маєш уточнення або джерело?<br/><a href="/contact/">Напиши редакції ↗</a>','html.parser'))
        path=ROOT/('uk' if lang=='uk' else '')/'analysis'/slug/'index.html'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(str(s),encoding='utf-8')
        entries.append(dict(url=urls[lang],lang=lang,title=d['title'],description=d['description'],path=path,urls=urls,topic=post['topic']))
        print(lang,slug,words,'words')

# Add a newest-first section; retain every existing story and section.
cards='<section class="section" id="editorial-20261102"><div class="wrap"><div class="section-head"><div><div class="kicker">November 2, 2026 · EN / УКР</div><h2>Ship the experience, not just the demo.</h2></div></div><div class="cards">'
for e in entries:
    if e['lang']!='en': continue
    cards+=f'<article class="card"><h3><a href="{e["url"]}">{html.escape(e["title"])}</a></h3><p>{html.escape(e["description"])}</p><a href="{e["urls"]["en"]}" lang="en">Read in English ↗</a> · <a href="{e["urls"]["uk"]}" lang="uk" hreflang="uk">Читати українською ↗</a></article>'
cards+='</div></div></section>'
for name in ('index.html','latest/index.html','authors/oleh-hebel/index.html','topics/design-ux/index.html','topics/engineering/index.html'):
    p=ROOT/name
    s=BeautifulSoup(p.read_text(),'html.parser')
    old=s.find(id='editorial-20261102')
    if old: old.decompose()
    main=s.find('main')
    # Homepage: after hero. Other collections: after introductory section.
    section=main.find('section',recursive=False)
    if section: section.insert_after(BeautifulSoup(cards,'html.parser'))
    else: main.insert(0,BeautifulSoup(cards,'html.parser'))
    p.write_text(str(s),encoding='utf-8')

sp=ROOT/'sitemap.xml'
tree=ET.parse(sp)
for e in entries:
    for old in list(tree.getroot()):
        if old.findtext(f'{{{SM}}}loc')==e['url']: tree.getroot().remove(old)
    node=ET.SubElement(tree.getroot(),f'{{{SM}}}url')
    ET.SubElement(node,f'{{{SM}}}loc').text=e['url']
    ET.SubElement(node,f'{{{SM}}}lastmod').text=DATE
    for code,url in {**e['urls'],'x-default':e['urls']['en']}.items():
        ET.SubElement(node,f'{{{XH}}}link',rel='alternate',hreflang=code,href=url)
tree.write(sp,encoding='utf-8',xml_declaration=True)
feed=ET.parse(ROOT/'feed.xml')
channel=feed.getroot().find('channel')
for e in reversed(entries):
    for old in list(channel.findall('item')):
        if old.findtext('link')==e['url']: channel.remove(old)
    item=ET.Element('item')
    for key,val in [('title',e['title']),('link',e['url']),('guid',e['url']),('description',e['description']),('pubDate',format_datetime(datetime.fromisoformat(DATE)))]:
        ET.SubElement(item,key).text=val
    channel.insert(0,item)
feed.write(ROOT/'feed.xml',encoding='utf-8',xml_declaration=True)
