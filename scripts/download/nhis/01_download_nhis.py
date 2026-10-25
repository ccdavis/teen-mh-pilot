"""Download the NHIS public-use files used by the NHIS section (Sample Child 2021-2024 CSV + codebooks + survey descriptions) and the
NHIS-Teen documentation and public aggregate estimates (NHIS-Teen microdata are RDC-only; see data/external/nhis/README.md).
Idempotent: skips files already present; writes data/external/nhis/manifest.csv (url, path, bytes, sha256, downloaded).
Usage: uv run python scripts/download/nhis/01_download_nhis.py [--force]"""
import sys, hashlib, pathlib, zipfile, datetime, csv, requests
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/nhis"
FTP = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS"
FILES = []
for y in (2021, 2022, 2023, 2024):
    yy = str(y)[2:]
    FILES.append((f"{FTP}/Datasets/NHIS/{y}/child{yy}csv.zip", f"child/child{yy}csv.zip"))
    for doc in ("Child-codebook.pdf", "Child-summary.pdf", "srvydesc-508.pdf"):
        FILES.append((f"{FTP}/Dataset_Documentation/NHIS/{y}/{doc}", f"docs/{y}/{doc}"))
    FILES.append((f"{FTP}/Dataset_Documentation/NHIS/{y}/" + ("checksum.pdf" if y == 2021 else "Checksum-Filelist.pdf"), f"docs/{y}/" + ("checksum.pdf" if y == 2021 else "Checksum-Filelist.pdf")))
for y in (2021, 2022):
    FILES.append((f"{FTP}/Dataset_Documentation/NHIS/{y}/Sponsored-Content-508.pdf", f"docs/{y}/Sponsored-Content-508.pdf"))
TEEN = "https://www.cdc.gov/nchs/data/nhis/teen"
FILES += [
    (f"{TEEN}/NHIS-teen-survey-instrument-508.pdf", "teen/NHIS-teen-survey-instrument-508.pdf"),
    (f"{TEEN}/NHIS-Teen-18m-Methodology-Report.pdf", "teen/NHIS-Teen-18m-Methodology-Report.pdf"),
    (f"{TEEN}/NHIS-Teen-Weighting-18m-Report.pdf", "teen/NHIS-Teen-Weighting-18m-Report.pdf"),
    (f"{TEEN}/NHIS-Teen-30m-Methodology-Report.pdf", "teen/NHIS-Teen-30m-Methodology-Report.pdf"),
    (f"{TEEN}/NHIS-Teen-Weighting-30m-Report.pdf", "teen/NHIS-Teen-Weighting-30m-Report.pdf"),
    ("https://www.cdc.gov/nchs/media/pdfs/2026/01/NHIS-Teen-Citation-List.pdf", "teen/NHIS-Teen-Citation-List.pdf"),
    ("https://wwwn.cdc.gov/NHISDataQueryTool/NHIS_Teen/SHS_Tech_Notes_8.30.24.pdf", "teen/SHS_Tech_Notes_8.30.24.pdf"),
    ("https://www.cdc.gov/nchs/nhis/teen/index.html", "teen/nhis_teen_page.html"),
    ("https://wwwn.cdc.gov/NHISDataQueryTool/NHIS_Teen/index.html", "teen/query_tool_index.html"),
    ("https://data.cdc.gov/api/views/5pqj-rvh4/rows.csv?accessType=DOWNLOAD", "teen/data_cdc_gov_5pqj-rvh4.csv"),
    ("https://data.cdc.gov/api/views/5pqj-rvh4.json", "teen/data_cdc_gov_5pqj-rvh4_meta.json"),
    ("https://www.cdc.gov/nchs/data/nhsr/nhsr172.pdf", "teen/nhsr172.pdf"),
    ("https://www.cdc.gov/nchs/data/nhsr/nhsr206.pdf", "teen/nhsr206.pdf"),
    ("https://www.cdc.gov/nchs/data/nhsr/nhsr219.pdf", "teen/nhsr219.pdf"),
    ("https://www.cdc.gov/nchs/data/databriefs/db513.pdf", "teen/db513.pdf"),
    ("https://www.cdc.gov/nchs/data/databriefs/db514.pdf", "teen/db514.pdf"),
]
force = "--force" in sys.argv; rows = []
for url, rel in FILES:
    p = OUT/rel; p.parent.mkdir(parents=True, exist_ok=True)
    if force or not p.exists() or p.stat().st_size == 0:
        # www.cdc.gov rejects browser-like User-Agents sent without full browser headers; a plain python-requests UA works (see data/external/yrbs/README.md)
        r = requests.get(url, timeout=600); r.raise_for_status(); p.write_bytes(r.content); print(f"downloaded {rel} ({len(r.content):,} bytes)")
    rows.append(dict(url=url, path=rel, bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     downloaded=datetime.datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()))
    if rel.endswith(".zip"):
        with zipfile.ZipFile(p) as z: z.extractall(p.parent/p.stem.replace("csv", ""))
with open(OUT/"manifest.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} files, {sum(r['bytes'] for r in rows):,} bytes; manifest at {OUT/'manifest.csv'}")
