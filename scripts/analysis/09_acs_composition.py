"""Who drives the 12-17 rise in ACS cognitive difficulty? Rates by period x subgroup (poverty, race/ethnicity, school type, metro status, nativity)."""
import duckdb, pandas as pd, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
T = ROOT/"results/tables"; pd.set_option("display.width", 200)
con = duckdb.connect()
con.sql(f"""create view p as select YEARP as yr, PERWT/100.0 as w, SEX as sex, DIFFREM as rem,
  case when YEARP between 2008 and 2010 then '2008-10' when YEARP between 2017 and 2019 then '2017-19' when YEARP between 2022 and 2024 then '2022-24' end as period,
  case when POVERTY between 1 and 99 then 'poor <100%' when POVERTY between 100 and 199 then '100-199%' when POVERTY between 200 and 399 then '200-399%' when POVERTY>=400 then '400%+' else 'n/a' end as povgrp,
  case when HISPAN>0 then 'Hispanic' when RACE=100 then 'White NH' when RACE=200 then 'Black NH' when RACE between 400 and 699 then 'Asian-PI NH' else 'Other-multi NH' end as raceeth,
  case when SCHLTYPE=2 then 'public' when SCHLTYPE=3 then 'private' when SCHLTYPE=1 then 'not in school' else 'other' end as schltype,
  case when METRO_H in (3,4,5) then 'metro' when METRO_H=1 then 'nonmetro' when METRO_H=2 then 'mixed' else 'unknown' end as metro,  -- METRO: 1 nonmetro, 2 metro status indeterminable (mixed), 3-5 in metro area
  case when BPL<=12000 then 'US-born' else 'foreign-born' end as nativity,
  case when SCHOOL=2 then 'in school' else 'not' end as inschool
  from read_parquet('{ROOT.as_posix()}/data/extracts/acs/person_*.parquet') where AGE between 12 and 17 and YEARP>=2008""")
for g in ["povgrp","raceeth","schltype","metro","nativity"]:
    df = con.sql(f"""select {g}, sex, period, 100*sum(case when rem=2 then w end)/sum(w) rate, sum(w)/1e6 pop_m
        from p where period is not null group by 1,2,3 order by 1,2,3""").df()
    t = df.pivot_table(index=[g,"sex"], columns="period", values="rate")
    t["rel_chg_1719"] = 100*(t["2017-19"]/t["2008-10"]-1); t["abs_pp_1719"] = t["2017-19"]-t["2008-10"]; t["rel_chg_2224"] = 100*(t["2022-24"]/t["2008-10"]-1)
    t["share_pop_0810"] = df[df.period=="2008-10"].groupby([g,"sex"]).pop_m.sum()/df[df.period=="2008-10"].pop_m.sum()*100
    print(f"\n=== {g}"); print(t.round(2).to_string()); t.to_csv(T/f"acs_composition_{g}.csv")
