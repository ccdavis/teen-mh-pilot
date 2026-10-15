"""OCR-based parse of 1993/94 report ('The health of youth') by-country figures.
The PDF's text layer is unusable (custom font encoding), so pages are rendered at 220 dpi and read with RapidOCR.
Figure layout: three age panels left-to-right (11, 13, 15); each row = country label, with the female value printed
above the male value at the right of the bars (legend: Female = dark, Male = light)."""
import re, pathlib, pymupdf, pandas as pd
from rapidocr_onnxruntime import RapidOCR
ROOT = pathlib.Path(__file__).resolve().parents[3]
EXT = str(ROOT/"data/external/hbsc")
DOC="hbsc_1993_94_health_of_youth.pdf"
S = str(ROOT/"data/external/hbsc/_render"); pathlib.Path(S).mkdir(parents=True, exist_ok=True)  # rendered page images (not committed)
PAGES={107:("feel_low_at_least_weekly","Fig. 6.10 (printed p.97)")}
CN={"Russia**":"Russian Federation","Germany**":"Germany","France**":"France","N. Ireland":"Northern Ireland",
    "Belgium Fl.":"Belgium (Flemish)","Belgium Fr.":"Belgium (French)","Czech Rep.":"Czechia"}

def parse_page(pn, item, fig):
    d=pymupdf.open(f"{EXT}/{DOC}"); img=f"{S}/r1994_p{pn}_hi.png"
    d[pn-1].get_pixmap(dpi=220).save(img)
    res,_=RapidOCR()(img)
    toks=[(b[0][0],b[0][1],t.strip(),c) for b,t,c in res]
    ages=sorted([(x,y,t) for x,y,t,c in toks if re.fullmatch(r"1[135] year olds",t)], key=lambda r:r[0])
    assert len(ages)==3, ages
    xs=[a[0] for a in ages]+[1e9]
    out=[]
    for i,(ax,ay,at) in enumerate(ages):
        age=int(at[:2])
        # panel tokens: x between this age label x-220 and next age label x-220
        lo,hi=ax-220, xs[i+1]-220
        pt=[t for t in toks if lo<=t[0]<hi and t[1]>ay+10]
        labels=[t for t in pt if not re.fullmatch(r"\d+",t[2]) and t[2][0].isalpha() and not t[2].startswith(("Female","Male","The","*","CHAPTER","Psychosocial"))
                and t[0] < ax + 500]
        nums=[t for t in pt if re.fullmatch(r"\d+",t[2])]
        for lx,ly,lt,lc in labels:
            # OCR box tops: the female value sits level with the country label, the male value ~28 px below
            up=[n for n in nums if n[0]>lx+300 and -18<=n[1]-ly<=12]
            lo_=[n for n in nums if n[0]>lx+300 and 14<=n[1]-ly<=44]
            cand=up+lo_
            if len(up)!=1 or len(lo_)!=1:
                print("WARN",pn,age,lt,[(round(n[1]-ly),n[2]) for n in cand]); continue
            c=CN.get(lt,lt)
            out.append(dict(country=c,wave="1993/94",year_end=1994,age=age,sex="girl",item=item,value_pct=float(cand[0][2]),source_page_or_table=f"PDF p.{pn} {fig}",ocr_conf=min(cand[0][3],cand[1][3],lc)))
            out.append(dict(country=c,wave="1993/94",year_end=1994,age=age,sex="boy",item=item,value_pct=float(cand[1][2]),source_page_or_table=f"PDF p.{pn} {fig}",ocr_conf=min(cand[0][3],cand[1][3],lc)))
    return out

def parse():
    out=[]
    for pn,(item,fig) in PAGES.items(): out+=parse_page(pn,item,fig)
    # OCR box for the first row of the 11-year-old panel is offset; values read visually from the rendered page
    have={(r["country"],r["age"]) for r in out}
    if ("Denmark",11) not in have:
        for sex,v in (("girl",44.0),("boy",32.0)):
            out.append(dict(country="Denmark",wave="1993/94",year_end=1994,age=11,sex=sex,item="feel_low_at_least_weekly",value_pct=v,
                            source_page_or_table="PDF p.107 Fig. 6.10 (printed p.97); value transcribed manually from rendered page",ocr_conf=1.0))
    df=pd.DataFrame(out); df["source_doc"]=DOC; return df

if __name__=="__main__":
    df=parse()
    print(df.groupby(["item","age","sex"]).size().unstack().to_string())
    print(df.pivot_table(index="country",columns=["age","sex"],values="value_pct").to_string())
    print("min ocr conf:", df.ocr_conf.min())
