import json,sys,urllib.request
from pathlib import Path
from urllib.parse import urlparse
key=Path('60a759d8d9915a4816e0dafdc1128b86.txt').read_text().strip()
urls=sys.argv[1:]
if not urls:
    raise SystemExit('Usage: python3 scripts/indexnow.py https://interfacereport.com/path/ [...]')
if any(urlparse(u).hostname!='interfacereport.com' for u in urls):
    raise SystemExit('Only canonical interfacereport.com URLs are accepted')
payload={'host':'interfacereport.com','key':key,'keyLocation':f'https://interfacereport.com/{key}.txt','urlList':urls}
req=urllib.request.Request('https://api.indexnow.org/indexnow',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
with urllib.request.urlopen(req,timeout=30) as r:
    print(r.status,r.read().decode(errors='replace'))
