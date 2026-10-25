"""Fetch the public county-broadband source files into data/external/broadband/ (idempotent: a file whose size equals the server's
Content-Length is skipped; a short or missing file is re-downloaded). Usage, from the repository root:
    uv run python scripts/download/broadband/fetch_broadband_files.py [--only ntia|fcc|blockpop|census2000] [--skip-big]
Sources (all checked 2026-10-24; every URL is also listed in data/external/broadband/README.md):
  ntia      NTIA State Broadband Initiative / National Broadband Map archive, https://www2.ntia.doc.gov/node/762 (round pages
            /June-2010-datasets ... /June_2014_datasets; files under /files/broadband-data/). The first page the plan cited,
            https://www.ntia.gov/page/national-broadband-map-data, returns 404; www2.ntia.gov/node/<id> redirects to www2.ntia.doc.gov.
  fcc       FCC Form 477 fixed-deployment block files for the rounds that are not on opendata.fcc.gov (Dec 2014 - Jun 2016), from
            transition.fcc.gov (www.fcc.gov itself returns 403 to curl and to headless Chromium). The Dec 2016 - Jun 2021 county
            "Area Table" summaries are pulled from opendata.fcc.gov by fetch_fcc_area_tables.py.
  blockpop  FCC staff block population estimates (2010 Census blocks; pop2010 and pop2015 per block) and the county counts file, from
            the links on the archived https://www.fcc.gov/reports-research/data/staff-block-estimates page.
  census2000 Census 2000 Summary File 1 geographic header per state (block-level POP100), needed because the June and December 2010
            SBI releases report 2000 Census blocks.
"""
import argparse, pathlib, re, sys, time, urllib.request, urllib.error
ROOT = pathlib.Path(__file__).resolve().parents[3]; EXT = ROOT/"data/external/broadband"
NTIA = "https://www2.ntia.doc.gov/files/broadband-data/"
NTIA_FILES = ["NBM_Files_Released_December_2010.xlsx", "NBM_Files_Released_June_2014.xlsx", "NBM_Broadband_Provider_List_December_2010.xlsx",
              "NBM_Broadband_Provider_List_June_2014.xlsx", "USA_DataPackage.xls", "national-broadband-map-technology-by-speed.pdf",
              "All-NBM-Analyze-Table-June-2011.zip", "All-NBM-Analyze-Table-December-2011.zip", "All-NBM-Analyze-Table-June-2012.zip",
              "All-NBM-Analyze-Table-December-2012.zip", "All-NBM-Analyze-Table-June-2013.zip", "All-NBM-Analyze-Table-Dec-2013.zip",
              "All-NBM-Analyze-Table-June-2014.zip", "All-NBM-Provider-Table-June-2014.zip"]
NTIA_BIG = ["SBDD-USA-Fall2010.zip", "All-NBM-CSV-December-2010.zip", "All-NBM-CSV-December-2013.zip", "All-NBM-CSV-June-2014.zip"]
FCC = {"US-Fixed-with-Satellite-Dec2014.zip": "https://transition.fcc.gov/form477/BroadbandData/Fixed/Dec14/Version%203/US-Fixed-with-Satellite-Dec2014.zip",
       "US-Fixed-with-Satellite-Jun2015.zip": "https://transition.fcc.gov/form477/BroadbandData/Fixed/Jun15/Version%203/US-Fixed-with-Satellite-Jun2015.zip",
       "US-Fixed-with-Satellite-Dec2015.zip": "https://transition.fcc.gov/form477/BroadbandData/Fixed/Dec15/Version%203/US-Fixed-with-Satellite-Dec2015.zip",
       "US-Fixed-with-Satellite-Jun2016.zip": "https://transition.fcc.gov/form477/BroadbandData/Fixed/Jun16/Version%202/US-Fixed-with-Satellite-Jun2016.zip"}
BLOCKPOP = {"US2015.csv.zip": "https://transition.fcc.gov/bureaus/wcb/cpd/US2015.csv.zip", "us2016.csv.zip": "https://transition.fcc.gov/bureaus/wcb/cpd/us2016.csv.zip",
            "CountyCounts2010to2016.zip": "https://transition.fcc.gov/wcb/cpd/CountyCounts2010to2016.zip"}
SF1 = "https://www2.census.gov/census_2000/datasets/Summary_File_1/"
UA = {"User-Agent": "curl/8.5.0"}
def remote_size(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=60) as r: return int(r.headers.get("Content-Length") or -1), r.status
    except urllib.error.HTTPError as e: return -1, e.code
def fetch(url, dest, log):
    dest.parent.mkdir(parents=True, exist_ok=True); size, status = remote_size(url)
    if dest.exists() and size > 0 and dest.stat().st_size == size: log.write(f"ok      {dest.stat().st_size:>12}  {dest.relative_to(ROOT)}  {url}\n"); return True
    if status != 200: log.write(f"HTTP {status}  {url}\n"); return False
    t = time.time(); tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20): f.write(chunk)
    got = tmp.stat().st_size
    if size > 0 and got != size: log.write(f"SHORT   {got} of {size}  {url}\n"); tmp.unlink(); return False
    tmp.replace(dest); log.write(f"fetched {got:>12}  {dest.relative_to(ROOT)}  {url}  ({time.time()-t:.0f}s)\n"); return True
def census2000_geo(log):
    html = urllib.request.urlopen(urllib.request.Request(SF1, headers=UA), timeout=60).read().decode()
    states = [s for s in re.findall(r'href="([A-Z][A-Za-z_]+)/"', html) if s not in {"National", "Puerto_Rico", "Virgin_Islands", "Guam", "American_Samoa", "Northern_Mariana_Islands"}]
    for s in states:
        page = urllib.request.urlopen(urllib.request.Request(SF1 + s + "/", headers=UA), timeout=60).read().decode()
        m = re.search(r'href="([a-z]{2}geo_uf1\.zip)"', page)
        if m: fetch(SF1 + s + "/" + m.group(1), EXT/"census2000"/m.group(1), log)
        else: log.write(f"no geo file listed for {s}\n")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["ntia", "fcc", "blockpop", "census2000"]); ap.add_argument("--skip-big", action="store_true", help="skip the 0.5-2 GB NTIA national CSV zips")
    a = ap.parse_args(); log = sys.stdout
    if a.only in (None, "ntia"):
        for f in NTIA_FILES + ([] if a.skip_big else NTIA_BIG): fetch(NTIA + f, EXT/"ntia_nbm"/f, log)
    if a.only in (None, "fcc"):
        for f, u in FCC.items(): fetch(u, EXT/"fcc477"/f, log)
    if a.only in (None, "blockpop"):
        for f, u in BLOCKPOP.items(): fetch(u, EXT/"blockpop"/f, log)
    if a.only in (None, "census2000"): census2000_geo(log)
