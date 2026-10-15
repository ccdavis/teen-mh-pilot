"""Download Illinois Youth Survey county report PDFs. Usage: uv run python scripts/download/state_surveys/il_download.py <link list>
The link list is a text file with one report URL (or site-relative path) per line, as listed on the IYS county-report pages
(https://iys.cprd.illinois.edu/; see notes/state_surveys.md). Files land in data/external/state_surveys/il/ and are parsed by parse_il.py."""
import os, re, time, requests, sys
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3]); OUT = f"{ROOT}/data/external/state_surveys/il"; os.makedirs(OUT, exist_ok=True); fails = []
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 research (teen-mh-pilot)"
for l in open(sys.argv[1]):
    l = l.strip()
    if not l: continue
    m = re.search(r'Cnty(\d\d)_([^/]+)\.(pdf|html)$', l, re.I)
    if not m: continue
    yr = 2000 + int(m.group(1)); ext = m.group(3).lower()
    safe = re.sub(r'[^A-Za-z0-9]+', '_', requests.utils.unquote(m.group(2))).strip('_')
    fn = f"{OUT}/iys_{yr}_{safe}.{ext}"
    if os.path.exists(fn) and os.path.getsize(fn) > 5000: continue
    url = l if l.startswith('http') else 'https://iys.cprd.illinois.edu' + l
    for a in range(3):
        try:
            r = s.get(url.replace(' ', '%20'), timeout=180)
            if r.status_code == 200 and len(r.content) > 5000:
                open(fn, 'wb').write(r.content); print(yr, safe, len(r.content)); break
            print('bad', url, r.status_code); time.sleep(3)
        except Exception as e:
            print('err', url, e); time.sleep(5)
    else: fails.append(fn)
    time.sleep(0.3)
print('done')
if fails: raise SystemExit(f'{len(fails)} downloads failed: {fails}')
