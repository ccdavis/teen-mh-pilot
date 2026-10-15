"""ATUS time-use mediators for ages 15-17 (and 18-24, 35-54 comparison), 2003-2024.
Minutes per day in: sleep, homework, class, in-person socializing, computer leisure, games, TV, sports, phone/texting-ish.
Weights: WT06 (string double) except 2020 -> WT20/1e6. Weighted mean of daily minutes = sum(w*min)/sum(w) over respondents.
"""
import duckdb, pandas as pd, pathlib
OUT = pathlib.Path("results/tables")
con = duckdb.connect()
con.sql("""create view a as select *, case when YEARP=2020 then WT20/1e6 else try_cast(WT as double) end as w,
  case when MONTH in (6,7,8) then 'summer' else 'school' end as season,
  case when DAY in (1,7) or HOLIDAY=1 then 'weekend' else 'weekday' end as daytype,
  case when AGE between 15 and 17 then '15-17' when AGE between 18 and 24 then '18-24' when AGE between 35 and 54 then '35-54' end as agegrp
  from read_parquet('data/extracts/atus/atus_*.parquet', union_by_name=true)""")
cats = {"sleep":"ACTIVITY between 10100 and 10199", "homework":"ACTIVITY between 60300 and 60399", "class":"ACTIVITY between 60100 and 60199",
        "educ_all":"ACTIVITY between 60000 and 69999", "social_inperson":"ACTIVITY between 120100 and 120299", "computer_leisure":"ACTIVITY=120308",
        "games":"ACTIVITY=120307", "tv":"ACTIVITY in (120303,120304)", "sports":"ACTIVITY between 130100 and 130199", "phone":"ACTIVITY between 160100 and 160199",
        "work":"ACTIVITY between 50100 and 50199", "relax_think":"ACTIVITY=120301", "reading":"ACTIVITY=120312", "alone_leisure_screen":"ACTIVITY in (120303,120307,120308)"}
sel = ",\n ".join(f"sum(case when {c} then DURATION else 0 end) as {k}" for k,c in cats.items())
con.sql(f"""create table resp as select YEARP as year, CASEIDA, any_value(w) w, any_value(AGE) age, any_value(SEX) sex, any_value(agegrp) agegrp,
   any_value(season) season, any_value(daytype) daytype, any_value(SCHLCOLL) schlcoll, any_value(STATEFIP_H) statefip, {sel}
   from a where agegrp is not null group by 1,2""")
def wmean(g, name):
    cols = ", ".join(f"sum(w*{k})/sum(w) as {k}" for k in cats)
    df = con.sql(f"select {g}, count(*) n, {cols} from resp group by {g} order by {g}").df(); df.to_csv(OUT/f"{name}.csv", index=False); return df
d = wmean("year, agegrp", "atus_year_age")
wmean("year, agegrp, sex", "atus_year_age_sex"); wmean("year, agegrp, season, daytype", "atus_year_age_season_daytype")
# 3-year pooled, 15-17 school-year weekdays (the Gray test): homework, sleep, socializing
con.sql("create table r2 as select *, case when year<=2005 then '2003-05' when year<=2008 then '2006-08' when year<=2011 then '2009-11' when year<=2014 then '2012-14' when year<=2017 then '2015-17' when year<=2019 then '2018-19' when year<=2022 then '2020-22' else '2023-24' end period from resp")
cols = ", ".join(f"round(sum(w*{k})/sum(w),1) as {k}" for k in ["sleep","homework","class","educ_all","social_inperson","computer_leisure","games","tv","sports","phone"])
p = con.sql(f"select period, agegrp, season, daytype, count(*) n, {cols} from r2 where agegrp='15-17' group by 1,2,3,4 order by 2,3,4,1").df()
p.to_csv(OUT/"atus_1517_period_season_daytype.csv", index=False)
pd.set_option("display.width",220); print(p[p.daytype=="weekday"].to_string())
print(con.sql(f"select period, sex, count(*) n, {cols} from r2 where agegrp='15-17' and season='school' and daytype='weekday' group by 1,2 order by 2,1").df().to_string())
