"""Extract selected PISA 2012 student- and school-questionnaire columns from the OECD fixed-width text files to parquet.
Run from the repository root: uv run python scripts/download/pisa_panel/extract_2012.py
Inputs (see data/external/pisa_panel/README.md): data/external/pisa_panel/2012/INT_STU12_DEC03.zip (INT_STU12_DEC03.txt, 1.13 GB,
read directly from the zip in chunks so the text file is never unpacked), INT_SCQ12_DEC03.zip, and the OECD SPSS control files
PISA2012_SPSS_student.sps / PISA2012_SPSS_school.sps (CP1252), which give column positions, variable labels, value labels and
missing-value codes. Outputs: data/extracts/pisa_panel/pisa2012_student.parquet, pisa2012_school.parquet, _meta_2012.pkl.
"""
import re, io, zipfile, pathlib, time, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/pisa_panel/2012"; OUT = ROOT/"data/extracts/pisa_panel"; OUT.mkdir(parents=True, exist_ok=True)

STU_COLS = """CNT SUBNATIO STRATUM OECD NC SCHOOLID StIDStd ST01Q01 ST03Q02 ST04Q01 ST08Q01 ST09Q01 ST115Q01 ST28Q01 ST57Q01
ST42Q01 ST42Q02 ST42Q03 ST42Q04 ST42Q05 ST42Q06 ST42Q07 ST42Q08 ST42Q09 ST42Q10 ST88Q01 ST88Q02 ST88Q03 ST88Q04
ST87Q01 ST87Q02 ST87Q03 ST87Q04 ST87Q05 ST87Q06 ST87Q07 ST87Q08 ST87Q09
IC01Q01 IC01Q02 IC01Q03 IC01Q04 IC01Q05 IC01Q06 IC01Q07 IC01Q08 IC01Q09 IC01Q10 IC01Q11 IC02Q01 IC02Q02 IC02Q03 IC02Q04 IC02Q05 IC02Q06 IC02Q07
IC03Q01 IC04Q01 IC05Q01 IC06Q01 IC07Q01 IC08Q01 IC08Q02 IC08Q03 IC08Q04 IC08Q05 IC08Q06 IC08Q07 IC08Q08 IC08Q09 IC08Q11
IC09Q01 IC09Q02 IC09Q03 IC09Q04 IC09Q05 IC09Q06 IC09Q07 IC10Q01 IC10Q02 IC10Q03 IC10Q04 IC10Q05 IC10Q06 IC10Q07 IC10Q08 IC10Q09
IC11Q01 IC11Q02 IC11Q03 IC11Q04 IC11Q05 IC11Q06 IC11Q07
AGE GRADE ANXMAT ATSCHL ATTLNACT BELONG ENTUSE ESCS HOMSCH ICTATTNEG ICTATTPOS ICTHOME ICTSCH IMMIG USESCH PV1MATH W_FSTUWT""".split()
SCH_COLS = "CNT SUBNATIO STRATUM OECD NC SCHOOLID SC01Q01 SC03Q01 SC11Q01 SC11Q02 SC11Q03 SC13Q01 SC13Q02 SC13Q03 SC14Q07 SC14Q08 SC14Q09 SC40Q01 COMPWEB RATCMP15 SCHLTYPE SCHSIZE STRATIO W_FSCHWT".split()

