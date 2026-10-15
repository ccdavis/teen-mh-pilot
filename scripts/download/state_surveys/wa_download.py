"""Download Washington Healthy Youth Survey county frequency reports from AskHYS.
2023/2025: Excel (one workbook per county, sheets by grade). 2014-2021: multi-grade PDF.
2010/2012: single-grade PDFs (8, 10, 12). Also ESD-level reports (same formats)."""
import re, os, sys, time, requests
OUT = "data/external/state_surveys/wa"
os.makedirs(OUT, exist_ok=True)
BASE = "https://www.askhys.net/SurveyResults"
YEARS = [2010, 2012, 2014, 2016, 2018, 2021, 2023, 2025]
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 research (teen-mh-pilot)"
index = []
for y in YEARS:
    for level in ["county-select", "esd-select"]:
        html = s.get(f"{BASE}/SelectionFrequencyReports", params={"year": y, "reportLevel": level}).text
        sel = re.search(rf'id="{level}".*?</select>', html, re.S).group(0)
        opts = re.findall(r'<option value="(\d+)">([^<]+)</option>', sel)
        for gid, name in opts:
            name = name.strip()
            if level == "county-select" and not name.endswith(" County"):
                continue  # skip combined-county groupings
            lst = s.get(f"{BASE}/GetReportList", params={"year": y, "reportLevel": gid}).text
            labels = [l for l in re.findall(r'reportLable=([^"]+)"', lst)]
            labels = [requests.utils.unquote(l.replace("&amp;", "&")) for l in labels]
            want = []
            if "Excel" in labels:
                want = [("Excel", "xlsx")]
            elif any(l.startswith("Multi-grade") for l in labels):
                want = [(next(l for l in labels if l.startswith("Multi-grade")), "pdf")]
            else:
                want = [(l, "pdf") for l in labels if l in ("Grade 8", "Grade 10", "Grade 12")]
            geo = "esd" if level == "esd-select" else "county"
            safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
            for lab, ext in want:
                tag = re.sub(r"[^A-Za-z0-9]+", "", lab)
                fn = f"{OUT}/hys_{y}_{geo}_{safe}_{tag}.{ext}"
                index.append((y, geo, name, gid, lab, fn))
                if os.path.exists(fn) and os.path.getsize(fn) > 1000:
                    continue
                for attempt in range(3):
                    try:
                        r = s.get(f"{BASE}/GetReport", params={"year": y, "reportLevel": gid, "reportLable": lab}, timeout=120)
                        if r.status_code == 200 and len(r.content) > 1000:
                            open(fn, "wb").write(r.content); break
                        print("bad", y, name, lab, r.status_code, len(r.content)); time.sleep(2)
                    except Exception as e:
                        print("err", y, name, lab, e); time.sleep(5)
                print(y, geo, name, lab, os.path.exists(fn) and os.path.getsize(fn))
                time.sleep(0.3)
import csv
with open(f"{OUT}/index.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "geo", "name", "askhys_id", "report", "file"]); w.writerows(index)
print("done", len(index))
