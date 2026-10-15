"""Download Maine Integrated Youth Health Survey county report files. Usage: uv run python scripts/download/state_surveys/me_download.py <link list>
The link list is a text file with one line per report: the survey year, a space, and the site-relative path on www.maine.gov as listed on
the MIYHS results pages (see notes/state_surveys.md). Files land in data/external/state_surveys/me/ and are parsed by parse_me.py."""
import os, re, time, requests, sys
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3]); OUT = f"{ROOT}/data/external/state_surveys/me"; os.makedirs(OUT, exist_ok=True); fails = []
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 research (teen-mh-pilot)"
for line in open(sys.argv[1]):
    yr, l = line.strip().split(' ', 1)
    name = requests.utils.unquote(l.split('/')[-1])
    ext = name.rsplit('.', 1)[-1].lower()
    safe = re.sub(r'[^A-Za-z0-9]+', '_', name.rsplit('.', 1)[0]).strip('_')
    fn = f"{OUT}/miyhs_{yr}_{safe}.{ext}"
    if os.path.exists(fn) and os.path.getsize(fn) > 5000: continue
    for a in range(3):
        try:
            r = s.get("https://www.maine.gov" + l, timeout=180)
            if r.status_code == 200 and len(r.content) > 5000:
                open(fn, 'wb').write(r.content); print(yr, safe, ext, len(r.content)); break
            print('bad', l, r.status_code); time.sleep(3)
        except Exception as e:
            print('err', l, e); time.sleep(5)
    else: fails.append(fn)
    time.sleep(0.3)
print('done')
if fails: raise SystemExit(f'{len(fails)} downloads failed: {fails}')
