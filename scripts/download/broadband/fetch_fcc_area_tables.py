"""Pull the county rows of the FCC Form 477 "Area Table" releases (Dec 2016 - Jun 2021) from the Socrata API on opendata.fcc.gov into
data/external/broadband/fcc477/area_table/area_table_<release>.csv. Usage (repository root): uv run python scripts/download/broadband/fetch_fcc_area_tables.py
The Area Table gives, for each geography x technology set x speed tier, the population with 0, 1, 2, 3+ providers of consumer fixed
broadband at or above the tier (FCC staff block population estimates). Technology letters: a=ADSL, c=cable, f=fiber, o=other, s=satellite,
w=fixed wireless; the set "acfow" is the FCC's "fixed terrestrial" definition and "acfo" is wireline only. Speed tiers (download Mbps)
are 0.2, 4, 10, 25, 100, 250, 1000 with the FCC's paired upload thresholds (25 = 25/3, 10 = 10/1). Rows are split urban/rural and
tribal/non-tribal, which we sum. Dataset ids were taken from the Socrata catalog (api.us.socrata.com/api/catalog/v1?domains=opendata.fcc.gov
&q=Area%20Table, 2026-10-24); where a release has two versions the later "Status V2" is used.
"""
import csv, json, pathlib, sys, time, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/broadband/fcc477/area_table"; OUT.mkdir(parents=True, exist_ok=True)
RELEASES = {"2016-12": ("xv2f-wqqz", "Area Table Dec2016"), "2017-06": ("yikn-7er3", "Area Table June2017"), "2017-12": ("fnid-qg8r", "Area Table Dec, 2017 V2"),
            "2018-06": ("cekp-f8tj", "Area Table June 2018"), "2018-12": ("wucg-w9k9", "Area Table December 2018"), "2019-06": ("udcw-naqn", "Area Table June 2019 Status V2"),
            "2019-12": ("ws2a-amik", "Area Table December 2019 V1"), "2020-06": ("wxit-5xtm", "Area Table June 2020 Status V2"), "2020-12": ("ymd4-xaiz", "Area Table December 2020"),
            "2021-06": ("xvwq-qtaj", "Area Table June 2021 Status V1")}
TECHS = ["acfow", "acfo", "w", "acfosw"]
def pull(ds):
    rows, off = [], 0
    where = "type='county' AND tech in(" + ",".join(f"'{t}'" for t in TECHS) + ")"
    while True:
        q = urllib.parse.urlencode({"$where": where, "$limit": 50000, "$offset": off, "$order": "id,tech,speed,urban_rural,tribal_non"})
        url = f"https://opendata.fcc.gov/resource/{ds}.json?{q}"
        for attempt in range(4):
            try: page = json.load(urllib.request.urlopen(url, timeout=300)); break
            except Exception as e: print("  retry", attempt, e, file=sys.stderr); time.sleep(10 * (attempt + 1))
        else: raise SystemExit(f"failed {url}")
        rows += page; off += 50000
        if len(page) < 50000: break
    return rows
if __name__ == "__main__":
    for rel, (ds, name) in RELEASES.items():
        f = OUT/f"area_table_{rel}.csv"
        if f.exists() and f.stat().st_size > 1e6: print(f"ok {f.name}"); continue
        t = time.time(); rows = pull(ds)
        with open(f, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["type", "id", "tech", "speed", "urban_rural", "tribal_non", "has_0", "has_1", "has_2", "has_3more"]); w.writeheader()
            for r in rows: w.writerow({k: r.get(k, "") for k in w.fieldnames})
        print(f"{rel} {name} ({ds}): {len(rows)} county rows, {time.time()-t:.0f}s -> {f.relative_to(ROOT)}")
