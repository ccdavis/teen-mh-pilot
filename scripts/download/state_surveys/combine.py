"""Stack the per-state extracts into data/compiled/state_surveys/state_survey_county_panel.csv and attach county FIPS."""
import pandas as pd, glob, re, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[3]; E = str(ROOT/"data/compiled/state_surveys")
COUNTY = ROOT/"data/external/state_surveys/national_county.txt"  # Census national county file (2010 vintage codes)
if not COUNTY.exists():
    COUNTY.parent.mkdir(parents=True, exist_ok=True); urllib.request.urlretrieve("https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt", COUNTY)
COLS = ["state", "geography_type", "geography_name", "geography_fips", "year", "grade_or_age", "sex", "item", "value_pct", "n", "source_url", "note"]
parts = []
for f in sorted(glob.glob(f"{E}/*_county.csv")):
    d = pd.read_csv(f, dtype={"geography_fips": str})
    for c in COLS:
        if c not in d.columns: d[c] = None
    parts.append(d[COLS])
df = pd.concat(parts, ignore_index=True)
fips = pd.read_csv(COUNTY, header=None, names=["st", "sf", "cf", "name", "cls"], dtype=str)
fips["fips"] = fips.sf + fips.cf
fips["key"] = fips.name.str.lower().str.replace(r"\s+county$", "", regex=True).str.replace(r"[^a-z]", "", regex=True)
lk = {(r.st, r.key): r.fips for r in fips.itertuples()}
def county_fips(row):
    if row.geography_type != "county" or (isinstance(row.geography_fips, str) and row.geography_fips.strip()):
        return row.geography_fips
    name = str(row.geography_name).lower()
    name = name.replace("charter schools only county", "").replace("non chicago", "").replace("saint clair", "st. clair").strip()
    k = re.sub(r"[^a-z]", "", re.sub(r"\s+county$", "", name))
    return lk.get((row.state, k))
df["geography_fips"] = df.apply(county_fips, axis=1)
df.loc[df.geography_name == "Cook Non Chicago", "note"] += " | Cook County excluding City of Chicago (IYS reports Chicago separately by community area)"
df.loc[df.geography_name == "Cook Non Chicago", "geography_name"] = "Cook County (non-Chicago)"
df.loc[df.geography_name.str.contains("Charter Schools Only", case=False), "note"] += " | Philadelphia charter-schools-only profile report (no district-school report)"
# PAYS 2025 names the same charter-schools-only series "Philadelphia County" (its 2021 and 2023 columns equal the 2023 edition's cell for cell), so one name is used
df.loc[(df.state == "PA") & df.geography_name.str.contains("Philadelphia", case=False), "geography_name"] = "Philadelphia County"
df.loc[(df.state == "PA") & (df.geography_name == "Philadelphia County"), "note"] = df.loc[(df.state == "PA") & (df.geography_name == "Philadelphia County"), "note"].str.replace(r" \| Philadelphia charter-schools-only.*$", "", regex=True) + " | Philadelphia: charter-schools-only PAYS series (no district-school report; 2025 edition drops the label)"
df = df.sort_values("note").drop_duplicates(["state", "geography_type", "geography_name", "year", "grade_or_age", "sex", "item"], keep="last")
df["year"] = df.year.astype(int)
df = df.sort_values(["state", "geography_type", "geography_name", "item", "year", "grade_or_age", "sex"]).reset_index(drop=True)
df.to_csv(f"{E}/state_survey_county_panel.csv", index=False)
miss = df[(df.geography_type == "county") & df.geography_fips.isna()].geography_name.unique()
print("rows", len(df), "| counties without FIPS:", list(miss)[:20])
cov = df[df.geography_type == "county"].groupby(["state", "item"]).agg(years=("year", lambda s: " ".join(map(str, sorted(s.unique())))), n_counties=("geography_name", "nunique"), rows=("year", "size"))
print(cov.to_string())
