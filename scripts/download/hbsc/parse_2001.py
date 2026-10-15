"""Parse 2001/02 report figures (text flow: per age panel, girls values, boys values, country names)."""
import re, pymupdf, pandas as pd
EXT = str(__import__("pathlib").Path(__file__).resolve().parents[3]/"data/external/hbsc")
DOC="hbsc_2001_02_young_peoples_health_in_context_1_9789289013727-eng.pdf"
PAGES={57:"like_school",61:"schoolwork_pressure",72:"multiple_complaints",73:"high_life_satisfaction"}
CN={"TFYR Macedonia":"North Macedonia","Czech Republic":"Czechia","USA":"United States"}
def parse():
    d=pymupdf.open(f"{EXT}/{DOC}"); out=[]
    for pn,item in PAGES.items():
        lines=[l.strip() for l in d[pn-1].get_text().split("\n") if l.strip()]
        fig=[l for l in lines if l.startswith("Fig.")][0]
        runs=[]
        for l in lines:
            k="N" if re.fullmatch(r"\d+(\.\d+)?",l) else "T"
            if runs and runs[-1][0]==k: runs[-1][1].append(l)
            else: runs.append([k,[l]])
        # panels: N-run of 2k followed by T-run whose first k entries are names
        panels=[]
        for i in range(len(runs)-1):
            if runs[i][0]=="N" and len(runs[i][1])>=40 and runs[i+1][0]=="T":
                nums=runs[i][1]; k=len(nums)//2; names=runs[i+1][1][:k]
                assert len(nums)==2*k and names[-1]=="HBSC average", (pn, len(nums), names[-3:])
                panels.append((nums[:k], nums[k:], names))
        assert len(panels)==3, (pn,len(panels))
        for age,(g,b,names) in zip([11,13,15],panels):
            for name,gv,bv in zip(names,g,b):
                c=CN.get(name,name)
                out.append(dict(country=c,wave="2001/02",year_end=2002,age=age,sex="girl",item=item,value_pct=float(gv),source_page_or_table=f"p.{pn} {fig[:9]}"))
                out.append(dict(country=c,wave="2001/02",year_end=2002,age=age,sex="boy",item=item,value_pct=float(bv),source_page_or_table=f"p.{pn} {fig[:9]}"))
    df=pd.DataFrame(out); df["source_doc"]=DOC
    return df
if __name__=="__main__":
    df=parse(); print(df.groupby(["item","age","sex"]).size().unstack().to_string())
    print(df[df.country.isin(["HBSC average","United States","Wales"])&(df.item=="schoolwork_pressure")].pivot_table(index=["country","age"],columns="sex",values="value_pct").to_string())
    print(df[df.country=="HBSC average"].pivot_table(index=["item","age"],columns="sex",values="value_pct").to_string())
