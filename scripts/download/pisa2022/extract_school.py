"""Extract the PISA 2022 school-questionnaire file from the OECD SPSS file to parquet (all variables; 21,629 schools).
Run from the repository root: uv run python scripts/download/pisa2022/extract_school.py
Input: data/external/pisa2022/CY08MSP_SCH_QQQ.SAV (from SCH_QQQ_SPSS.zip; see data/external/pisa2022/README.md for the OECD URLs).
Outputs: data/extracts/pisa2022/pisa2022_school.parquet and _sch_meta.pkl (variable and value labels, read by build_items_and_coverage.py).
"""
import os, time, pathlib, pyreadstat, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT/"data/external/pisa2022/CY08MSP_SCH_QQQ.SAV"; EX = ROOT/"data/extracts/pisa2022"; EX.mkdir(parents=True, exist_ok=True)
t0 = time.time()
df, meta = pyreadstat.read_sav(str(SRC), apply_value_formats=False, user_missing=False)
print("read", df.shape, f"{time.time()-t0:.0f}s")
df.to_parquet(EX/"pisa2022_school.parquet", index=False, compression="zstd")
pd.DataFrame([dict(file="SCH_QQQ", variable=c, label=meta.column_labels[i], value_labels=meta.variable_value_labels.get(c))
              for i, c in enumerate(meta.column_names)]).to_pickle(EX/"_sch_meta.pkl")
print("wrote", EX/"pisa2022_school.parquet", f"{os.path.getsize(EX/'pisa2022_school.parquet')/1e6:.1f} MB")
