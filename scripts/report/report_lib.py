"""Shared helpers for the report builder (90_build_report.py) and the per-source report parts in scripts/report/parts/.

A part is a module scripts/report/parts/<name>.py exposing `build(ctx) -> dict[str, str]`: it reads results/tables/, adds plotly
figures to ctx.figs (ctx.figs["key"] = ctx.base(fig)) and returns HTML fragments keyed by section name. The builder places each
fragment with `{extra['<key>']}`. Preview one part with `uv run python scripts/report/parts/_run_part.py <name>`.
"""
import os, json, pathlib, importlib.util, types, traceback
import pandas as pd, numpy as np, plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; PARTS = ROOT/"scripts/report/parts"
BOY, GIRL, ALL, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#8a919c"
PAL = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"]

def base(fig, h=380, **kw):
    lay = dict(template="none", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=h, margin=dict(l=48,r=16,t=36,b=40),
        font=dict(family="'IBM Plex Sans', system-ui, sans-serif", size=12), hovermode="x unified", legend=dict(orientation="h", y=-0.18, x=0)); lay.update(kw)
    fig.update_layout(**lay)
    fig.update_xaxes(showgrid=False, zeroline=False); fig.update_yaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig

def covid_band(fig, row=None, col=None):
    fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(128,128,128,.12)", line_width=0, row=row, col=col)

def fig_div(key):
    return f'<div class="chart" id="fig-{key}"></div>'

def fmt(coef, se, d=2, bold_t=None):
    """'+0.90 (0.44)'; with bold_t=1.96, wraps in <strong> when |coef/se| exceeds it."""
    s = f"{coef:+.{d}f} ({se:.{d}f})"
    return f"<strong>{s}</strong>" if (bold_t and se > 0 and abs(coef/se) > bold_t) else s

def table(header, rows, cls=""):
    """HTML table: header = list of column labels, rows = list of lists (cells are inserted as-is, so pre-format numbers)."""
    th = "".join(f"<th>{h}</th>" for h in header)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table{(" class=" + chr(34) + cls + chr(34)) if cls else ""}><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def make_ctx(figs):
    return types.SimpleNamespace(ROOT=ROOT, T=T, figs=figs, base=base, covid_band=covid_band, fig_div=fig_div, fmt=fmt, table=table,
                                 PAL=PAL, BOY=BOY, GIRL=GIRL, ALL=ALL, MUTED=MUTED, go=go, make_subplots=make_subplots, pd=pd, np=np)

def load_parts(figs, only=None, strict=None):
    """Run every scripts/report/parts/<name>.py (names not starting with '_') and return the merged fragment dict.
    A part that raises is reported and replaced by a pending note unless strict (env REPORT_STRICT=1 or strict=True)."""
    strict = bool(int(os.environ.get("REPORT_STRICT", "0"))) if strict is None else strict
    out = {}
    for p in sorted(PARTS.glob("*.py")):
        if p.stem.startswith("_") or (only and p.stem not in only): continue
        spec = importlib.util.spec_from_file_location(f"report_part_{p.stem}", p); mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod); frags = mod.build(make_ctx(figs))
            assert isinstance(frags, dict) and all(isinstance(v, str) for v in frags.values()), f"{p.name}: build() must return dict[str, str]"
            dup = set(frags) & set(out); assert not dup, f"{p.name}: fragment keys already used by another part: {dup}"
            out.update(frags); print(f"part {p.stem}: {', '.join(frags)}")
        except Exception as e:
            if strict: raise
            traceback.print_exc(); print(f"WARNING: part {p.stem} failed ({e}); inserting a pending note")
            out[p.stem] = f'<p class="pending">Pending: the {p.stem} section could not be built ({type(e).__name__}).</p>'
    return out
