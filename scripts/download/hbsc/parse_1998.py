"""Parse 1997/98 report figures (Figs 3.1, 5.1, 5.8) from the PDF text flow.
Each figure page has three age panels; each panel is emitted as: n male values, n female values, n country names.
The order of the '<age>-year-olds' labels in the flow gives the panel order (verified against coordinates on p.27:
the panel whose bar-end labels sit just above the '15-year-olds' axis label is the first panel in the flow)."""
import re, pymupdf, pandas as pd
EXT="data/external/hbsc"
DOC="hbsc_1997_98_health_and_health_behaviour.pdf"
PAGES={27:("feel_low_at_least_weekly","Fig. 3.1"),51:("like_school","Fig. 5.1"),64:("schoolwork_pressure_a_lot","Fig. 5.8")}
CN={"Czech Republic":"Czechia","USA":"United States","Germany*":"Germany","France*":"France","Russian Federation*":"Russian Federation"}

def parse_page(page, item, fig, pn):
    lines=[l.strip() for l in page.get_text().split("\n") if l.strip()]
    ages=[int(l[:2]) for l in lines if re.fullmatch(r"1[135]-year-olds",l)]
    assert len(ages)==3, ages
    runs=[]
    for l in lines:
        k="N" if re.fullmatch(r"\d+",l) else "T"
        if runs and runs[-1][0]==k: runs[-1][1].append(l)
        else: runs.append([k,[l]])
    panels=[]
    for i in range(len(runs)-1):
        if runs[i][0]=="N" and len(runs[i][1])>=40 and runs[i+1][0]=="T":
            nums=runs[i][1]
            if len(nums)%2==1: nums=nums[1:]   # leading page number glued to the first run
            names=[t for t in runs[i+1][1] if not t.startswith("*") and t not in ("male","female") and "year-olds" not in t and not t.startswith("Fig")]
            n=len(nums)//2
            assert len(nums)==2*n and len(names)>=n, (pn,len(nums),len(names))
            panels.append((nums[:n],nums[n:],names[:n]))
    assert len(panels)==3,(pn,len(panels))
    out=[]
    for age,(male,female,names) in zip(ages,panels):
        for name,mv,fv in zip(names,male,female):
            c=CN.get(name,name)
            out.append(dict(country=c,wave="1997/98",year_end=1998,age=age,sex="boy",item=item,value_pct=float(mv),source_page_or_table=f"p.{pn} {fig}"))
            out.append(dict(country=c,wave="1997/98",year_end=1998,age=age,sex="girl",item=item,value_pct=float(fv),source_page_or_table=f"p.{pn} {fig}"))
    return out

def parse():
    d=pymupdf.open(f"{EXT}/{DOC}"); out=[]
    for pn,(item,fig) in PAGES.items(): out+=parse_page(d[pn-1],item,fig,pn)
    df=pd.DataFrame(out); df["source_doc"]=DOC; return df

if __name__=="__main__":
    df=parse()
    print(df.groupby(["item","age","sex"]).size().unstack().to_string())
    print(df[df.country.isin(["Greece","United States","Wales","Russian Federation","Austria"])].pivot_table(index=["item","country"],columns=["age","sex"],values="value_pct").to_string())
    print(df.groupby(["item","age","sex"]).value_pct.mean().unstack().round(1).to_string())
    print(sorted(df.country.unique()))
