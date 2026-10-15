"""County-level social-media / screen-time items vs sadness in WA (2023, 2025) and ME (2017-2021), on the county x grade cells of
state_survey_county_grade_series.csv (written by 23_state_surveys.py), so the exposure item and the outcome always cover the same
grades. Across: year fixed effects; within: county x grade and year fixed effects. SE clustered by county."""
import pandas as pd, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"
G = pd.read_csv(T/"state_survey_county_grade_series.csv", dtype={"grade": str}); G = G[G.sex=="all"]
W = G.pivot_table(index=["state","fips","grade","year"], columns="item", values="value").reset_index(); W["unit"] = W.fips.astype(str)+"_"+W.grade; rows = []
for st, x in [("WA","social_media_daily"),("WA","screen_time_3plus"),("ME","screen_time_3plus")]:
    for y in ["sad_hopeless","considered_suicide"]:
        d = W[(W.state==st)&W[x].notna()&W[y].notna()]
        m = pf.feols(f"{y} ~ {x} | year", data=d, vcov={"CRV1":"fips"}); m2 = pf.feols(f"{y} ~ {x} | unit + year", data=d, vcov={"CRV1":"fips"})
        rows.append(dict(state=st, dose=x, outcome=y, n=len(d), counties=d.fips.nunique(), grades=" ".join(sorted(d.grade.unique())), years=" ".join(str(v) for v in sorted(d.year.unique())),
                         cross_coef=m.coef().iloc[0], cross_se=m.se().iloc[0], within_coef=m2.coef().iloc[0], within_se=m2.se().iloc[0],
                         **{f"dose_mean_{int(yr)}": d[d.year==yr][x].mean() for yr in sorted(d.year.unique())}, **{f"outcome_mean_{int(yr)}": d[d.year==yr][y].mean() for yr in sorted(d.year.unique())}))
R = pd.DataFrame(rows); R.to_csv(T/"county_screen_dose.csv", index=False); pd.set_option("display.width", 250); print(R.round(2).to_string())
