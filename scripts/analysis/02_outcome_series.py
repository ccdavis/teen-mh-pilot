"""Step 2: ACS cognitive-difficulty outcome series with SDR replicate-weight SEs.
Outputs (results/tables/):
  acs_national_year_sex_age.csv   year x sex x agegrp, 2005-2024 (2005-07 flagged: pre-2008 wording)
  acs_state_year_sex_1217.csv     state x year x sex, ages 12-17
  acs_met_year_sex_1217.csv       met2013 x year x sex, ages 12-17 (plus state non-metro remainders)
  acs_state_year_sex_age.csv      state x year x sex x agegrp (for placebos at state level)
SE via ACS successive-difference replication: var = (4/80) * sum_r (theta_r - theta)^2.
PERWT has 2 implied decimals; REPWTP are integral, so PERWT/100 is on the same scale as REPWTP.
"""
import duckdb, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
con.sql(f"create view cells as select * from read_parquet('{ROOT}/data/extracts/acs/cells_*.parquet')")

rep_terms = " + ".join(f"power(sum(rem_r{i})/sum(n_r{i}) - sum(rem_w)/100.0/(sum(n_w)/100.0), 2)" for i in range(1, 81))
def agg(group_cols, where="1=1", name=""):
    g = ", ".join(group_cols)
    q = f"""
    select {g},
      sum(n_unwt) as n_unwt, sum(rem_unwt) as rem_unwt,
      sum(n_w)/100.0 as pop,
      sum(rem_w)/100.0 / (sum(n_w)/100.0) as rate,
      sqrt(4.0/80 * ({rep_terms})) as se,
      sum(sens_w)/sum(n_w) as rate_sens, sum(eye_w)/sum(n_w) as rate_eye, sum(hear_w)/sum(n_w) as rate_hear,
      sum(care_w)/sum(n_w) as rate_care, sum(phys_w)/sum(n_w) as rate_phys, sum(mob_w)/sum(n_w) as rate_mob
    from cells where {where} group by {g} order by {g}"""
    df = con.sql(q).df()
    df["pre2008_wording"] = df["year"] < 2008
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(name, df.shape)
    return df

# DIFFREM universe is age 5+; exclude 00-04
nat = agg(["year", "sex", "agegrp"], "agegrp <> '00-04'", "acs_national_year_sex_age")
agg(["year", "agegrp"], "agegrp <> '00-04'", "acs_national_year_age")
agg(["year", "sex"], "agegrp in ('12-14','15-17')", "acs_national_year_sex_1217")
agg(["statefip", "year", "sex"], "agegrp in ('12-14','15-17')", "acs_state_year_sex_1217")
agg(["statefip", "year"], "agegrp in ('12-14','15-17')", "acs_state_year_1217")
agg(["statefip", "year", "sex", "agegrp"], "agegrp <> '00-04'", "acs_state_year_sex_age")
# metro: met2013 code 0 = not in identifiable area -> keep as state remainder (key = statefip*100000)
con.sql("create view cells_m as select *, case when met2013>0 then met2013 else statefip*100000 end as market from cells")
q = f"""select market, year, sex, sum(n_unwt) n_unwt, sum(rem_unwt) rem_unwt, sum(n_w)/100.0 pop,
   sum(rem_w)/100.0/(sum(n_w)/100.0) rate, sqrt(4.0/80*({rep_terms})) se
   from cells_m where agegrp in ('12-14','15-17') group by 1,2,3 order by 1,2,3"""
m = con.sql(q).df(); m.to_csv(OUT / "acs_met_year_sex_1217.csv", index=False); print("met", m.shape, m.market.nunique(), "markets")
q = q.replace("market, year, sex,", "market, year,").replace("group by 1,2,3 order by 1,2,3", "group by 1,2 order by 1,2")
m = con.sql(q).df(); m.to_csv(OUT / "acs_met_year_1217.csv", index=False)

# quick printout: national 12-17 by sex, and 65+ placebo
import pandas as pd
pd.set_option("display.width", 200)
p = nat[nat.agegrp.isin(["12-14","15-17","65+"])].pivot_table(index="year", columns=["agegrp","sex"], values="rate")*100
print((p.round(2)).to_string())
