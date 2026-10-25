"""Generate duckdb SQL that turns IPUMS ATUS extracts into the slim activity files the analysis reads.

Input per sample (at2003 ... at2025): data/ipums/atus/<sample>_A.parquet (activity records) and <sample>_P.parquet (person
records). A hierarchical ATUS extract is split into these two files by RECTYPE before conversion. Output per sample:
data/extracts/atus/atus_<sample>.parquet, one row per activity of each diary respondent with the respondent's characteristics
attached. Writes build/sql/atus_<sample>.sql and build/sql/run_atus.sh (which creates the output directory).

Column resolution: the files used for the report carried internal names (CASEIDA/CASEIDP, PSERIALA/PSERIAL, RESP, household
variables with an _H suffix); a standard extract uses CASEID, LINENO and unsuffixed names. Each output column keeps the internal
name and is taken from the first candidate that exists in the file; required columns raise when none does, optional ones are
written as NULL. The respondent is selected by RESP = 1 where the file has RESP, else by WT06 > 0 (household members who did not
keep the diary have a zero weight). WT is WT06 as delivered (the internal copy is a string with six implied decimals, a standard
extract a decimal number; the analysis scripts use weight ratios only, so the scale does not matter) and WT20, the 2020 pandemic
weight, is written where the file carries it.

Usage: uv run python scripts/extract/atus_extract.py [ipums_dir]   (default data/ipums/atus)
"""
import sys, pathlib, duckdb
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT/"build/sql"; OUT.mkdir(parents=True, exist_ok=True)
PQ = sys.argv[1] if len(sys.argv) > 1 else "data/ipums/atus"; DEST = "data/extracts/atus"
# (output name, candidate input names, required)
ACT = [("ACTIVITY",["ACTIVITY"],True), ("DURATION",["DURATION"],True), ("WHERE",["WHERE"],False), ("START",["START"],False),
       ("ACTLINE",["ACTLINE"],False), ("CASEIDA",["CASEIDA","CASEID"],True), ("PSERIALA",["PSERIALA","PERNUM","LINENO"],False)]
PER = [("YEARP",["YEARP","YEAR"],True), ("CASEIDP",["CASEIDP","CASEID"],True), ("PSERIAL",["PSERIAL","PERNUM","LINENO"],False), ("RESP",["RESP"],False),
       ("AGE",["AGE"],True), ("SEX",["SEX"],True), ("RACE",["RACE"],False), ("HISPAN",["HISPAN"],False), ("EDUC",["EDUC"],False),
       ("SCHLCOLL",["SCHLCOLL"],True), ("FULLPART",["FULLPART"],False), ("EMPSTAT",["EMPSTAT"],False), ("DAY",["DAY"],True),
       ("HOLIDAY",["HOLIDAY"],True), ("MONTH",["MONTH"],False), ("DIFFREM",["DIFFREM"],False),
       ("STATEFIP_H",["STATEFIP_H","STATEFIP"],False), ("METRO_H",["METRO_H","METRO"],False), ("METFIPS_H",["METFIPS_H","METFIPS"],False),
       ("HH_CHILD_H",["HH_CHILD_H","HH_CHILD"],False), ("FAMINCOME_H",["FAMINCOME_H","FAMINCOME"],False), ("POVERTY185_H",["POVERTY185_H","POVERTY185"],False),
       ("KIDBEDTIME_H",["KIDBEDTIME_H","KIDBEDTIME"],False), ("GENHEALTH",["GENHEALTH"],False),
       ("WBWT",["WBWT"],False), ("WT",["WT06","WT"],True), ("WT20",["WT20"],False)]
def columns(have):
    return set(r[0] for r in duckdb.sql(f"describe select * from read_parquet('{have}')").fetchall())
RESERVED = {"WHERE"}  # SQL keywords used as IPUMS variable names must be quoted
def q(name): return f'"{name}"' if name in RESERVED else name
def resolve(spec, have, alias, sample):
    out = []
    for name, cands, required in spec:
        hit = next((c for c in cands if c in have), None)
        if hit: out.append(f"{alias}.{q(hit)} AS {q(name)}" if hit != name else f"{alias}.{q(name)}")
        elif required: raise SystemExit(f"{sample}: none of {cands} found for required column {name}")
        else: out.append(f"NULL::BIGINT AS {q(name)}")
    return out
runner = ["#!/bin/bash", "set -u", f"mkdir -p {DEST}"]
n = 0
for y in range(2003, 2026):
    s = f"at{y}"; fa, fp = ROOT/PQ/f"{s}_A.parquet", ROOT/PQ/f"{s}_P.parquet"
    if not (fa.exists() and fp.exists()): print("missing extract:", fa if not fa.exists() else fp); continue
    ha, hp = columns(fa), columns(fp)
    sel = ",\n  ".join(resolve(ACT, ha, "a", s) + resolve(PER, hp, "p", s))
    caseid_a = next(c for c in ["CASEIDA","CASEID"] if c in ha); caseid_p = next(c for c in ["CASEIDP","CASEID"] if c in hp)
    resp = "p.RESP = 1" if "RESP" in hp else ("p.WT06 > 0" if "WT06" in hp else "p.WT > 0")
    sql = f"""PRAGMA threads=4;
COPY (SELECT
  {sel}
FROM read_parquet('{PQ}/{s}_A.parquet') a
JOIN read_parquet('{PQ}/{s}_P.parquet') p ON p.{caseid_p} = a.{caseid_a} AND {resp}
) TO '{DEST}/atus_{s}.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
"""
    (OUT/f"atus_{s}.sql").write_text(sql); n += 1
    runner.append(f"echo \"$(date) start {s}\"; duckdb < build/sql/atus_{s}.sql && echo \"$(date) done {s}\" || echo \"$(date) FAILED {s}\"")
runner.append("echo ALLDONE")
(OUT/"run_atus.sh").write_text("\n".join(runner) + "\n")
print("wrote", n, "sql files and build/sql/run_atus.sh")
