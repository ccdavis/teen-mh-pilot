import os, re, time, requests, sys
OUT = "data/external/state_surveys/pa"; os.makedirs(OUT, exist_ok=True)
links = [l.strip() for l in open(sys.argv[1]) if l.strip()]
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 research (teen-mh-pilot)"
for l in links:
    yr = re.search(r'/(\d{4})-pays/', l).group(1)
    name = requests.utils.unquote(l.split('/')[-1]).replace('.pdf', '')
    safe = re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')
    fn = f"{OUT}/pays_{yr}_{safe}.pdf"
    if os.path.exists(fn) and os.path.getsize(fn) > 10000: continue
    for a in range(3):
        try:
            r = s.get("https://www.pa.gov" + l, timeout=180)
            if r.status_code == 200 and r.content[:4] == b'%PDF':
                open(fn, 'wb').write(r.content); print(yr, safe, len(r.content)); break
            print('bad', l, r.status_code); time.sleep(3)
        except Exception as e:
            print('err', l, e); time.sleep(5)
    time.sleep(0.5)
print('done')
