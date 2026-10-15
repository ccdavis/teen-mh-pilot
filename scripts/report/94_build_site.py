"""Build the self-contained report site in docs/ (index.html + local Plotly + local fonts + figures) from build/report.html."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; S = ROOT/"docs"; (S/"assets").mkdir(parents=True, exist_ok=True); (S/"figures").mkdir(exist_ok=True)
import shutil, urllib.request
if not (S/"assets/plotly.min.js").exists(): urllib.request.urlretrieve("https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.3/plotly.min.js", S/"assets/plotly.min.js")
for png in (ROOT/"build/figures").glob("*.png"): shutil.copy(png, S/"figures"/png.name)
html = (ROOT/"build/report.html").read_text()
title = re.search(r"<title>(.*?)</title>", html).group(1)
body = re.sub(r"<title>.*?</title>", "", html, count=1)
body = body.replace('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">', '<link rel="stylesheet" href="assets/fonts.css">')
body = body.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.3/plotly.min.js"></script>', '<script src="assets/plotly.min.js"></script>')
assert "googleapis" not in body and "cdnjs" not in body
# download links for the print editions, placed before the reproducibility note
body = body.replace('<p class="caption">Reproducibility:', '<p class="caption">Print editions: <a href="Teen_Distress_Pilot.pdf">PDF</a> · <a href="Teen_Distress_Pilot.docx">Word</a>. Static images of every chart are in <code>figures/</code>.</p>\n<p class="caption">Reproducibility:', 1)
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Public-data pilot results for the smartphone vs. school-pressure explanations of rising adolescent distress.">
<style>:root{{color-scheme:light dark}} html{{margin:0}} img{{max-width:100%}} [hidden]{{display:none!important}}</style>
</head>
<body>
{body}
</body>
</html>"""
(S/"index.html").write_text(page); print("docs/index.html", len(page), "bytes")
