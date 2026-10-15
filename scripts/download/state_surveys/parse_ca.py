"""California Healthy Kids Survey county estimates via kidsdata.org CSV exports (WestEd CHKS, grades 7/9/11/NT).
Topics: 662 depressive feelings by grade; 387 by gender x grade; 1825 suicidal ideation by grade; 1826 by gender x grade.
Two-school-year windows (e.g. 2011_2013 = 2011-12 + 2012-13); year is coded as the window end year."""
import pandas as pd, glob
D = "data/external/state_surveys/ca"
SLUG = {662: "depressive-feelings-grade", 387: "depressive-feelings-gender", 1825: "suicidal-ideation-grade", 1826: "suicidal-ideation-gender"}
ITEM = {662: "sad_hopeless", 387: "sad_hopeless", 1825: "considered_suicide", 1826: "considered_suicide"}
WORD = {"sad_hopeless": "CHKS: during the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more that you stopped doing some usual activities? (% yes)",
        "considered_suicide": "CHKS: during the past 12 months, did you ever seriously consider attempting suicide? (% yes; grades 9/11/NT only)"}
out = []
for t, slug in SLUG.items():
    df = pd.read_csv(f"{D}/kidsdata_topic{t}_all.csv", dtype=str)
    df = df[df.LocationType.isin(["County", "State"])]
    df = df[df.DataFormat == "Percent"]
    if "StudentResponse" in df.columns:
        df = df[df.StudentResponse == "Yes"]
    df = df[pd.to_numeric(df.Data, errors="coerce").notna()]
    for _, r in df.iterrows():
        sex = "all"
        if "Gender" in df.columns:
            g = r["Gender"].strip().lower(); sex = {"female": "female", "male": "male"}.get(g, g)
        grade = r["GradeLevel"].replace("Grade ", "").strip()
        grade = {"Non-Traditional": "NT", "Nontraditional": "NT"}.get(grade, grade)
        y0, y1 = r["TimeFrame"].split("_")
        out.append(dict(state="CA", geography_type="county" if r.LocationType == "County" else "state",
                        geography_name=r.Location, geography_fips=r.FIPSCode.zfill(5) if r.LocationType == "County" else "06",
                        year=int(y1), grade_or_age=grade, sex=sex, item=ITEM[t], value_pct=float(r.Data), n=None,
                        source_url=f"https://www.kidsdata.org/topic/{t}/{slug}/table",
                        note=f"{WORD[ITEM[t]]}; pooled school years {y0}-{int(y0)+1} and {int(y1)-1}-{y1}; kidsdata topic {t}"))
df = pd.DataFrame(out).drop_duplicates(["geography_name", "year", "grade_or_age", "sex", "item"])
df.to_csv("data/compiled/state_surveys/ca_chks_county.csv", index=False)
print(df.groupby(["item", "sex", "year"]).size().unstack(fill_value=0))
print(df.geography_name.nunique(), "geographies;", df[df.geography_type=="county"].geography_name.nunique(), "counties")
print(sorted(df.grade_or_age.unique()))
