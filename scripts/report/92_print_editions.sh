#!/bin/bash
# Rebuild the print editions (PDF + Word) into docs/ from build/report.html. Run from the repo root after scripts/report/90_build_report.py.
set -e; cd "$(dirname "$0")/../.."
uv run python - <<'PY'
from playwright.sync_api import sync_playwright
import pathlib, glob, re, os
html = pathlib.Path("build/report.html").read_text()
src = html.replace('src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.3/plotly.min.js"', 'src="../docs/assets/plotly.min.js"').replace("<nav>", "<nav style='display:none'>")
pathlib.Path("build/_preview.html").write_text("<!doctype html><html data-theme='light'><head><meta charset='utf-8'></head><body>" + src + "</body></html>")
exe = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell")))[-1]
keys = re.findall(r'id="fig-([a-z_0-9]+)"', html); pathlib.Path("build/figures").mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page(viewport={"width":1000,"height":900}, device_scale_factor=2)
    pg.goto("file://"+str(pathlib.Path("build/_preview.html").resolve())); pg.wait_for_timeout(9000)
    for k in keys: pg.locator(f"#fig-{k}").screenshot(path=f"build/figures/{k}.png")
    b.close()
static = re.sub(r'<div class="chart" id="fig-([a-z_0-9]+)"></div>', r'<p class="figimg"><img src="figures/\1.png" alt="" width="6.5in"></p>', html)
static = re.sub(r"<script.*?</script>", "", static, flags=re.S); static = re.sub(r"<nav>.*?</nav>", "", static, flags=re.S)
static = static.replace("and public files; every chart has hover values.</p>", "and public files. This is the print edition of the interactive report; the charts are static images and the data tables behind each are listed in the project archive.</p>")
pathlib.Path("build/report_static.html").write_text(static)
print_css = "<style>@page{size:Letter;margin:0.8in 0.75in} body{font-size:11pt;line-height:1.45;padding:0;max-width:none} .wrap{max-width:none} h1{font-size:22pt;margin-top:0} h2{font-size:16pt;page-break-after:avoid} h3{font-size:13pt;page-break-after:avoid} h4,h5{page-break-after:avoid} p,li{max-width:none} p.figimg{page-break-inside:avoid;margin:10px 0 4px} p.figimg img{border:1px solid #d6dbe3;border-radius:4px;width:100%} table{font-size:9pt} tr{page-break-inside:avoid} .tw{overflow:visible} .note{page-break-inside:avoid} a{color:inherit;text-decoration:underline}</style>"
pathlib.Path("build/_print.html").write_text("<!doctype html><html data-theme='light'><head><meta charset='utf-8'></head><body>" + static.replace("</style>", "</style>" + print_css, 1) + "</body></html>")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page()
    pg.goto("file://"+str(pathlib.Path("build/_print.html").resolve()), wait_until="networkidle"); pg.wait_for_timeout(2000); pg.emulate_media(media="print")
    pg.pdf(path="docs/Teen_Distress_Pilot.pdf", format="Letter", print_background=True, margin={"top":"0.8in","bottom":"0.8in","left":"0.75in","right":"0.75in"}, display_header_footer=True, header_template="<div></div>", footer_template="<div style='font-size:8pt;color:#777;width:100%;text-align:center;font-family:sans-serif'>Teen Distress Pilot · page <span class='pageNumber'></span> of <span class='totalPages'></span></div>")
    b.close()
s = re.sub(r"<title>.*?</title>", "", static, count=1)
def add_cols(m):
    tbl = m.group(0); head = re.search(r"<thead>.*?</thead>", tbl, flags=re.S); n = len(re.findall(r"<th", head.group(0))) if head else 0
    if n == 0: return tbl
    w = {2:[26,74],3:[22,56,22] if "verdict" in tbl[:60] else [30,40,30],4:[34,22,22,22],5:[30,16,18,18,18]}.get(n, [round(100/n)]*n)
    return tbl.replace("<thead>", "<colgroup>" + "".join(f'<col width="{x}%">' for x in w) + "</colgroup><thead>", 1)
s = re.sub(r"<table[^>]*>.*?</table>", add_cols, s, flags=re.S); s = re.sub(r'<span class="pill[^"]*">(.*?)</span>', r'<b>\1</b>', s)
pathlib.Path("build/_pandoc.html").write_text(s)
PY
pandoc build/_pandoc.html -f html -t docx -o docs/Teen_Distress_Pilot.docx --resource-path=build --reference-doc=scripts/report/reference.docx && rm -f build/_preview.html build/_pandoc.html && uv run --with lxml python scripts/report/93_docx_fix.py docs/Teen_Distress_Pilot.docx
echo "written: docs/Teen_Distress_Pilot.pdf and .docx"
