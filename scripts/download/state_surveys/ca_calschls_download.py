"""Download California Healthy Kids Survey county "Main Report" PDFs from the CalSCHLS LEA report search.
Usage: uv run python scripts/download/state_surveys/ca_calschls_download.py [windows]   (default windows: 1517 1719 1921 2123 2325)

The search form at https://calschls.org/reports-data/search-lea-reports/ is a plain POST (fields sbmt=1, county=<1..58>,
county_rep=County Reports); the result table lists one row per county report with its two-school-year window and a PDF link on
data.calschls.org (e.g. Alameda_County_2123_Sec_CHKS.pdf = secondary-school CHKS, 2021-22 + 2022-23). County ids follow the
alphabetical county order of the form's <select> (1 = Alameda ... 58 = Yuba). Writes data/external/state_surveys/ca/calschls/index.csv
(county, window, url, file) and the PDFs; parse with parse_ca_calschls.py. kidsdata.org (used for 2011-13 .. 2017-19) stops at
2017-19, so these reports are the only public county-level source for 2019-21 onward."""
import os, re, sys, time, csv, requests, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/state_surveys/ca/calschls"; OUT.mkdir(parents=True, exist_ok=True)
WINDOWS = sys.argv[1:] or ["1517", "1719", "1921", "2123", "2325"]
URL = "https://calschls.org/reports-data/search-lea-reports/"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 research (teen-mh-pilot)"
page = s.get(URL, timeout=60).text
counties = dict((int(a), b) for a, b in re.findall(r'<option value="(\d+)">([^<]+)</option>', page))
assert len(counties) == 58, f"expected 58 counties in the form, found {len(counties)}"
rows = []
for cid, cname in counties.items():
    for attempt in range(3):
        try:
            r = s.post(URL, data={"sbmt": "1", "county": str(cid), "district": "", "county_rep": "County Reports"}, timeout=60); r.raise_for_status(); break
        except Exception as e:
            print("retry", cname, e); time.sleep(5)
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", r.text, flags=re.S):
        tds = re.findall(r'<td[^>]*title="([^"]*)"', m.group(1)); links = re.findall(r'href="(https://data\.calschls\.org/resources/[^"]+)"', m.group(1))
        if len(tds) >= 4 and links:
            for u in links:
                rows.append(dict(county=cname, county_id=cid, report=tds[2], years=tds[3], url=u, file=""))
    time.sleep(0.3)
print(len(rows), "county report links across", len(counties), "counties")
fails = []
for row in rows:
    win = row["years"].replace("/", ""); win = win[2:4] + win[6:8]  # 2021/2023 -> 2123
    row["window"] = win
    if win not in WINDOWS: continue
    fn = OUT/re.sub(r"[^A-Za-z0-9_.-]+", "_", row["url"].split("/")[-1]); row["file"] = fn.name
    if fn.exists() and fn.stat().st_size > 20000: continue
    for attempt in range(3):
        try:
            r = s.get(row["url"], timeout=60, headers={"Connection": "close"})
            if r.status_code == 200 and r.content[:4] == b"%PDF":
                fn.write_bytes(r.content); print(row["county"], win, len(r.content)); break
            print("bad", row["url"], r.status_code); time.sleep(3)
        except Exception as e:
            print("err", row["url"], e); time.sleep(5)
    else: fails.append(row["url"])
    time.sleep(0.4)
with open(OUT/"index.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["county", "county_id", "report", "years", "window", "url", "file"]); w.writeheader(); w.writerows(rows)
print("index written:", OUT/"index.csv")
if fails: raise SystemExit(f"{len(fails)} downloads failed: {fails}")
