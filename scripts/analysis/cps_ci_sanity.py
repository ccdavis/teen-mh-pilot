"""Sanity checks for the CPS Computer & Internet Use supplement extract.

Reads data/extracts/cps/cps_ci_*.parquet (produced by scripts/extract/cps_internet_supplement.sql from an IPUMS CPS extract)
and prints markdown tables used in notes/cps_internet_supplement.md.
"""
import duckdb, pandas as pd, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLOB = str(ROOT / "data/extracts/cps/cps_ci_*.parquet")
con = duckdb.connect()
con.execute(f"CREATE VIEW p AS SELECT * FROM read_parquet('{GLOB}')")

def md(df, floatfmt=".3f"):
    return df.to_markdown(index=False, floatfmt=floatfmt)

# 1. rows, households, weighted population
q1 = """
SELECT SAMPLE, YEAR, MONTH, count(*) AS n_persons, count(DISTINCT SERIAL) AS n_hh,
       round(sum(WTFINL)/1e6,2) AS pop_wtfinl_m, round(sum(CISUPPWT)/1e6,2) AS pop_cisuppwt_m,
       round(sum(CIPWT)/1e6,2) AS pop_cipwt_m,
       count(*) FILTER (WHERE CIPWT>0) AS n_cipwt_pos,
       round(sum(HWTFINL) FILTER (WHERE PERNUM=1)/1e6,2) AS hh_hwtfinl_m
FROM p GROUP BY 1,2,3 ORDER BY 1"""
print("## Rows and weighted totals\n"); print(md(con.execute(q1).df(), ".2f")); print()

# 2. household internet at home. 2009-2010: CINETHH; 2011+: CINETHP (household-level item in 2015+).
#    HH-level = any person in HH coded Yes(2). NIU/no-response treated as No.
q2 = """
WITH hh AS (
  SELECT SAMPLE, YEAR, SERIAL,
         max(CASE WHEN coalesce(CINETHH,0)=2 OR coalesce(CINETHP,0)=2 THEN 1 ELSE 0 END) AS hh_net,
         max(CASE WHEN coalesce(CINETHH,0)=2 OR coalesce(CINETHP,0)=2 THEN 1
                  WHEN coalesce(CINETHH,0)=1 OR coalesce(CINETHP,0)=1 THEN 0 END) AS hh_net_answered,
         max(HWTFINL) AS HWTFINL, sum(CISUPPWT) AS hh_cisuppwt
  FROM p GROUP BY 1,2,3)
SELECT SAMPLE, YEAR,
  round(sum(hh_net*HWTFINL)/sum(HWTFINL),3) AS hh_any_home_internet_hwt,
  round(sum(hh_net*hh_cisuppwt)/sum(hh_cisuppwt),3) AS hh_any_home_internet_personwt,
  round(sum(hh_net_answered*HWTFINL) FILTER (WHERE hh_net_answered IS NOT NULL)
        / sum(HWTFINL) FILTER (WHERE hh_net_answered IS NOT NULL),3) AS hh_any_home_internet_among_answered,
  round(sum(HWTFINL) FILTER (WHERE hh_net_answered IS NOT NULL)/sum(HWTFINL),3) AS share_hh_with_answer
FROM hh GROUP BY 1,2 ORDER BY 1"""
print("## Household any home internet (all NIU treated as No; NOTE: mobile data-plan item is NOT in IPUMS)\n")
print(md(con.execute(q2).df())); print()

# 3. Persons 15-24: internet use items (no mobile-device item is available in IPUMS harmonized data)
q3 = """
SELECT SAMPLE, YEAR,
  count(*) FILTER (WHERE AGE BETWEEN 15 AND 24) AS n_15_24,
  round(sum(CISUPPWT*(CINTUSE=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24)/sum(CISUPPWT) FILTER (WHERE AGE BETWEEN 15 AND 24),3) AS uses_internet_anywhere_CINTUSE,
  round(sum(CISUPPWT*(CINETHP=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24)/sum(CISUPPWT) FILTER (WHERE AGE BETWEEN 15 AND 24),3) AS internet_at_home_CINETHP,
  round(sum(CISUPPWT*(CINTOUT=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24)/sum(CISUPPWT) FILTER (WHERE AGE BETWEEN 15 AND 24),3) AS internet_outside_home_CINTOUT,
  round(sum(CISUPPWT*(coalesce(CINETHP,0)=2 OR coalesce(CINTOUT,0)=2 OR coalesce(CINTLIB,0)=2 OR coalesce(CINTSCH,0)=2 OR coalesce(CINTOTHH,0)=2 OR coalesce(CINTUSE,0)=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24)/sum(CISUPPWT) FILTER (WHERE AGE BETWEEN 15 AND 24),3) AS any_use_proxy,
  round(sum(CIPWT*(CIEMAIL=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24 AND CIPWT>0)/sum(CIPWT) FILTER (WHERE AGE BETWEEN 15 AND 24 AND CIPWT>0),3) AS email_CIEMAIL_cipwt,
  round(sum(CIPWT*(CINTPHON=2)::INT) FILTER (WHERE AGE BETWEEN 15 AND 24 AND CIPWT>0)/sum(CIPWT) FILTER (WHERE AGE BETWEEN 15 AND 24 AND CIPWT>0),3) AS internet_phone_calls_CINTPHON_cipwt
FROM p GROUP BY 1,2 ORDER BY 1"""
print("## Persons 15-24 (CISUPPWT; CIPWT for random-respondent items). NIU treated as No.\n")
print(md(con.execute(q3).df())); print()

# 4. geography coding check
q4 = """
SELECT SAMPLE,
  count(*) FILTER (WHERE METFIPS NOT IN (99998,99999)) AS n_metfips_ident,
  count(DISTINCT METFIPS) FILTER (WHERE METFIPS NOT IN (99998,99999)) AS n_metfips_codes,
  count(*) FILTER (WHERE METAREA IS NOT NULL AND METAREA NOT IN (9997,9998,9999)) AS n_metarea_ident,
  count(*) FILTER (WHERE COUNTY<>0) AS n_county_ident,
  count(DISTINCT STATEFIP) AS n_states,
  round(sum(WTFINL) FILTER (WHERE METFIPS NOT IN (99998,99999))/sum(WTFINL),3) AS share_pop_metfips_ident
FROM p GROUP BY 1 ORDER BY 1"""
print("## Geography coding\n"); print(md(con.execute(q4).df())); print()

# 5. code frequencies for every CI item (unweighted) -> csv
ci = [c for c in con.execute("SELECT * FROM p LIMIT 0").df().columns if c.startswith("CI") and c not in ("CISUPPWT","CIPWT")]
frames = []
for c in ci:
    frames.append(con.execute(f"SELECT SAMPLE, '{c}' AS var, {c} AS code, count(*) AS n FROM p WHERE {c} IS NOT NULL GROUP BY 1,2,3 ORDER BY 1,3").df())
codes = pd.concat(frames)
out = ROOT / "notes/cps_ci_code_freqs.csv"
codes.to_csv(out, index=False)
print(f"wrote {out}")
print("\n## Availability matrix (non-null in sample)\n")
avail = codes.pivot_table(index="var", columns="SAMPLE", values="n", aggfunc="sum").notna().replace({True:"x", False:""})
print(avail.to_markdown())
