# Report parts (Phase 2 sections)

Each module here builds one source's report section from `results/tables/` and is merged into the report by
`scripts/report/90_build_report.py` through `report_lib.load_parts()`. The builder places every fragment a part returns
with `{extra['<key>']}` in its page template, so a part owns its text, tables and charts but not its position.

```python
"""<one-line purpose>"""
def build(ctx):
    pd, np, go = ctx.pd, ctx.np, ctx.go
    d = pd.read_csv(ctx.T/"<source>_<table>.csv")
    fig = go.Figure(...); ctx.figs["<source>_<chart>"] = ctx.base(fig, h=380)      # chart keys: lowercase, source-prefixed, unique
    html = f"""<h3 id="<source>">Section title</h3>
<p>...</p>
{ctx.fig_div('<source>_<chart>')}
<p class="caption">...</p>
{ctx.table(["Outcome", "Sex", "Effect (SE)"], [[...], ...])}
<div class="note"><strong>Assessment.</strong> ...</div>"""
    return {"<source>": html}                                                       # fragment keys: unique across parts
```

Conventions (match the Phase 1 sections): `ctx.base(fig)` for every figure (palette `ctx.PAL`, `ctx.BOY`, `ctx.GIRL`, `ctx.ALL`,
`ctx.MUTED`; `ctx.covid_band(fig)` for a 2020 marker), `<h3>` for the section heading and `<h4>`/`<h5>` beneath, `<p class="caption">`
under charts and tables, estimates written as `+0.90 (0.44)` via `ctx.fmt(coef, se)`, and a closing `<div class="note">` assessment that
states what the test shows for H1, H2, H3 or H0. Numbers in the prose must come from the tables the part reads, not be typed in by hand,
so a rerun of the analysis updates the text.

Preview a part on its own: `uv run python scripts/report/parts/_run_part.py <name>` writes `build/parts/<name>.html`. A failing part is
replaced by a pending note in the full build unless `REPORT_STRICT=1`.
