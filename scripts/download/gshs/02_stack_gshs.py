"""Stack GSHS country-rounds into one harmonized parquet.

Reads each data/external/gshs/<ISO>_<YEAR>/ directory (all data files; prefers .dta for value
labels, falls back to .csv/.sav), identifies core items by variable label (Q-numbering shifts
across rounds), recodes 0/1 indicators using value-label text, validates against the CDC-derived
QN* dichotomies where present, and writes:
  data/extracts/gshs/gshs_stacked.parquet
  data/compiled/gshs/gshs_inventory.csv   (one row per country-round)
  data/extracts/gshs/gshs_files.csv       (one row per data file)
"""
import json, re, glob, pathlib, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
ROOT = pathlib.Path(__file__).resolve().parents[3]
EXT, OUT, COMP = ROOT / 'data/external/gshs', ROOT / 'data/extracts/gshs', ROOT / 'data/compiled/gshs'
OUT.mkdir(parents=True, exist_ok=True); COMP.mkdir(parents=True, exist_ok=True)

# construct -> (label regex, exclude regex)
ITEMS = {
    'age':               (r'how old|^age\b|custom age|\bage\b', r'first|before|when you|cigarette|drink|sex|alcohol|marijuana|drug|tried|start|old were'),
    'sex':               (r'^sex$|^what is your sex|^gender|\bsex\b', r'intercourse|had sex|sexual|partner|condom|first'),
    'grade':             (r'grade|class|form|standard|year are you', r'homework|missed|absent|during class'),
    'lonely':            (r'lonel', None),
    'worried_sleep':     (r'sleep', r'enough|hours'),
    'sad_hopeless':      (r'sad|hopeless', None),
    'suicide_consider':  (r'consider', None),
    'suicide_plan':      (r'plan', r'meal|birth|family plan'),
    'suicide_attempt':   (r'attempt', None),
    'close_friends':     (r'close friend', None),
    'parents_understand':(r'understand', None),
    'pa_days':           (r'physical activity|physically active|active 60|active.{0,15}60 min|days active', r'usual week|typical week|physical education|PE class|walk|bike|not physically'),
    'sit_hours':         (r'sitting|sit\b', None),
}
NET = r'internet|phone|computer|screen|online|social media|video game|television|\btv\b|gaming|electronic|cyber|social network'

def yesno(lab):
    l = lab.strip().lower()
    if l.startswith('yes'): return 1
    if l.startswith('no'): return 0
    return np.nan
def most_always(lab):
    l = lab.strip().lower()
    if 'most' in l or 'always' in l: return 1
    if any(k in l for k in ['never', 'rarely', 'sometimes']): return 0
    return np.nan
def attempt(lab):
    l = lab.strip().lower()
    m = re.match(r'\s*(\d+)', l)
    if l.startswith('0') or l.startswith('no') or 'zero' in l: return 0
    if m or 'time' in l or 'more' in l: return 1
    return np.nan
def zero_friends(lab):
    l = lab.strip().lower()
    if l.startswith('0') or l.startswith('none') or 'no close' in l: return 1
    if re.match(r'\s*\d', l) or 'more' in l: return 0
    return np.nan
def first_int(lab):
    m = re.search(r'(\d+)', str(lab)); return int(m.group(1)) if m else np.nan
def sit3(lab):
    l = lab.lower()
    if 'less than 1' in l or l.startswith('1 to 2') or l.startswith('1-2') or l.startswith('less') or '1 or 2' in l: return 0
    m = re.match(r'\s*(\d+)', l)
    if m: return 1 if int(m.group(1)) >= 3 else 0
    if 'more than' in l: return 1
    return np.nan

RECODE = {  # construct -> (new name, label-fn, fallback code-fn)
    'lonely':            ('lonely',            most_always, lambda v: np.where(v.isna(), np.nan, (v >= 4).astype(float))),
    'worried_sleep':     ('worried_sleep',     most_always, lambda v: np.where(v.isna(), np.nan, (v >= 4).astype(float))),
    'sad_hopeless':      ('sad_hopeless',      yesno,       lambda v: np.where(v.isna(), np.nan, (v == 1).astype(float))),
    'suicide_consider':  ('suicide_consider',  yesno,       lambda v: np.where(v.isna(), np.nan, (v == 1).astype(float))),
    'suicide_plan':      ('suicide_plan',      yesno,       lambda v: np.where(v.isna(), np.nan, (v == 1).astype(float))),
    'suicide_attempt':   ('suicide_attempt',   attempt,     lambda v: np.where(v.isna(), np.nan, (v >= 2).astype(float))),
    'close_friends':     ('no_close_friends',  zero_friends,lambda v: np.where(v.isna(), np.nan, (v == 1).astype(float))),
    'parents_understand':('parents_understand',most_always, lambda v: np.where(v.isna(), np.nan, (v >= 4).astype(float))),
    'pa_days':           ('pa_days',           first_int,   lambda v: v - 1),
    'sit_hours':         ('sit_3plus',         sit3,        lambda v: np.where(v.isna(), np.nan, (v >= 3).astype(float))),
    'age':               ('age_yrs',           first_int,   lambda v: v + 10),
    'sex':               ('female',            lambda l: 1 if l.lower().startswith('f') else (0 if l.lower().startswith('m') else np.nan),
                                                            lambda v: np.where(v.isna(), np.nan, (v == 2).astype(float))),
}
QN_CHECK = {'lonely': r'lonel', 'worried_sleep': r'sleep', 'suicide_consider': r'consider', 'suicide_plan': r'plan',
            'suicide_attempt': r'attempt', 'no_close_friends': r'no close friend', 'sad_hopeless': r'sad|hopeless'}

