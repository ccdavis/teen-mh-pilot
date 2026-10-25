"""Slim extract of the NHIS Sample Child public-use files 2021-2024 -> data/extracts/nhis/child_2021_2024.parquet (gitignored).
Keeps identifiers/design (HHX, PSTRAT, PPSU, WTFA_C, INTV_QRT), demographics, the Washington Group anxiety/depression items (ANXFREQ_C,
DEPFREQ_C; parent-reported, ages 5-17), the 2022/2024 screen-time item (SCREENTIME_C), the 2021-2022 bullying items (BULLYVIC_C, BULLYPERP_C),
mental-health care items and a few covariates. Codes are kept as in the codebooks (7/8/9 = refused / not ascertained / don't know).
URBRRL23 (2024, 2023 NCHS scheme) is stacked into URBRRL with urb_scheme marking the vintage. Usage: uv run python scripts/download/nhis/02_extract_child.py"""
import pandas as pd, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/nhis/child"; OUT = ROOT/"data/extracts/nhis"; OUT.mkdir(parents=True, exist_ok=True)
KEEP = ["SRVY_YR","INTV_QRT","HHX","PSTRAT","PPSU","WTFA_C","AGEP_C","SEX_C","HISPALLP_C","RACEALLP_C","RATCAT_C","POVRATTC_C","IMPINCFLG_C",
        "MAXEDUCP_C","PCNTPARNTS_C","REGION","URBRRL","ANXFREQ_C","DEPFREQ_C","DISAB5_C","SCREENTIME_C","BULLYVIC_C","BULLYPERP_C","MHRX_C",
        "MHTHRPY_C","MHTHND_C","ADHDEV_C","LEARNDF_C","SCHDYMSSTC_C","SUPPORT_C","CSTATNEW","PHSTAT_C"]
parts = []
for y in (21, 22, 23, 24):
    d = pd.read_csv(RAW/f"child{y}/child{y}.csv", low_memory=False)
    scheme = 2023 if "URBRRL23" in d else 2013
    d = d.rename(columns={"URBRRL23": "URBRRL"}).reindex(columns=KEEP).assign(urb_scheme=scheme)   # missing items (e.g. SCREENTIME_C in 2021/2023) become NaN
    parts.append(d); print(f"20{y}: {len(d):,} sample children; 12-17: {d.AGEP_C.between(12,17).sum():,}; SCREENTIME_C={d.SCREENTIME_C.notna().any()}, BULLYVIC_C={d.BULLYVIC_C.notna().any()}")
x = pd.concat(parts, ignore_index=True)
for c in x.columns:
    if c != "HHX": x[c] = pd.to_numeric(x[c], errors="coerce")
x.to_parquet(OUT/"child_2021_2024.parquet", index=False); print(f"wrote {OUT/'child_2021_2024.parquet'}: {len(x):,} rows x {x.shape[1]} cols")
