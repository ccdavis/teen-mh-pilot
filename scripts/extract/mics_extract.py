"""Extract MICS6/7 children 5-17 (fs), women (wm), men (mn), households (hh) for all samples with the Child Functioning Module."""
import pandas as pd, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from mics_reader import read, RAW
OUT = pathlib.Path(__file__).resolve().parents[2]/"data/extracts/mics"; OUT.mkdir(parents=True, exist_ok=True)
samples = sorted(p.name.replace("_fs.layout.txt","") for p in (RAW/"layouts").glob("*_fs.layout.txt") if "ANXIFREQ" in p.read_text())
print(len(samples), "samples")
FS = ["SAMPLE","COUNTRY_ISO3","YEAR","SERIAL","CLUSTER","PSU","HHNO","LINECH","LINEMC","WEIGHTFS","URBAN","REGIONW","AGEFS","SEXFS","WINDEX5","WSCORE","EDCURR_FS","EDGRADEATT_ORIG","RESULTFS",
      "ANXIFREQ","DEPRESSFREQ","DIFFSEE","DIFFHEAR","DIFFLEARN","DIFFREMEM","DIFFDISTRACT","DIFFROUTINE","DIFFBEHAV","DIFFFRIEND","DIFFCARE","DIFFCOMIN","DIFFCOMOUT","DIFFWALKFAR","INTERVIEWMO","INTERVIEWYR","PRHOMEWORK","CLWORKHOURS","CLCHOREHOURS"]
WM = ["SAMPLE","SERIAL","CLUSTER","HHNO","LINEWM","WEIGHTWM","AGEWM","URBAN","WINDEX5","RESULTWM","MOBILEWM","PHONEFREQ3MO","INTEVER","INTFREQ3MO","PCFREQ3MO","EDLEVELWM","TVFREQ","NEWSFREQ","RADIOFREQ"]
MN = ["SAMPLE","SERIAL","CLUSTER","HHNO","LINEMN","WEIGHTMN","AGEMN","URBAN","WINDEX5","RESULTMN","MOBILEMN","PHONEFREQ3MO","INTEVER","INTFREQ3MO","PCFREQ3MO"]
HH = ["SAMPLE","SERIAL","CLUSTER","HHNO","WEIGHTHH","URBAN","REGIONW","WINDEX5","WSCORE","MOBILE","COMPUTER","INTERNET","ELECTRICITY","INTERVIEWMO","INTERVIEWYR"]
fails = []
for rt, cols in [("fs",FS),("wm",WM),("mn",MN),("hh",HH)]:
    frames = []; t = time.time()
    for s in samples:
        if not (RAW/"data"/f"{s}_{rt}_mics.dat.gz").exists(): continue
        try: d = read(s, rt, cols); d["sample"] = s; frames.append(d)
        except Exception as e: fails.append((s, rt, str(e)[:100])); print("FAIL", s, rt, str(e)[:100])
    df = pd.concat(frames, ignore_index=True); df.to_parquet(OUT/f"mics_{rt}.parquet"); print(rt, df.shape, len(frames), "samples", round(time.time()-t), "s")
if fails: raise SystemExit(f"{len(fails)} sample files could not be read (the analysis would silently cover fewer surveys): {fails}")