def parse_sps(path):
    """Return (layout, labels, value_labels, missing) from an OECD PISA 2012 SPSS control file."""
    txt = path.read_text(encoding="cp1252").replace("\r", "")
    layout = {}
    for m in re.finditer(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)\s*-\s*(\d+)\s*\((A|F,\d+)\)", txt, re.M):
        layout[m.group(1)] = (int(m.group(2)) - 1, int(m.group(3)), m.group(4))   # 0-based start, end exclusive, format
    labels = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\s*/?([A-Za-z_][A-Za-z0-9_]*)\s+\"([^\"]*)\"\s*$", txt, re.M)}
    # value labels: blocks start with "/VAR" (or "/VAR1 VAR2 ...") followed by lines of  code "label"
    vlab = {}
    for blk in re.finditer(r"^\s*/([A-Za-z_][A-Za-z0-9_ ]*?)\s*\n((?:\s*['\"]?[0-9A-Za-z.\-]+['\"]?\s+\"[^\"]*\"\s*\n?)+)", txt, re.M):
        names = blk.group(1).split(); pairs = re.findall(r"['\"]?([0-9A-Za-z.\-]+)['\"]?\s+\"([^\"]*)\"", blk.group(2))
        for n in names:
            vlab.setdefault(n, {}).update({k: v for k, v in pairs})
    missing = {}
    for m in re.finditer(r"^Missing values\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", txt, re.M | re.I):
        missing[m.group(1)] = [x.strip().strip("'") for x in m.group(2).split(",")]
    return layout, labels, vlab, missing

def read_fwf_zip(zip_path, member, layout, cols, chunk=200_000):
    specs = [layout[c][:2] for c in cols]; fmts = {c: layout[c][2] for c in cols}
    dtype = {c: str for c in cols if fmts[c] == "A"}
    t0 = time.time(); parts = []
    with zipfile.ZipFile(zip_path) as z, z.open(member) as fh:
        for i, ch in enumerate(pd.read_fwf(io.TextIOWrapper(fh, encoding="latin-1"), colspecs=specs, names=cols, header=None, dtype=dtype, chunksize=chunk, na_filter=True)):
            parts.append(ch); print(f"  chunk {i+1}: {sum(len(p) for p in parts):,} rows, {time.time()-t0:.0f}s", flush=True)
    return pd.concat(parts, ignore_index=True)

def clean(df, cols, layout, missing):
    for c in cols:
        if layout[c][2] == "A":
            df[c] = df[c].astype("string").str.strip()
            if c in missing: df.loc[df[c].isin(missing[c]), c] = pd.NA
        else:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            if c in missing: df.loc[df[c].isin([float(x) for x in missing[c]]), c] = np.nan
    # hours categories are stored as 2-character strings ("01".."07") in IC05-IC07: convert to integers
    for c in [c for c in cols if c in ("IC05Q01", "IC06Q01", "IC07Q01")]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in df.columns:
        if df[c].dtype == "float64":
            s = df[c].dropna()
            if len(s) and (s == s.round()).all() and s.abs().max() < 2**31: df[c] = df[c].astype("Int32")
    return df

if __name__ == "__main__":
    meta_rows = []
    for name, cols, zp, member, sps, out in [
        ("STU", STU_COLS, RAW/"INT_STU12_DEC03.zip", "INT_STU12_DEC03.txt", RAW/"PISA2012_SPSS_student.sps", OUT/"pisa2012_student.parquet"),
        ("SCH", SCH_COLS, RAW/"INT_SCQ12_DEC03.zip", "INT_SCQ12_DEC03.txt", RAW/"PISA2012_SPSS_school.sps", OUT/"pisa2012_school.parquet")]:
        layout, labels, vlab, missing = parse_sps(sps)
        miss = [c for c in cols if c not in layout]; assert not miss, f"{name}: not in control file: {miss}"
        print(f"{name}: {len(layout)} variables in control file; reading {len(cols)} from {zp.name}")
        df = clean(read_fwf_zip(zp, member, layout, cols), cols, layout, missing)
        for c in ["CNT", "SUBNATIO", "STRATUM", "NC"]:
            if c in df: df[c] = df[c].astype("category")
        df.to_parquet(out, index=False, compression="zstd"); print("wrote", out, df.shape)
        meta_rows += [dict(file=f"2012_{name}", variable=c, label=labels.get(c, ""), value_labels=vlab.get(c), missing=missing.get(c)) for c in cols]
    pd.DataFrame(meta_rows).to_pickle(OUT/"_meta_2012.pkl"); print("wrote", OUT/"_meta_2012.pkl")
