"""Preview one report part: uv run python scripts/report/parts/_run_part.py <name> [<name> ...]
Writes build/parts/<name>.html (a standalone page with the fragments and their charts) and prints the fragment keys and sizes."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from report_lib import load_parts, ROOT
names = sys.argv[1:] or sys.exit(__doc__)
figs = {}; frags = load_parts(figs, only=set(names), strict=True)
css = (ROOT/"scripts/report/90_build_report.py").read_text().split("<style>")[1].split("</style>")[0].replace("{{", "{").replace("}}", "}")
(ROOT/"build/parts").mkdir(parents=True, exist_ok=True)
for n in names:
    body = "\n".join(v for k, v in frags.items())
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>part {n}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.3/plotly.min.js"></script><style>{css}</style></head><body><div class="wrap">{body}</div>
<script>const FIGS = {json.dumps({k: json.loads(v.to_json()) for k, v in figs.items()})};
for (const [k, f] of Object.entries(FIGS)) {{ const el = document.getElementById('fig-'+k); if (el) Plotly.react(el, f.data, Object.assign({{}}, f.layout, {{autosize: true}}), {{displayModeBar: false, responsive: true}}); }}</script></body></html>"""
    (ROOT/f"build/parts/{n}.html").write_text(page)
for k, v in frags.items(): print(f"  {k}: {len(v):,} chars")
print("figures:", ", ".join(figs) or "(none)"); print("preview:", ", ".join(str(ROOT/f"build/parts/{n}.html") for n in names))
