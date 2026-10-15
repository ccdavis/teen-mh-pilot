"""Extract selected PISA 2022 student-questionnaire columns from the OECD SPSS file to parquet.
Run: uv run python scripts/pisa2022/extract_student.py
"""
import re, os, json, time
import pyreadstat, pandas as pd

ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2])
SRC = f"{ROOT}/data/external/pisa2022/CY08MSP_STU_QQQ.SAV"
OUT = f"{ROOT}/data/extracts/pisa2022/pisa2022_student.parquet"
META_OUT = f"{ROOT}/data/extracts/pisa2022/_stu_meta.pkl"

# Column selection: exact names + regex blocks (see notes/pisa2022.md for rationale)
EXACT = """CNT CNTRYID CNTSCHID CNTSTUID STRATUM SUBNATIO REGION OECD ADMINMODE LANGTEST_QQQ
Option_ICTQ Option_WBQ Option_FL Option_CT Option_PQ Option_TQ Option_UH BOOKID
ST001D01T ST003D02T ST003D03T ST004D01T AGE GRADE ESCS HISEI HOMEPOS ICTRES IMMIG
W_FSTUWT SENWT PV1MATH PV1READ PV1SCIE
ST016Q01NA BELONG BULLIED FEELSAFE ANXMAT LIFESAT SOCONPA
ST250Q04JA ST250Q05JA ST253Q01JA ST254Q06JA ST309Q02JA ST354Q01JA ST354Q04JA
ICTSCH ICTAVSCH ICTHOME ICTAVHOM ICTQUAL ICTSUBJ ICTWKDY ICTWKEND ICTREG ICTINFO ICTDISTR ICTEFFIC""".split()
BLOCKS = r"^(ST034Q|ST038Q|ST292Q|ST322Q|ST273Q|ST326Q|ST345Q|IC170Q|IC171Q|IC172Q|IC173Q|IC177Q|IC178Q|IC179Q|IC181Q|WB150|WB153|WB154|WB155|WB156|WB158|WB160|WB161|WB162|WB163|WB164|WB171|WB173|WB178|WB031|WB032)"

t0 = time.time()
_, meta = pyreadstat.read_sav(SRC, metadataonly=True)
allcols = meta.column_names
cols = [c for c in allcols if c in EXACT or re.match(BLOCKS, c)]
missing = [c for c in EXACT if c not in allcols]
print(f"{len(allcols)} columns in file; selecting {len(cols)}; missing from file: {missing}")

df, meta2 = pyreadstat.read_sav(SRC, usecols=cols, apply_value_formats=False, user_missing=False)
print("read", df.shape, f"{time.time()-t0:.0f}s")
# downcast floats that are integer-coded to save space
for c in df.columns:
    if df[c].dtype == "float64":
        s = df[c].dropna()
        if len(s) and (s == s.round()).all() and s.abs().max() < 2**31:
            df[c] = df[c].astype("Int32") if s.min() >= -2**31 else df[c]
for c in ["CNT","STRATUM","SUBNATIO","REGION"]:
    if c in df: df[c] = df[c].astype("category")
df.to_parquet(OUT, index=False, compression="zstd")
print("wrote", OUT, f"{os.path.getsize(OUT)/1e6:.1f} MB", f"{time.time()-t0:.0f}s")
rows = [dict(file="STU_QQQ", variable=c, label=meta.column_labels[meta.column_names.index(c)],
             value_labels=meta.variable_value_labels.get(c)) for c in cols]
pd.DataFrame(rows).to_pickle(META_OUT)