def read_file(path):
    """Return (df, varlabels, valuelabels-by-var)."""
    p = pathlib.Path(path)
    if p.suffix.lower() == '.dta':
        r = pd.read_stata(p, convert_categoricals=False, iterator=True)
        vl = r.value_labels(); labs = r.variable_labels(); df = r.read()
        lbl = dict(zip(r._varlist, r._lbllist)) if hasattr(r, '_lbllist') else {}
        vals = {v: vl[lbl[v]] for v in df.columns if lbl.get(v) in vl}
        return df, labs, vals
    if p.suffix.lower() == '.sav':
        import pyreadstat
        df, m = pyreadstat.read_sav(str(p))
        return df, m.column_names_to_labels, m.variable_value_labels
    df = pd.read_csv(p, low_memory=False)
    return df, {}, {}

def pick(labs, construct, used):
    pat, excl = ITEMS[construct]
    hits = []
    for name, lab in labs.items():
        if name in used or not lab: continue
        if name.upper().startswith('QN') or name.lower().startswith('qn'): continue
        if re.search(pat, lab, re.I) and not (excl and re.search(excl, lab, re.I)):
            hits.append(name)
    return hits

def process_round(d):
    d = pathlib.Path(d); tag = d.name; iso, year = tag.split('_')
    cat = json.load(open(d / 'catalog.json')) if (d / 'catalog.json').exists() else {}
    api_labs = {v['name']: (v.get('labl') or '') for v in json.load(open(d / 'variables.json'))['variables']} if (d / 'variables.json').exists() else {}
    files = json.loads((d / 'files.json').read_text()) if (d / 'files.json').exists() else []
    if isinstance(files, dict): files = files.get('files', [])
    data = [f['filename'] for f in files if re.search(r'\.(dta|sav|csv)$', f['filename'], re.I)]
    # group by stem: prefer dta > sav > csv
    stems = {}
    for f in data:
        stem = re.sub(r'\.(dta|sav|csv)$', '', f, flags=re.I).lower()
        stems.setdefault(stem, []).append(f)
    parts, frows = [], []
    # national vs subnational parts: keep only the national file(s) when present
    stem_list = list(stems)
    nat = [st for st in stem_list if 'national' in st]
    if not nat and len(stem_list) > 1:
        sizes = {}
        for st in stem_list:
            fs = sorted(stems[st], key=lambda f: {'.dta': 0, '.sav': 1, '.csv': 2}[pathlib.Path(f).suffix.lower()])
            try: sizes[st] = len(read_file(d / fs[0])[0])
            except Exception: sizes[st] = -1
        for st in stem_list:
            if sizes[st] > 0 and sizes[st] == sum(v for k, v in sizes.items() if k != st): nat = [st]
    for stem, fs in stems.items():
        stack_it = (not nat) or (stem in nat)
        fs.sort(key=lambda f: {'.dta': 0, '.sav': 1, '.csv': 2}[pathlib.Path(f).suffix.lower()])
        f = fs[0]
        try:
            df, labs, vals = read_file(d / f)
        except Exception as e:
            frows.append({'round': tag, 'file': f, 'n': 0, 'error': str(e)[:200]}); continue
        # unify labels: file labels first, API fallback (case-insensitive name match)
        api_ci = {k.lower(): v for k, v in api_labs.items()}
        labs = {c: (labs.get(c) or api_ci.get(c.lower(), '')) for c in df.columns}
        vals = {c: {float(k): str(v) for k, v in vv.items()} for c, vv in vals.items()}
        out = pd.DataFrame(index=df.index)
        out['iso3'], out['year'], out['country'], out['datafile'] = iso, int(year), cat.get('nation', iso), f
        out['catalog_id'] = cat.get('id', '')
        cols_ci = {c.lower(): c for c in df.columns}
        def find(names):
            for n in names:
                if n in cols_ci: return cols_ci[n]
        wcol = find(['weight', 'wt', 'weights', 'sampleweight', 'finalweight', 'final_weight'])
        pcol = find(['psu', 'cluster']); scol = find(['stratum', 'strata', 'stratum_id'])
        out['weight'] = pd.to_numeric(df[wcol], errors='coerce') if wcol else np.nan
        out['psu'] = df[pcol].astype(str) if pcol else None
        out['stratum'] = df[scol].astype(str) if scol else None
        used, mapping, srcs = set([wcol, pcol, scol]), {}, {}
        for construct in ITEMS:
            hits = pick(labs, construct, used)
            if not hits: continue
            src = hits[0]; used.add(src); mapping[construct] = src
            raw = pd.to_numeric(df[src], errors='coerce')
            out[f'raw_{construct}'] = raw
            out[f'src_{construct}'] = src
            if construct in RECODE:
                new, fn_lab, fn_code = RECODE[construct]
                if src in vals and vals[src]:
                    m = {k: fn_lab(v) for k, v in vals[src].items()}
                    out[new] = raw.map(m); srcs[construct] = 'labels'
                else:
                    out[new] = fn_code(raw); srcs[construct] = 'assumed'
            elif construct == 'grade':
                out['grade'] = raw
        # sitting raw categories preserved as raw_sit_hours; pa_days numeric
        # internet/phone/screen items
        net = [c for c in df.columns if labs.get(c) and re.search(NET, labs[c], re.I) and not c.upper().startswith('QN')]
        for c in net:
            out[f'net_{c}'] = pd.to_numeric(df[c], errors='coerce')
        # validation vs QN* indicators (1=yes, 2=no)
        checks = {}
        for new, pat in QN_CHECK.items():
            if new not in out: continue
            construct = [k for k, v in RECODE.items() if v[0] == new][0]
            srcq = mapping.get(construct, '')
            m = re.match(r'^[Qq](\d+)$', srcq)
            qn = [c for c in df.columns if m and c.upper() == f'QN{m.group(1)}']
            if not qn:
                qn = [c for c in df.columns if c.upper().startswith('QN') and labs.get(c) and re.search(pat, labs[c], re.I)]
            if qn:
                q = pd.to_numeric(df[qn[0]], errors='coerce').map({1: 1, 2: 0})
                both = out[new].notna() & q.notna()
                checks[new] = round(float((out[new][both] == q[both]).mean()), 4) if both.any() else np.nan
        out['national_file'] = bool(nat) and stem in nat
        frows.append({'round': tag, 'iso3': iso, 'year': int(year), 'country': cat.get('nation', ''), 'file': f, 'n': len(df),
                      'stacked': stack_it, 'national_file': bool(nat) and stem in nat,
                      'weight_var': wcol, 'psu_var': pcol, 'stratum_var': scol,
                      'labels_from': pathlib.Path(f).suffix.lower(),
                      **{f'src_{k}': v for k, v in mapping.items()},
                      **{f'coding_{k}': v for k, v in srcs.items()},
                      **{f'qncheck_{k}': v for k, v in checks.items()},
                      'net_items': '; '.join(f'{c}={labs[c][:60]}' for c in net)})
        if stack_it: parts.append(out)
    return parts, frows

