"""Generate duckdb SQL that turns IPUMS USA 1-year ACS extracts (2005-2024, one parquet per sample in data/ipums/usa/) into the
two slim files the analysis uses: person_<sample>.parquet (all ages, ~50 variables) and cells_<sample>.parquet (year x state x
MET2013 x sex x age-group cells with the 80 replicate-weight sums for cognitive difficulty). See scripts/extract/README.md for the
variable list and how to obtain the extract from usa.ipums.org. Writes build/sql/extract_<sample>.sql and build/sql/run_extract.sh."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "sql"; OUT.mkdir(parents=True, exist_ok=True)
PQ = "data/ipums/usa"
GP1_OUT = "data/extracts/acs"

PERSON_COLS = [
 "YEARP","SERIALP","PERNUM","PERWT","HHWT_H","AGE","SEX","RACE","HISPAN","BPL","CITIZEN","LANGUAGE",
 "SCHOOL","GRADEATT","SCHLTYPE","EDUC","MIGRATE1",
 "DIFFREM","DIFFCARE","DIFFSENS","DIFFEYE","DIFFHEAR","DIFFPHYS","DIFFMOB",
 "POVERTY","FTOTINC","HHINCOME_H","HCOVANY","RELATE","MOMLOC","POPLOC","NCHILD",
 "STATEFIP_H","COUNTYFIP_H","PUMA_H","CPUMA0010_H","CPUMA1020_H","MET2013_H","MET2013ERR_H","MET2023_H","METRO_H","DENSITY_H",
 "CINETHH_H","CIHISPEED_H","CIDATAPLN_H","CISMRTPHN_H","CIHAND_H","CILAPTOP_H","CIBRDBND_H","OWNERSHP_H","MULTGEN_H",
]
AGEGRP = """CASE WHEN AGE BETWEEN 5 AND 11 THEN '05-11' WHEN AGE BETWEEN 12 AND 14 THEN '12-14'
  WHEN AGE BETWEEN 15 AND 17 THEN '15-17' WHEN AGE BETWEEN 18 AND 24 THEN '18-24' WHEN AGE BETWEEN 25 AND 49 THEN '25-49'
  WHEN AGE BETWEEN 50 AND 64 THEN '50-64' WHEN AGE >= 65 THEN '65+' ELSE '00-04' END"""

runner = ["#!/bin/bash", "set -u", f"mkdir -p {GP1_OUT}"]
for y in range(2005, 2025):
    s = f"us{y}a"
    import duckdb
    src_file = ROOT / PQ / f"{s}.parquet"
    if not src_file.exists(): print("missing extract:", src_file); continue
    have = set(r[0] for r in duckdb.sql(f"describe select * from read_parquet('{src_file}')").fetchall())
    sel = ",\n  ".join(c if c in have else f"NULL::BIGINT AS {c}" for c in PERSON_COLS)
    src = f"read_parquet('{PQ}/{s}.parquet')"
    def col(c): return c if c in have else "NULL::BIGINT"
    rep_num = ",\n  ".join(f"SUM(CASE WHEN DIFFREM=2 THEN REPWTP{i} ELSE 0 END) AS rem_r{i}" for i in range(1, 81))
    rep_den = ",\n  ".join(f"SUM(REPWTP{i}) AS n_r{i}" for i in range(1, 81))
    sql = f"""PRAGMA threads=4;
COPY (SELECT
  {sel}
FROM {src}) TO '{GP1_OUT}/person_{s}.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
COPY (SELECT YEARP AS year, STATEFIP_H AS statefip, MET2013_H AS met2013, SEX AS sex,
  {AGEGRP} AS agegrp,
  COUNT(*) AS n_unwt,
  SUM(PERWT) AS n_w,
  SUM(CASE WHEN DIFFREM=2 THEN PERWT ELSE 0 END) AS rem_w,
  SUM(CASE WHEN DIFFREM=2 THEN 1 ELSE 0 END) AS rem_unwt,
  SUM(CASE WHEN {col('DIFFSENS')}=2 THEN PERWT ELSE 0 END) AS sens_w,
  SUM(CASE WHEN {col('DIFFEYE')}=2 THEN PERWT ELSE 0 END) AS eye_w,
  SUM(CASE WHEN {col('DIFFHEAR')}=2 THEN PERWT ELSE 0 END) AS hear_w,
  SUM(CASE WHEN {col('DIFFCARE')}=2 THEN PERWT ELSE 0 END) AS care_w,
  SUM(CASE WHEN {col('DIFFPHYS')}=2 THEN PERWT ELSE 0 END) AS phys_w,
  SUM(CASE WHEN {col('DIFFMOB')}=2 THEN PERWT ELSE 0 END) AS mob_w,
  {rep_den},
  {rep_num}
FROM {src}
GROUP BY ALL) TO '{GP1_OUT}/cells_{s}.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
"""
    (OUT / f"extract_{s}.sql").write_text(sql)
    runner.append(f"echo \"$(date) start {s}\"; duckdb < build/sql/extract_{s}.sql && echo \"$(date) done {s}\" || echo \"$(date) FAILED {s}\"")
runner.append("echo ALLDONE")
(OUT / "run_extract.sh").write_text("\n".join(runner) + "\n")
print("wrote", len(list(OUT.glob('extract_*.sql'))), "sql files")
