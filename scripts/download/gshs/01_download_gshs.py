"""Download GSHS public-use microdata from the WHO NCD Microdata Repository (NADA).

For each catalog entry in the GSHS collection: save the variable list (names + labels)
from the NADA API, accept the public-use terms (click-through, no login), then download
every data file listed on the get-microdata page. Sequential, with small sleeps.
Output: data/external/gshs/<iso3>_<year>/ with data files + variables.json + files.json
"""
import json, re, sys, time, pathlib, html
import requests

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/external/gshs'
BASE = 'https://extranet.who.int/ncdsmicrodata/index.php'
UA = 'teen-mh-pilot research downloader (python-requests)'
SLEEP = 1.5

s = requests.Session(); s.headers['User-Agent'] = UA

def get(url, **kw):
    for i in range(4):
        try:
            r = s.get(url, timeout=120, **kw); r.raise_for_status(); return r
        except Exception as e:
            print('  retry', i, url, e, flush=True); time.sleep(5 * (i + 1))
    raise RuntimeError(url)

def catalog():
    r = get(f'{BASE}/api/catalog/search?collection=GSHS&ps=500&format=json')
    return r.json()['result']['rows']

def dirname(row):
    m = re.match(r'([A-Z]{3})_(\d{4})_', row['idno']) or re.match(r'(\d{4})_([A-Z]{3})_', row['idno'])
    iso, yr = (m.group(1), m.group(2)) if m.group(1).isalpha() else (m.group(2), m.group(1))
    # a few idno years disagree with the catalog year; use the idno (dataset name) year but record both
    return f'{iso}_{yr}', iso, yr

def parse_files(page):
    out = []
    # blocks: <td class="caption">Filename</td><td>NAME</td> ... href=".../download/NNN"
    for m in re.finditer(r'Filename</td>\s*<td>([^<]+)</td>(.*?)download/(\d+)"', page, re.S):
        out.append({'filename': html.unescape(m.group(1).strip()), 'fileid': m.group(3)})
    return out

def main(only=None):
    rows = catalog()
    rows.sort(key=lambda r: (r['nation'], r['year_start']))
    # catalog listing kept with the compiled tables (165 country-rounds at the 2026-09-16 download)
    import csv
    comp = ROOT / 'data/compiled/gshs'; comp.mkdir(parents=True, exist_ok=True)
    with open(comp / 'gshs_who_catalog_165.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['id', 'idno', 'nation', 'year_start', 'form_model', 'varcount', 'url'])
        for r in rows: w.writerow([r.get('id'), r.get('idno'), r.get('nation'), r.get('year_start'), r.get('form_model'), r.get('varcount'), f"{BASE}/catalog/{r.get('id')}"])
    inv = []
    for row in rows:
        d, iso, yr = dirname(row)
        if only and d not in only: continue
        dd = OUT / d; dd.mkdir(parents=True, exist_ok=True)
        meta = dd / 'catalog.json'
        print(f'== {d} id={row["id"]} {row["nation"]} {row["year_start"]}', flush=True)
        if not (dd / 'variables.json').exists():
            try:
                v = get(f'{BASE}/api/catalog/{row["idno"]}/variables').json()
                (dd / 'variables.json').write_text(json.dumps(v, indent=1))
            except Exception as e:
                print('  variables failed', e, flush=True)
            time.sleep(SLEEP)
        if (dd / 'files.json').exists() and all((dd / f['filename']).exists() for f in json.loads((dd / 'files.json').read_text())):
            print('  already done', flush=True); continue
        page = get(f'{BASE}/catalog/{row["id"]}/get-microdata').text
        tok = re.search(r'name="ncsrf" value="([0-9a-f]+)"', page)
        if tok:
            time.sleep(SLEEP)
            page = s.post(f'{BASE}/catalog/{row["id"]}/get-microdata', data={'ncsrf': tok.group(1), 'accept': 'Accept'}, timeout=120).text
        files = parse_files(page)
        if not files:
            note = 'login-required' if 'login' in page.lower() and 'download/' not in page else 'no-files-listed'
            print('  NO FILES:', note, flush=True)
            (dd / 'files.json').write_text(json.dumps({'note': note, 'files': []}))
            json.dump(row, open(meta, 'w'), indent=1)
            (dd / 'files.json').write_text(json.dumps([]))
            (dd / 'ACCESS_PROBLEM.txt').write_text(note + '\n')
            time.sleep(SLEEP); continue
        for f in files:
            dest = dd / f['filename']
            if dest.exists() and dest.stat().st_size > 0: continue
            time.sleep(SLEEP)
            r = get(f'{BASE}/catalog/{row["id"]}/download/{f["fileid"]}', stream=True)
            cd = r.headers.get('Content-Disposition', '')
            with open(dest, 'wb') as fh:
                for chunk in r.iter_content(1 << 16): fh.write(chunk)
            f['bytes'] = dest.stat().st_size; f['content_disposition'] = cd
            print(f'  {f["filename"]} {f["bytes"]:,} B', flush=True)
        (dd / 'files.json').write_text(json.dumps(files, indent=1))
        json.dump(row, open(meta, 'w'), indent=1)
        time.sleep(SLEEP)

if __name__ == '__main__':
    main(set(sys.argv[1:]) or None)