def main():
    dirs = sorted(glob.glob(str(EXT / '*_[0-9][0-9][0-9][0-9]')))
    if len(sys.argv) > 1: dirs = [d for d in dirs if pathlib.Path(d).name in sys.argv[1:]]
    allparts, allrows = [], []
    for d in dirs:
        parts, rows = process_round(d)
        print(pathlib.Path(d).name, [(r['file'], r['n']) for r in rows], flush=True)
        allparts += parts; allrows += rows
    files = pd.DataFrame(allrows); files.to_csv(COMP / 'gshs_files.csv', index=False)
    st = pd.concat(allparts, ignore_index=True)
    for c in st.columns:
        if c.startswith('src_') or c in ('psu', 'stratum', 'datafile', 'catalog_id'): st[c] = st[c].astype('string')
    st.to_parquet(OUT / 'gshs_stacked.parquet', index=False)
    # country-round inventory
    ind = ['lonely', 'worried_sleep', 'sad_hopeless', 'suicide_consider', 'suicide_plan', 'suicide_attempt', 'no_close_friends',
           'parents_understand', 'pa_days', 'sit_3plus', 'age_yrs', 'female', 'grade']
    inv = []
    for (iso, yr, ctry), g in st.groupby(['iso3', 'year', 'country']):
        row = {'iso3': iso, 'year': yr, 'country': ctry, 'n_students': len(g), 'n_files': g.datafile.nunique(),
               'weight_var': files.loc[(files['round'] == f'{iso}_{yr}'), 'weight_var'].dropna().unique().tolist()[:1],
               'has_weight': float(g.weight.notna().mean()) if 'weight' in g else 0,
               'items': ','.join(i for i in ind if i in g and g[i].notna().any())}
        for i in ['lonely', 'worried_sleep', 'suicide_consider', 'suicide_plan', 'suicide_attempt', 'no_close_friends']:
            if i in g and g[i].notna().any():
                w = g.weight.fillna(1)
                row[f'p_{i}'] = round(float(np.average(g[i].fillna(0)[g[i].notna()], weights=w[g[i].notna()])), 4)
        row['net_items'] = '; '.join(sorted(set(x for x in files.loc[files['round'] == f'{iso}_{yr}', 'net_items'].dropna() if x)))
        inv.append(row)
    inv = pd.DataFrame(inv); inv['weight_var'] = inv.weight_var.str[0]
    inv.to_csv(COMP / 'gshs_inventory.csv', index=False)
    print(inv.to_string()); print('stacked', st.shape)

if __name__ == '__main__':
    main()
