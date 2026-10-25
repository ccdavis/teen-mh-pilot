"""Extract selected PISA 2015 or 2018 student- and school-questionnaire columns from the OECD SPSS files to parquet.
Run from the repository root:  uv run python scripts/download/pisa_panel/extract_sav.py 2015   (or 2018)
Inputs: data/external/pisa_panel/<year>/ zips listed in data/external/pisa_panel/README.md. The student SAV (2.7-3.4 GB) is unpacked
to the same directory, read with pyreadstat usecols (metadata first, then only the selected columns), and deleted again so that only
the verified zip is kept; the small school SAV is kept unpacked. 2015 life satisfaction (ST016Q01NA) and the bullying items are in
the separate CY6_MS_CMB_STU_QQ2.sav inside the same student zip and are merged on CNTSTUID.
Outputs: data/extracts/pisa_panel/pisa<year>_student.parquet, pisa<year>_school.parquet, _meta_<year>.pkl (labels, value labels).
"""
import sys, re, os, zipfile, pathlib, time, pyreadstat, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/extracts/pisa_panel"; OUT.mkdir(parents=True, exist_ok=True)
YEAR = int(sys.argv[1]); RAW = ROOT/f"data/external/pisa_panel/{YEAR}"
CFG = {2015: dict(stu_zip="PUF_SPSS_COMBINED_CMB_STU_QQQ.zip", stu_sav="CY6_MS_CMB_STU_QQQ.sav", stu2_sav="CY6_MS_CMB_STU_QQ2.sav", sch_zip="PUF_SPSS_COMBINED_CMB_SCH_QQQ.zip", sch_sav="CY6_MS_CMB_SCH_QQQ.sav"),
       2018: dict(stu_zip="SPSS_STU_QQQ.zip", stu_sav="STU/CY07_MSU_STU_QQQ.sav", stu2_sav=None, sch_zip="SPSS_SCH_QQQ.zip", sch_sav="SCH/CY07_MSU_SCH_QQQ.sav")}[YEAR]
EXACT = """CNT CNTRYID CNTSCHID CNTSTUID STRATUM SUBNATIO Region OECD ADMINMODE LANGTEST_QQQ Option_ICTQ Option_ECQ Option_PQ Option_TQ Option_FL Option_UH BOOKID
ST001D01T ST003D02T ST003D03T ST004D01T AGE GRADE ESCS HISEI HOMEPOS ICTRES IMMIG REPEAT W_FSTUWT SENWT PV1MATH PV1READ PV1SCIE
ST016Q01NA BELONG ANXTEST ANXMAT LIFESAT SWBP EUDMO RESILIENCE GFOFAIL WORKMAST COMPETE ATTLNACT BEINGBULLIED EMOSUPS PERFEED TEACHSUP DISCLIMA
ENTUSE HOMESCH USESCH INTICT COMPICT AUTICT SOIAICT ICTHOME ICTSCH OUTHOURS TMINS""".split()
BLOCKS = r"^(ST034Q|ST118Q|ST038Q|ST039Q|ST062Q|ST123Q|ST119Q|ST012Q0[5-9]|ST011Q0[6-7]|ST188Q|ST208Q|ST181Q|ST182Q|ST184Q|ST185Q|ST186Q|ST207Q|IC00[1-9]Q|IC01[0-7]Q|IC15[0-2]Q)"
SCH_EXACT = "CNT CNTRYID CNTSCHID STRATUM SUBNATIO Region OECD SC001Q01TA SC013Q01TA PRIVATESCH SCHLTYPE SCHSIZE CLSIZE STRATIO RATCMP1 RATCMP2 EDUSHORT STAFFSHORT STUBEHA TEACHBEHA W_SCHGRNRABWT W_FSCHWT".split()
SCH_BLOCKS = r"^(SC155Q|SC156Q|SC004Q|SC017Q|SC061Q|SC064Q|SC048Q)"

def unpack(zp, member):
    dest = RAW/pathlib.Path(member).name
    if not dest.exists():
        t0 = time.time(); print("unpacking", member, flush=True)
        with zipfile.ZipFile(zp) as z, z.open(member) as src, open(dest, "wb") as dst:
            while chunk := src.read(64 << 20): dst.write(chunk)
        print(f"  {dest.stat().st_size/1e9:.2f} GB in {time.time()-t0:.0f}s", flush=True)
    return dest

def read(sav, exact, blocks, tag):
    _, meta = pyreadstat.read_sav(str(sav), metadataonly=True); allcols = meta.column_names
    cols = [c for c in allcols if c in exact or re.match(blocks, c)]
    print(f"{tag}: {len(allcols)} columns in file; selecting {len(cols)}; requested but absent: {[c for c in exact if c not in allcols]}", flush=True)
    t0 = time.time(); df, _ = pyreadstat.read_sav(str(sav), usecols=cols, apply_value_formats=False, user_missing=False); print(f"  read {df.shape} in {time.time()-t0:.0f}s", flush=True)
    for c in df.columns:
        if df[c].dtype == "float64":
            s = df[c].dropna()
            if len(s) and (s == s.round()).all() and s.abs().max() < 2**31: df[c] = df[c].astype("Int32")
    for c in ["CNT", "STRATUM", "SUBNATIO", "Region", "PRIVATESCH", "LANGTEST_QQQ"]:
        if c in df: df[c] = df[c].astype("category")
    rows = [dict(file=f"{YEAR}_{tag}", variable=c, label=meta.column_labels[meta.column_names.index(c)], value_labels=meta.variable_value_labels.get(c)) for c in cols]
    return df, rows

if __name__ == "__main__":
    meta_rows = []
    sch = unpack(RAW/CFG["sch_zip"], CFG["sch_sav"]); df, rows = read(sch, SCH_EXACT, SCH_BLOCKS, "SCH"); meta_rows += rows
    df.to_parquet(OUT/f"pisa{YEAR}_school.parquet", index=False, compression="zstd"); print("wrote", OUT/f"pisa{YEAR}_school.parquet", df.shape)
    stu = unpack(RAW/CFG["stu_zip"], CFG["stu_sav"]); df, rows = read(stu, EXACT, BLOCKS, "STU"); meta_rows += rows
    if CFG["stu2_sav"]:
        stu2 = unpack(RAW/CFG["stu_zip"], CFG["stu2_sav"]); d2, rows2 = read(stu2, ["CNTSTUID", "ST016Q01NA"], r"^ST038Q", "STU_QQ2"); meta_rows += rows2
        df = df.merge(d2, on="CNTSTUID", how="left"); print("merged QQ2 (life satisfaction, bullying):", d2.shape, "->", df.shape)
        os.remove(stu2); print("removed", stu2)
    df.to_parquet(OUT/f"pisa{YEAR}_student.parquet", index=False, compression="zstd"); print("wrote", OUT/f"pisa{YEAR}_student.parquet", df.shape, f"{os.path.getsize(OUT/f'pisa{YEAR}_student.parquet')/1e6:.1f} MB")
    os.remove(stu); print("removed unpacked student SAV", stu, "(zip kept)")
    pd.DataFrame(meta_rows).to_pickle(OUT/f"_meta_{YEAR}.pkl"); print("wrote", OUT/f"_meta_{YEAR}.pkl")
