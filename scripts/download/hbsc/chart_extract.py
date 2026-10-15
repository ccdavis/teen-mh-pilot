"""Coordinate-based extraction of HBSC international-report bar charts.

Each chart lists country names in a right-aligned label column with the bar-end
value labels (one per sex) to the right, vertically adjacent to the country name.
We recover (country, upper value, lower value) per chart and let the caller map
upper/lower to girl/boy after validation.
"""
import re
import pymupdf

COUNTRY_RX = re.compile(r"^\*?\s*(?P<name>[A-Z][A-Za-z .()'’/-]+?)\s*[a-z]?\*?$")
KNOWN = {
 "Albania","Armenia","Austria","Azerbaijan","Belgium (Flemish)","Belgium (French)","Bulgaria","Canada","Croatia",
 "Cyprus","Czech Republic","Czechia","Denmark","England","Estonia","Finland","France","Georgia","Germany","Greece",
 "Greenland","Hungary","Iceland","Ireland","Israel","Italy","Kazakhstan","Kyrgyzstan","Latvia","Lithuania","Luxembourg",
 "Malta","MKD","North Macedonia","TFYR Macedonia","Netherlands","Norway","Poland","Portugal","Republic of Moldova",
 "Romania","Russian Federation","Scotland","Serbia","Slovakia","Slovenia","Spain","Sweden","Switzerland","Tajikistan",
 "Turkey","Ukraine","United States","USA","Wales","Northern Ireland","Republic of Ireland","Moldova","Macedonia",
 "HBSC average (gender)","HBSC average (total)","HBSC AVERAGE (GENDER)","HBSC AVERAGE (TOTAL)","HBSC average",
 "HBSC AVERAGE PREVALENCE","Belgium (Fl.)","Belgium (Fr.)","Denmark (Greenland)","Germany*","France*","Russian Federation*",
}
NUM_RX = re.compile(r"^[–\-]?\s*\d+(\.\d+)?$|^–$")

def norm_country(t):
    t = t.strip().replace("’", "'")
    t = re.sub(r"\s+", " ", t)
    t = t.lstrip("*").rstrip("*").strip()
    # strip superscript footnote letters glued to name e.g. "MKDa"
    if t.endswith("a") and t[:-1] in KNOWN:
        t = t[:-1]
    return t

def page_lines(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt:
                continue
            x0, y0, x1, y1 = l["bbox"]
            out.append(dict(text=txt, x0=x0, y0=y0, x1=x1, y1=y1, yc=(y0+y1)/2, xc=(x0+x1)/2))
    return out

def find_charts(page, ytol=7.0, label_x_tol=14.0, min_countries=8):
    """Return list of charts: each dict(title, age, countries=[(name, yc, [(x0,val),...])])."""
    lines = page_lines(page)
    labels = [l for l in lines if norm_country(l["text"]) in KNOWN]
    nums = [l for l in lines if NUM_RX.match(l["text"].replace("–", "–"))]
    titles = [l for l in lines if re.search(r"\b1[135]-year-olds?\b.*\bwho\b", l["text"])]
    # cluster labels by right edge x1
    labels.sort(key=lambda l: l["x1"])
    clusters = []
    for l in labels:
        if clusters and abs(l["x1"] - clusters[-1][-1]["x1"]) < label_x_tol:
            clusters[-1].append(l)
        else:
            clusters.append([l])
    clusters = [c for c in clusters if len(c) >= min_countries]
    # sort clusters left-to-right
    clusters.sort(key=lambda c: c[0]["x1"])
    charts = []
    for i, c in enumerate(clusters):
        xr = c[0]["x1"]
        xnext = clusters[i+1][0]["x0"] if i+1 < len(clusters) else page.rect.width
        xnext_min = min(l["x0"] for l in clusters[i+1]) if i+1 < len(clusters) else page.rect.width
        rows = []
        ys = sorted(l["yc"] for l in c)
        for l in c:
            vals = [(n["x0"], n["text"].replace("–", "–")) for n in nums
                    if n["x0"] > xr and n["x0"] < xnext_min and abs(n["yc"] - l["yc"]) <= ytol]
            rows.append((norm_country(l["text"]), l["yc"], sorted(vals, key=lambda v: (v[0],))))
        rows.sort(key=lambda r: r[1])
        ymin = min(r[1] for r in rows)
        # title: nearest title line above the chart whose x overlaps [xr-150, xnext_min]
        # chart x-range: from leftmost label to the next chart's labels (or page edge)
        cx0 = min(l["x0"] for l in c) - 20
        cx1 = xnext_min
        def overlap(t):
            return max(0.0, min(t["x1"], cx1) - max(t["x0"], cx0))
        cand = [t for t in titles if overlap(t) > 0.5 * (t["x1"] - t["x0"])]
        title = None
        if cand:
            title = min(cand, key=lambda t: abs(t["yc"] - ymin))
        # also gather nums rows for value positions per row: attach y of each value to distinguish upper/lower
        rows2 = []
        for l in c:
            vals = [(n["x0"], n["yc"], n["text"].replace("–", "–")) for n in nums
                    if n["x0"] > xr and n["x0"] < xnext_min and abs(n["yc"] - l["yc"]) <= ytol]
            rows2.append((norm_country(l["text"]), l["yc"], vals))
        rows2.sort(key=lambda r: r[1])
        charts.append(dict(title=title["text"] if title else None, title_y=title["yc"] if title else None,
                           x_label=xr, x_next=xnext_min, rows=rows2))
    return charts

if __name__ == "__main__":
    import sys
    doc = pymupdf.open(sys.argv[1])
    for pn in map(int, sys.argv[2:]):
        for ch in find_charts(doc[pn-1]):
            print(f"== p{pn} title={ch['title']!r} x_label={ch['x_label']:.0f} rows={len(ch['rows'])}")
            for name, yc, vals in ch["rows"][:6]:
                print(f"   {name:28s} y={yc:6.1f} vals={[(round(x),round(y,1),v) for x,y,v in vals]}")
