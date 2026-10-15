"""ACS adoption dose: share of 12-17-year-olds living in a household with a cellular data plan (2013+) / smartphone (2016+),
by year nationally, by state, and by market. CIDATAPLN/CISMRTPHN: 1=Yes 2=No 0=N/A(GQ), 8=suppressed."""
import duckdb, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = ROOT/"results/tables"
con = duckdb.connect()
con.sql(f"""create view p as select YEARP as yr, STATEFIP_H as statefip, MET2013_H as met2013,
  case when MET2013_H>0 then MET2013_H else STATEFIP_H*100000 end as market, AGE, SEX, PERWT/100.0 as w,
  CIDATAPLN_H as dp, CISMRTPHN_H as sp, CINETHH_H as net, CIHISPEED_H as hs, DIFFREM
  from read_parquet('{ROOT}/data/extracts/acs/person_us20[1-2]*.parquet') where YEARP>=2013 and AGE between 12 and 17""")
def q(g, name):
    df = con.sql(f"""select {g}, sum(w) pop, count(*) n,
      sum(case when dp=1 then w end)/sum(case when dp in (1,2) then w end) dataplan,
      sum(case when sp=1 then w end)/nullif(sum(case when sp in (1,2) then w end),0) smartphone,
      sum(case when net in (1,2) then w end)/sum(case when net in (1,2,3) then w end) anyinternet,
      sum(case when dp=1 and hs=20 then w end)/sum(case when dp in (1,2) then w end) dataplan_no_wired,
      sum(case when DIFFREM=2 and dp=1 then w end)/sum(case when dp=1 then w end) rem_if_dataplan,
      sum(case when DIFFREM=2 and dp=2 then w end)/sum(case when dp=2 then w end) rem_if_nodataplan
      from p group by {g} order by {g}""").df()
    df.to_csv(OUT/f"{name}.csv", index=False); return df
print(q("yr", "acs_dose_national_1217").round(3).to_string())
q("yr, sex", "acs_dose_national_sex_1217"); q("statefip, yr", "acs_dose_state_1217"); q("market, yr", "acs_dose_market_1217")
# label check
print(con.sql("select yr, net, count(*) from p group by 1,2 order by 1,2").df().pivot(index="yr", columns="net", values="count_star()").to_string())
