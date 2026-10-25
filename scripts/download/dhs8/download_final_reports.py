"""Download the DHS Program API survey/indicator/publication listings and the free final-report PDFs of every DHS survey with
fieldwork from 2019 on (DHS-7 tail and all DHS-8 releases), so the DHS-8 mental-health chapters can be located and parsed.

Writes data/external/dhs8/api/{surveys,indicators,publications}.json and data/external/dhs8/final_reports/<SurveyId>_<FRnnn>.pdf
plus final_reports/index.csv (survey, country, year, title, url, bytes, sha256, downloaded). Re-running skips files already present
with the advertised size. Usage: uv run python scripts/download/dhs8/download_final_reports.py [--only NP2022DHS,MZ2022DHS]
"""
import sys, json, hashlib, pathlib, time, datetime as dt, requests
ROOT = pathlib.Path(__file__).resolve().parents[3]; EXT = ROOT/"data/external/dhs8"; API = "https://api.dhsprogram.com/rest/dhs"
(EXT/"api").mkdir(parents=True, exist_ok=True); (EXT/"final_reports").mkdir(parents=True, exist_ok=True)
only = set(sys.argv[sys.argv.index("--only")+1].split(",")) if "--only" in sys.argv else None
UA = {"User-Agent": "teen-mh-pilot/0.1 (research; python-requests)"}
def get_json(name, url):
    p = EXT/"api"/f"{name}.json"
    if not p.exists():
        r = requests.get(url, headers=UA, timeout=120); r.raise_for_status(); p.write_bytes(r.content)
    return json.loads(p.read_text())["Data"]
surveys = get_json("surveys", f"{API}/surveys?f=json&perpage=5000")
get_json("indicators", f"{API}/indicators?f=json&perpage=5000")
pubs = get_json("publications", f"{API}/publications?f=json&perpage=5000&surveyYearStart=2019&publicationType=FR")
def url_fr(p): return p["PublicationURL"].rstrip("/").split("/")[-1].replace(".pdf", "")
dhs = {s["SurveyId"]: s for s in surveys if s.get("SurveyType") == "DHS" and int(str(s.get("SurveyYear", "0"))[:4]) >= 2019}
rows = []
for p in sorted(pubs, key=lambda x: x.get("SurveyId", "")):
    sid = p.get("SurveyId"); 
    if sid not in dhs or p.get("PublicationTitle") != "Final Report": continue
    if only and sid not in only and not (EXT/"final_reports"/f"{sid}_{url_fr(p)}.pdf").exists(): continue   # --only limits downloads, not the index
    url = p["PublicationURL"]; fr = url.rstrip("/").split("/")[-1].replace(".pdf", ""); out = EXT/"final_reports"/f"{sid}_{fr}.pdf"; size = int(p.get("PublicationSize") or 0)
    have = out.exists() and out.stat().st_size == size
    if out.exists() and not have:  # the API's PublicationSize is sometimes wrong (FR389: 31,791,083 advertised, 28,221,468 served); trust the server's Content-Length
        try:
            h = requests.head(url, headers=UA, timeout=60, allow_redirects=True); have = out.stat().st_size == int(h.headers.get("Content-Length", -1))
            if have: print(f"  {out.name}: size matches the server's Content-Length ({out.stat().st_size:,}); API advertised {size:,}")
        except Exception as e: print(f"  HEAD failed for {url}: {e}")
    if not have and (not only or sid in only):
        for attempt in range(3):
            try:
                r = requests.get(url, headers=UA, timeout=600, stream=True); r.raise_for_status()
                with open(out, "wb") as f:
                    for chunk in r.iter_content(1 << 20): f.write(chunk)
                break
            except Exception as e:
                print(f"  retry {attempt+1} {sid} {url}: {e}"); time.sleep(5)
        print(f"downloaded {out.name} {out.stat().st_size:,} bytes (advertised {size:,})")
    if not out.exists(): continue
    rows.append(dict(survey=sid, country=dhs[sid]["CountryName"], year=dhs[sid].get("SurveyYearLabel"), title=p["PublicationTitle"], url=url, file=out.name,
                     bytes=out.stat().st_size, sha256=hashlib.sha256(out.read_bytes()).hexdigest()[:16], downloaded=dt.date.today().isoformat(), fieldwork_end=dhs[sid].get("FieldworkEnd", "")[:10], release=dhs[sid].get("ReleaseDate", "")[:10]))
import csv
with open(EXT/"final_reports/index.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} final reports listed in {EXT/'final_reports/index.csv'}")
