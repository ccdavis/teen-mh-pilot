"""Build pisa2022_items.csv (variable, label, value labels) and per-country coverage tables.
Run after extract_student.py: uv run python scripts/pisa2022/build_items_and_coverage.py
"""
import json, pandas as pd, numpy as np
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2]); EX = f"{ROOT}/data/extracts/pisa2022"
SP = "/tmp/claude-1000/-home-ccd/39cfc7c3-ebec-4031-88de-95020340706c/scratchpad"
stu_meta = pd.read_pickle(f"{EX}/_stu_meta.pkl"); sch_meta = pd.read_pickle(f"{SP}/sch_meta.pkl")
# codebook varnum for cross-reference
cb = pd.concat([pd.read_csv(f"{SP}/CY08MSP_STU_QQQ_vars.csv").assign(file="STU_QQQ"),
                pd.read_csv(f"{SP}/CY08MSP_SCH_QQQ_vars.csv").assign(file="SCH_QQQ")])
items = pd.concat([stu_meta, sch_meta]).merge(cb[["file","NAME","VARNUM","VARLABEL"]], left_on=["file","variable"], right_on=["file","NAME"], how="left")
def fmt(d):
    if not d: return ""
    return "; ".join(f"{int(k) if isinstance(k,float) and k==int(k) else k}={v}" for k, v in d.items())
items["value_labels"] = items["value_labels"].apply(fmt)
items["codebook_label"] = items["VARLABEL"]
items = items[["file","variable","label","value_labels","VARNUM","codebook_label"]].rename(columns={"VARNUM":"codebook_varnum"})
items.to_csv(f"{EX}/pisa2022_items.csv", index=False)
print("items.csv rows:", len(items), "label mismatches vs codebook:", (items.label.fillna('') != items.codebook_label.fillna('')).sum())

stu = pd.read_parquet(f"{EX}/pisa2022_student.parquet"); sch = pd.read_parquet(f"{EX}/pisa2022_school.parquet")
print("student", stu.shape, "school", sch.shape)
cnames = dict(zip(sch.CNT.astype(str), sch.CNT.astype(str)))
key = {"ST016Q01NA":"lifesat","ST034Q06TA":"lonely","ST322Q07JA":"nervous_nodevice","ST322Q01JA":"turnoff_notif_class","ST273Q06JA":"distracted_self","ST273Q07JA":"distracted_others","ST326Q04JA":"hrs_leisure_school","IC170Q02JA":"smartphone_at_school","IC177Q02JA":"time_socnet","IC179Q01JA":"opinion_ban_phones","WB154Q04HA":"wb_depressed"}
g = stu.groupby("CNT", observed=True)
cov = pd.DataFrame({"n_students": g.size(), "ictq_share": g["Option_ICTQ"].mean().round(2), "wbq_share": g["Option_WBQ"].mean().round(2), "paper_share": (g["ADMINMODE"].apply(lambda s: (s==1).mean())).round(2)})
for v, nm in key.items():
    cov[nm] = g[v].apply(lambda s: s.notna().mean()).round(2)
gs = sch.groupby("CNT")
cov["n_schools"] = gs.size()
cov["sch_phone_ban_answered"] = gs["SC190Q02JA"].apply(lambda s: s.isin([1,2]).mean()).round(2)
cov["sch_phone_ban_yes"] = gs["SC190Q02JA"].apply(lambda s: (s==1).sum()/max(s.isin([1,2]).sum(),1)).round(2)
cov.index.name = "CNT"
cov.to_csv(f"{EX}/pisa2022_country_coverage.csv")
with pd.option_context("display.max_rows", 200, "display.width", 250):
    print(cov.to_string())
