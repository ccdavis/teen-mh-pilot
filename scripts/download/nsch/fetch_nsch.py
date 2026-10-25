"""Download the NSCH public-use topical files (Stata) 2016-2025 and their documentation from the Census Bureau.
Run from the repository root:  uv run python scripts/download/nsch/fetch_nsch.py [--years 2016 2017 ...]
Writes data/external/nsch/<year>/ (zip + unzipped .dta) and data/external/nsch/docs/ (variable lists, frequencies, methodology
reports, analytic guides, crosswalk) and appends a manifest to data/external/nsch/manifest.csv (url, path, bytes, sha256, date).
Nothing here is executed from the download directory; the .dta files are read later by extract_nsch.py with pandas/pyreadstat.
"""
import argparse, csv, hashlib, pathlib, sys, time, zipfile, datetime as dt
import requests

ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/nsch"
BASE = "https://www2.census.gov/programs-surveys/nsch"
YEARS = list(range(2016, 2026))
def topical_zip(y): return f"{BASE}/datasets/{y}/nsch_{y}{'e' if y == 2023 else ''}_topical_Stata.zip"
DOCS = {
    "codebook/{y}-NSCH-Topical-Variable-List.pdf": "variable list",
    "codebook/NSCH_{y}_Topical_Frequencies.pdf": "weighted/unweighted frequencies",
    "methodology/{y}-NSCH-Methodology-Report.pdf": "methodology report",
    "methodology/{y}-NSCH-FAQs.pdf": "FAQs",
}
GLOBAL_DOCS = ["methodology/NSCH-Guide-to-Multi-Year-Estimates.pdf", "methodology/NSCH-Analytic-Guide.pdf",
               "methodology/NSCH-Analysis-with-Imputed-Data-Guide.pdf", "NSCH_Crosswalk_2016-2019.xlsx",
               "NSCH_Enhancements_Technical_Document.pdf", "NSCH_Weighting_Revisions.pdf"]

def fetch(url, path, tries=3):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return path.stat().st_size, "cached"
    for k in range(tries):
        try:
            with requests.get(url, stream=True, timeout=300) as r:
                if r.status_code != 200:
                    return 0, f"HTTP {r.status_code}"
                tmp = path.with_suffix(path.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20): f.write(chunk)
                tmp.rename(path); return path.stat().st_size, "ok"
        except Exception as e:
            err = str(e); time.sleep(5)
    return 0, err

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--years", nargs="*", type=int, default=YEARS); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True); man = OUT/"manifest.csv"; rows = []
    today = dt.date.today().isoformat()
    def rec(url, path, nbytes, status, content):
        rows.append(dict(url=url, path=str(path.relative_to(ROOT)), bytes=nbytes, sha256=sha(path) if path.exists() and nbytes else "", status=status, date=today, content=content))
        print(f"{status:8s} {nbytes:>12,d}  {path.relative_to(ROOT)}", flush=True)
    for y in a.years:
        url = topical_zip(y); p = OUT/str(y)/url.rsplit("/", 1)[1]
        n, st = fetch(url, p); rec(url, p, n, st, f"NSCH {y} topical public-use file, Stata (.dta) zip")
        if n and zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as z:
                for m in z.infolist():
                    if m.filename.endswith("/") or ".." in m.filename: continue
                    dest = OUT/str(y)/pathlib.Path(m.filename).name
                    if not dest.exists():
                        with z.open(m) as src, open(dest, "wb") as f:
                            for b in iter(lambda: src.read(1 << 20), b""): f.write(b)
                    print(f"   unzip {dest.relative_to(ROOT)} {dest.stat().st_size:,d}", flush=True)
        for tmpl, what in DOCS.items():
            url = f"{BASE}/technical-documentation/{tmpl.format(y=y)}"; p = OUT/"docs"/url.rsplit("/", 1)[1]
            n, st = fetch(url, p); rec(url, p, n, st, f"NSCH {y} {what}")
    for tmpl in GLOBAL_DOCS:
        url = f"{BASE}/technical-documentation/{tmpl}"; p = OUT/"docs"/url.rsplit("/", 1)[1]
        n, st = fetch(url, p); rec(url, p, n, st, "NSCH documentation (all years)")
    new = man.exists()
    with open(man, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); 
        if not new: w.writeheader()
        w.writerows(rows)
    print("manifest:", man.relative_to(ROOT), len(rows), "rows")

if __name__ == "__main__":
    main()
