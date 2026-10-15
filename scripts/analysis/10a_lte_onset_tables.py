"""Onset tables for the ACS market event study (scripts/analysis/10_event_study.py).
Reads data/compiled/lte/lte_onset_by_cbsa.csv, keeps the CBSAs that IPUMS USA identifies (MET2013 codes listed in
notes/acs_value_labels.csv), and writes one CSV per onset definition with columns market (MET2013 code) and onset_date:
  results/tables/lte_onset_first_launch_date.csv    first LTE launch by any of the four national carriers
  results/tables/lte_onset_verizon_date.csv         Verizon's launch
  results/tables/lte_onset_second_carrier_date.csv  the second carrier's launch
Run from the repository root: uv run python scripts/analysis/10a_lte_onset_tables.py
"""
import pandas as pd, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"
lab = pd.read_csv(ROOT/"notes/acs_value_labels.csv"); met = set(lab[lab.variable=="MET2013"].outputcode.astype(int)) - {0}
on = pd.read_csv(ROOT/"data/compiled/lte/lte_onset_by_cbsa.csv", dtype={"cbsa_code": str})
on["market"] = on.cbsa_code.astype(int); on = on[on.market.isin(met)]
print("CBSAs with a launch date:", len(on), "of", len(met), "IPUMS-identifiable metros")
for col in ["first_launch_date", "verizon_date", "second_carrier_date"]:
    d = on[on[col].notna() & (on[col].astype(str).str.len() >= 7)][["market", col]].rename(columns={col: "onset_date"})
    d.to_csv(T/f"lte_onset_{col}.csv", index=False); print(f"  {col}: {len(d)} markets")
