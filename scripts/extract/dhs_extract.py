"""IPUMS DHS -> slim parquet extracts for the DHS-8 mental-health analyses (generalizes dhs_extract.sql to every available sample).

Input (either layout):
  data/ipums/dhs/_full/<sample>/*.parquet   full IPUMS DHS sample files copied from the IPUMS server (gitignored; one file per sample)
  data/ipums/dhs/<sample>.parquet            a projected sample file (a standard IPUMS DHS extract converted to parquet also works)
Step 1 projects the needed columns of every _full sample into data/ipums/dhs/<sample>.parquet (missing columns are written as NULL).
Step 2 writes data/extracts/dhs/<sample>_slim.parquet with the common analysis columns for every sample that carries at least one
mental-health variable (DEPRESSIONSCORE, GADSCORE, DEPRESSIONDIAG or their MN-suffixed men's versions). Men's files (*mr) use the IPUMS
DHS "MN" suffix (AGEMN, PERWEIGHTMN, ...); the slim files carry the women's names plus SEX = 'women' | 'men'.
Codes are left as delivered by IPUMS DHS (DEPRESSIONSCORE/GADSCORE 99 = not in the module universe; INTERNETMO 0 not at all, 1 < weekly,
2 weekly+, 3 almost daily, 9 NIU; INTERNETEVYR 0 never, 11 last 12 months, 12 before that, 99 NIU; CELLPHONESMART 0/1, 9 NIU = no own
phone; URBAN 1 urban 2 rural; WEALTHQ 1-5; EDUCLVL 0 none 1 primary 2 secondary 3 higher). PERWEIGHT has six implied decimals.
Usage: uv run python scripts/extract/dhs_extract.py            (prints a per-sample summary; rerun is idempotent)
"""
import duckdb, glob, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]; IP = ROOT/"data/ipums/dhs"; OUT = ROOT/"data/extracts/dhs"; OUT.mkdir(parents=True, exist_ok=True)
DESIGN = ["SAMPLE", "COUNTRY", "YEAR", "IDHSPSU", "IDHSSTRATA", "CLUSTERNO", "PERWEIGHT", "DVWEIGHT", "AGE", "URBAN", "WEALTHQ", "EDUCLVL", "MARSTAT"]
MH = ["DEPRESSIONSCORE", "DEPRESSIONREFER", "GADSCORE", "DEPRESSIONDIAG", "DEPRESSIONTR", "ANXIETYDIAG"]
ITEMS = ["GADNERVOUS2WK", "GADSTOPWORRY2WK", "GADWORRYMUCH2WK", "GADRELAX2WK", "GADRESTLESS2WK", "GADIRRITABLE2WK", "GADDREAD2WK",
         "DEPINTEREST2WK", "DEPFEELSAD2WK", "DEPSLEEPPROB2WK", "DEPLOWENERGY2WK", "DEPAPPETITE2WK", "DEPBADSELF2WK", "DEPFOCUS2WK", "DEPMOVE2WK", "DEPHURTSELF2WK"]
EXPO = ["INTERNETEVYR", "INTERNETMO", "CELLPHONSELF", "CELLPHONESMART", "MOBPHONE", "TVFQ", "RADIOFQ"]
WANT = DESIGN + MH + ITEMS + EXPO
NOSUFFIX = {"SAMPLE", "COUNTRY", "YEAR", "IDHSPSU", "IDHSSTRATA", "MOBPHONE"}   # household/sample-level names are the same in men's files

def schema(f): return [r[0] for r in duckdb.sql(f"select name from parquet_schema('{f}') where num_children is null").fetchall()]

def project(sample, src):
    """Write data/ipums/dhs/<sample>.parquet with WANT columns (NULL where the sample lacks them); men's files map <NAME>MN -> <NAME>."""
    cols = set(schema(src)); men = sample.endswith("mr"); sel = []
    for c in WANT:
        cands = [c] if c in NOSUFFIX else ([c + "MN", c] if men else [c])
        have = next((x for x in cands if x in cols), None)
        sel.append(f"{have} AS {c}" if have else f"NULL::INTEGER AS {c}")
    duckdb.sql(f"COPY (SELECT {', '.join(sel)} FROM read_parquet('{src}')) TO '{IP/(sample + '.parquet')}' (FORMAT PARQUET)")

if __name__ == "__main__":
    for d in sorted(p for p in (IP/"_full").glob("*") if p.is_dir()):
        s = d.name; files = glob.glob(str(d/"*.parquet"))
        if not files or not re.match(r"^[a-z]{2}\d{4}(ir|mr)$", s): continue
        c = set(schema(files[0])); has_mh = any(x in c or x + "MN" in c for x in ("DEPRESSIONSCORE", "GADSCORE", "DEPRESSIONDIAG"))
        if has_mh: project(s, files[0]); print(f"projected {s} -> data/ipums/dhs/{s}.parquet")
    for f in sorted(IP.glob("*.parquet")):
        s = f.stem; con = duckdb.connect(); c = set(schema(f)); sex = "men" if s.endswith("mr") else "women"
        sel = [(x if x in c else f"NULL::INTEGER AS {x}") for x in DESIGN + MH + EXPO] + [f"'{sex}' AS SEX"]
        con.sql(f"COPY (SELECT {', '.join(sel)} FROM read_parquet('{f}')) TO '{OUT/(s + '_slim.parquet')}' (FORMAT PARQUET)")
        r = con.sql(f"""SELECT count(*) n, sum(CASE WHEN DEPRESSIONSCORE <= 27 THEN 1 ELSE 0 END) phq, sum(CASE WHEN GADSCORE <= 21 THEN 1 ELSE 0 END) gad,
                       sum(CASE WHEN DEPRESSIONDIAG IN (0,1) THEN 1 ELSE 0 END) diag, sum(CASE WHEN INTERNETMO BETWEEN 0 AND 3 THEN 1 ELSE 0 END) netmo,
                       sum(CASE WHEN CELLPHONESMART IN (0,1,9) THEN 1 ELSE 0 END) smart FROM read_parquet('{OUT/(s + '_slim.parquet')}')""").fetchone()
        print(f"{s}_slim.parquet ({sex}): n={r[0]:,} PHQ-9={r[1]:,} GAD-7={r[2]:,} diagnosis item={r[3]:,} INTERNETMO={r[4]:,} CELLPHONESMART={r[5]:,}")
