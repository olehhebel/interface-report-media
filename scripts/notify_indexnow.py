"""Notify only after the public sitemap and ownership key match the release."""
import json
from pathlib import Path
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
HOST='interfacereport.com'
KEY='60a759d8d9915a4816e0dafdc1128b86'

def get(url):
    with urllib.request.urlopen(url,timeout=20) as r:
        return r.read().decode('utf-8')

if __name__=='__main__':
    expected=ET.canonicalize(from_file=ROOT/'sitemap.xml',strip_text=True)
    for attempt in range(20):
        try:
            live=ET.canonicalize(xml_data=get(f'https://{HOST}/sitemap.xml'),strip_text=True)
            if live==expected and get(f'https://{HOST}/{KEY}.txt').strip()==KEY:
                break
        except Exception as exc:
            print(f'Publication not verified yet: {exc}')
        time.sleep(30)
    else:
        raise SystemExit('Release/key not verified; nothing submitted')
    urls=[n.text for n in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')]
    assert urls and all(u.startswith(f'https://{HOST}/') for u in urls)
    body=json.dumps(dict(host=HOST,key=KEY,keyLocation=f'https://{HOST}/{KEY}.txt',urlList=urls)).encode()
    request=urllib.request.Request('https://api.indexnow.org/indexnow',data=body,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        print(f'IndexNow accepted notification: HTTP {response.status}; {len(urls)} URLs. Indexing is not guaranteed.')
