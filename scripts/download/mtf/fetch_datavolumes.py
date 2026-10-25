"""Download the Monitoring the Future data volumes ("Questionnaire Responses from the Nation's High School Seniors", one PDF per
survey year) from the Internet Archive's Wayback Machine into data/external/mtf/datavolumes/<year>dv.pdf.

monitoringthefuture.org (and icpsr.umich.edu / deepblue.lib.umich.edu) sit behind a Cloudflare bot challenge that returns HTTP 403 to
curl, headless Chromium and remote fetchers from this host (checked 2026-10-24), so the volumes are taken from the Wayback captures
listed below (CDX query http://web.archive.org/cdx/search/cdx?url=monitoringthefuture.org/datavolumes/*&filter=statuscode:200).
The series was published for survey years 1975-2012; only 1996-2012 were ever posted as PDFs at the datavolumes/ path (1991-1995
exist in print only). Each download is checked (PDF header, page count via pdfplumber) and re-fetched if damaged.

Usage: uv run python scripts/download/mtf/fetch_datavolumes.py [--only 1998 1999]
"""
import subprocess, sys, time, pathlib, argparse
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/mtf/datavolumes"
CAPTURES = {  # year: (original URL, Wayback timestamp)
    1996: ("http://www.monitoringthefuture.org/datavolumes/1996/1996dv.pdf", "20110105171719"),
    1997: ("http://www.monitoringthefuture.org/datavolumes/1997/1997dv.pdf", "20110105173924"),
    1998: ("http://www.monitoringthefuture.org/datavolumes/1998/1998dv.pdf", "20110105165121"),
    1999: ("http://www.monitoringthefuture.org/datavolumes/1999/1999dv.pdf", "20110105165454"),
    2000: ("http://www.monitoringthefuture.org/datavolumes/2000/2000dv.pdf", "20110105174349"),
    2001: ("http://www.monitoringthefuture.org/datavolumes/2001/2001dv.pdf", "20110105170835"),
    2002: ("http://www.monitoringthefuture.org/datavolumes/2002/2002dv.pdf", "20110105172918"),
    2003: ("http://www.monitoringthefuture.org/datavolumes/2003/2003dv.pdf", "20110105173328"),
    2004: ("http://www.monitoringthefuture.org/datavolumes/2004/2004dv.pdf", "20110105172455"),
    2005: ("http://www.monitoringthefuture.org/datavolumes/2005/2005dv.pdf", "20110105165622"),
    2006: ("http://www.monitoringthefuture.org/datavolumes/2006/2006dv.pdf", "20110105164759"),
    2007: ("http://www.monitoringthefuture.org/datavolumes/2007/2007dv.pdf", "20110105170011"),
    2008: ("http://www.monitoringthefuture.org/datavolumes/2008/2008dv.pdf", "20110105173446"),
    2009: ("http://www.monitoringthefuture.org/datavolumes/2009/2009dv.pdf", "20110105172155"),
    2010: ("http://monitoringthefuture.org/datavolumes/2010/2010dv.pdf", "20110727035022"),
    2011: ("http://www.monitoringthefuture.org/datavolumes/2011/2011dv.pdf", "20130801084612"),
    2012: ("http://monitoringthefuture.org/datavolumes/2012/2012dv.pdf", "20140702235730"),
}
def ok(path):
    try:
        if not path.exists() or path.stat().st_size < 500_000 or path.read_bytes()[:5] != b"%PDF-": return False
        import pdfplumber
        with pdfplumber.open(path) as pdf: n = len(pdf.pages); _ = pdf.pages[min(5, n - 1)].extract_text()
        return n > 50
    except Exception as e:
        print(f"  check failed for {path.name}: {e}"); return False
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--only", nargs="*", type=int); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for y, (orig, ts) in CAPTURES.items():
        if a.only and y not in a.only: continue
        dst = OUT/f"{y}dv.pdf"
        if ok(dst): print(f"{y}: ok ({dst.stat().st_size:,} bytes)"); continue
        u = f"https://web.archive.org/web/{ts}id_/{orig}"
        for attempt in range(5):
            r = subprocess.run(["curl", "-sL", "--max-time", "900", "-o", str(dst), "-w", "%{http_code} %{size_download}", u], capture_output=True, text=True)
            print(f"{y}: attempt {attempt+1} -> {r.stdout}", flush=True)
            if ok(dst): print(f"{y}: verified ({dst.stat().st_size:,} bytes)"); break
            time.sleep(15 * (attempt + 1))
        else: print(f"{y}: FAILED after 5 attempts")
        time.sleep(3)
