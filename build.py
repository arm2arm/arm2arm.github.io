#!/usr/bin/env python3
"""
cv-page builder — data-driven static site generator.

Usage:  python3 build.py            (writes *.html to the repo root)
        python3 build.py --check    (validates only; prints issues, writes nothing)

EXTENDING THE SITE
  - Site metadata / nav / contact .... content/site.json
  - Publications ..................... content/pubs.json  (ORCID v2.1 works)
  - Gallery .......................... content/gallery.json (list of figures —
                                       add entries, figures render in a grid
                                       that grows automatically)
  - Home prose (overview, research) .. content/pages/home_*.html  (raw HTML)
  - Project deep-dives ............... content/pages/<id>_deepdive.html,
                                       referenced from PROJECTS below
  - Projects / Software / Benchmarks . data lists in this file (PROJECTS, SW)
  - Theme palette .................... style.css  (2x2: data-theme x data-accent)

Everything renders from these sources; there is no hand-edited HTML in the
deployed output.
"""
import json, re, sys, html as H, os

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, 'content')
CHECK_ONLY = '--check' in sys.argv

# ---------------------------------------------------------------- data ----
def load(name):
    path = os.path.join(CONTENT, name)
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit('build.py: missing %s — add it before building' % path)
    except json.JSONDecodeError as e:
        sys.exit('build.py: %s is not valid JSON: %s' % (path, e))

SITE   = load('site.json')
PUBS   = load('pubs.json')
GALLERY= load('gallery.json')

def frag(name):
    path = os.path.join(CONTENT, 'pages', name)
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        sys.exit('build.py: missing fragment %s' % path)

HOME_OVERVIEW = frag('home_overview.html')
HOME_RESEARCH = frag('home_research.html')
BENCH_SECTIONS = frag('bench_sections.html')

# Single source of truth for the browser-chrome + favicon colors; emitted
# as JSON into both inline scripts (a 5th palette = add one entry here +
# one CSS block in style.css).
THEME_COLORS = {
    'chrome': {'ocean-light': '#EFF3F6', 'ocean-dark': '#0B1626',
               'paper-light': '#F6F4EE', 'paper-dark': '#1B1915'},
    'fav':    {'ocean-light': '#1D6A96', 'ocean-dark': '#4FA3D1',
               'paper-light': '#A02C1E', 'paper-dark': '#D4714B'},
}

# Each project: title, lang badge, href, desc, meta (optional),
# details (optional path -> content/pages/<name>, rendered after the row).
# NOTE: title/lang/desc/meta may contain RAW HTML (b, em, span, a) — the
# convention for this project list; free text from JSON files, by contrast,
# is escaped by the builder.
PROJECTS = [
    dict(num='01', title='PhysicsLLM', lang='LLM · agents · vLLM',
         href='https://github.com/arm2arm/llm4reana',
         desc='Large language models and agentic assistants for physics research. Fine-tuning, local inference on AIP GPU clusters, and AI agents that execute real scientific workflows end to end — including driving REANA research platforms from natural language. Co-developed with Dr. T. Tong at AIP.',
         meta='see also <b>Benchmarks</b> — LLM/SQL results on the AIP endpoints'),
    dict(num='02', title='SH26', lang='Python · Dask · Parquet',
         href='https://gitlab.aip.de/akhalatyan/SH26',
         desc='A 400 million-star spectroscopic catalogue of the Milky Way. I own the end-to-end data pipeline: float32 schema design, full-catalogue Parquet joins (210&nbsp;GB) on HPC, the plotting engine, and the publication figure suite — plus the science work on the bulge, bar and disc populations it enables.',
         meta='402,121,784 stars · 3,032 parts · 140 columns'),
    dict(num='03', title='PMViewer / SPViewer', lang='C++ · OpenGL · HDF5',
         href='https://sourceforge.net/projects/pmviewer/',
         desc='Interactive 3-D particle and cosmological-simulation viewer (OpenGL/GLU/GLEW). B-tree spatial acceleration for tens of millions of particles, HDF5 snapshot reader with on-the-fly disk cache, camera/fly-through navigation, particle-selection tooling, PCA and histogram diagnostics. The tool behind visual exploration of MareNostrum-class simulations; open source since 2005.',
         meta='OpenGL · GLU · GLUT · GLEW · HDF5'),
    dict(num='04', title='VR@AIP', lang='web · WebGL',
         href='https://vr.aip.de',
         desc='A virtual reality tour of the Leibniz Institute for Astrophysics Potsdam — <span>vr.aip.de</span>. 360° photography of the Telegrafenberg campus and observatory halls turned into an interactive browser/VR tour (Panotour pipeline) for public outreach and campus visits.'),
    dict(num='05', title='DRP-Hub (PUNCH4NFDI)', lang='Kubernetes · REANA',
         href='https://drphub-p4n.aip.de',
         desc='Research infrastructure for <b>Digital Research Products</b> in particle physics and astrophysics under the PUNCH4NFDI project — reproducible, FAIR (Findable, Accessible, Interoperable, Reusable) analysis workflows as citable products. I contribute to the P4N hub instance (<span>drphub-p4n.aip.de</span>), the REANA-based execution backend, and the compute/storage layer. First author of the WCEDMVO maturity model (with E. Sacchi and H. Enke) that gives DRP-Hub its computed L0–L4 levels.',
         meta='FAIR data · NFDI · Kubernetes',
         details='drp_deepdive.html'),
    dict(num='06', title='AstroAgentAssistant', lang='Python · skills',
         href='https://github.com/arm2arm/AstroAgentAssistant',
         desc='A human-centric AI assistance system for astronomy: a curated, human-reviewed skill library that teaches AI agents reproducible astrophysics workflows — catalogues, simulations, instrumentation, data pipelines.'),
    dict(num='07', title='PUNCH4NFDI Infrastructure', lang='HPC · storage',
         href='https://doi.org/10.1051/epjconf/202533701264',
         desc='Compute and storage infrastructure for the German National Research Data Infrastructure (NFDI): scalable, reliable HPC services for scientific data — the substrate that DRP-Hub and the AIP data services run on.'),
]

SW = [
    ('AstroAgentAssistant', 'Python · skills', 'Human-centric AI assistance in astronomy — a curated, human-reviewed skill library that teaches agents reproducible astrophysics workflows.', 'https://github.com/arm2arm/AstroAgentAssistant', ''),
    ('SH26', 'Python · Dask · Parquet', '400M-star catalogue pipelines: float32 schema migration, full-catalogue joins, plotting engine and 129-figure publication suite.', 'https://gitlab.aip.de/akhalatyan/SH26', ''),
    ('dbbench-benchmarks', 'Python', 'S3 object-storage and LLM/SQL benchmark suites (RustFS vs VersityGW; AgentBench DBBench) with standardized dashboards.', 'https://github.com/arm2arm/dbbench-benchmarks', '<span>see <b>Benchmarks</b> page</span>'),
    ('starhorse_db', 'Jupyter', 'Tutorial and access layer for the StarHorse database at gaia.aip.de.', 'https://github.com/arm2arm/starhorse_db', ''),
    ('shboost24', 'Jupyter', 'SHBoost: transferring spectroscopic stellar labels to 217M Gaia DR3 XP stars.', 'https://github.com/arm2arm/shboost24', ''),
    ('llm4reana', 'Python', 'Experiments driving REANA research workflows with a locally hosted LLM (PhysicsLLM).', 'https://github.com/arm2arm/llm4reana', ''),
    ('reanademo1', 'REANA', 'Reference demo for running DRP-Hub analyses as REANA workflows.', 'https://github.com/arm2arm/reanademo1', ''),
    ('astro-aiko', 'Docker', 'Reproducible Docker base image for AIP astrophysics data analysis.', 'https://github.com/arm2arm/astro-aiko', ''),
    ('gaiautils', 'Python', 'Practical access utilities and cheatsheet for the gaia.aip.de portal.', 'https://github.com/arm2arm/gaiautils', ''),
    ('al', 'Python', 'LTO tape-management utility collection for HPC archival storage.', 'https://github.com/arm2arm/al', ''),
    ('StarTracer', 'C++', 'Traces AFOF star groups in GADGET cosmological simulations.', 'https://github.com/arm2arm/StarTracer', ''),
    ('mymc.sh', 'Shell', 'MinIO upload/download helper for large dataset transfers on the cluster.', 'https://github.com/arm2arm/mymc.sh', ''),
    ('excosm-potsdam-25', 'C · notes', 'Lecture notes and code from the EXCOSM Potsdam workshop (Horizon Europe).', 'https://github.com/arm2arm/excosm-potsdam-25', ''),
]

# ---------------------------------------------------------------- head ----
def nav_html(active):
    # `active` = lowercased NAV LABEL (e.g. 'projects'), 'home' for index
    # (matched via the 'index.html' href), or None for no highlight (404).
    AC = ' aria-current="page"'
    out = []
    for label, href in SITE['nav']:
        cur = active is not None and (
            label.lower() == active or os.path.basename(href.split('#')[0]).lower() == active)
        cls = 'nav-link active' if cur else 'nav-link'
        out.append('<a class="%s" href="%s"%s>%s</a>' % (cls, href, AC if cur else '', label))
    return '\n      '.join(out)

THEME_JS_PRE = '''<script>
/* apply saved theme + accent before first paint — no flash.
   Default (no saved choice): ocean + dark (blue). */
(function () {
  try {
    var t = localStorage.getItem('theme');
    if (t !== 'light' && t !== 'dark') { t = 'dark'; }
    var a = localStorage.getItem('accent');
    if (a !== 'ocean' && a !== 'paper') { a = 'ocean'; }
    var chrome = __CHROME__[a + '-' + t];
    var fav  = __FAV__[a + '-' + t];
    var r = document.documentElement;
    r.setAttribute('data-theme', t);
    r.setAttribute('data-accent', a);
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) { m.setAttribute('content', chrome); }
    var f = document.getElementById('favicon');
    if (f) {
      f.setAttribute("href", "data:image/svg+xml," + encodeURIComponent(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='13' fill='" + fav + "' font-family='Georgia'>A.</text></svg>"));
    }
    var b1 = document.getElementById('theme-toggle');
    if (b1) {
      b1.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      b1.setAttribute('aria-pressed', t === 'dark');
    }
    var b2 = document.getElementById('accent-toggle');
    if (b2) {
      b2.setAttribute('aria-label', a === 'ocean' ? 'Switch to Paper palette' : 'Switch to Ocean palette');
      b2.setAttribute('aria-pressed', a === 'paper');
    }
  } catch (e) {}
})();
</script>'''

THEME_JS_TOGGLES = '''<script>
/* theme + accent toggles — persist per visitor */
(function () {
  var chrome = __CHROME__;
  var fav  = __FAV__;
  function apply() {
    var r = document.documentElement;
    var t = r.getAttribute('data-theme') || 'light';
    var a = r.getAttribute('data-accent') || 'ocean';
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) { m.setAttribute('content', chrome[a + '-' + t]); }
    var f = document.getElementById('favicon');
    if (f) {
      f.setAttribute("href", "data:image/svg+xml," + encodeURIComponent(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='13' fill='" + fav[a + '-' + t] + "' font-family='Georgia'>A.</text></svg>"));
    }
    var b1 = document.getElementById('theme-toggle');
    if (b1) {
      b1.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      b1.setAttribute('aria-pressed', t === 'dark');
    }
    var b2 = document.getElementById('accent-toggle');
    if (b2) {
      b2.setAttribute('aria-label', a === 'ocean' ? 'Switch to Paper palette' : 'Switch to Ocean palette');
      b2.setAttribute('aria-pressed', a === 'paper');
    }
  }
  var b1 = document.getElementById('theme-toggle');
  if (b1) { b1.addEventListener('click', function () {
    var r = document.documentElement;
    var t = r.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    r.setAttribute('data-theme', t);
    try { localStorage.setItem('theme', t); } catch (e) {}
    apply();
  }); }
  var b2 = document.getElementById('accent-toggle');
  if (b2) { b2.addEventListener('click', function () {
    var r = document.documentElement;
    var a = r.getAttribute('data-accent') === 'ocean' ? 'paper' : 'ocean';
    r.setAttribute('data-accent', a);
    try { localStorage.setItem('accent', a); } catch (e) {}
    apply();
  }); }
})();
</script>'''

MAIL_JS = '''<script>
// Email assembled at runtime from the reversed, obfuscated data-mail attribute
// so crawlers scraping the HTML source never see a bare address.
(function () {
  var a = document.getElementById('mail-btn');
  if (!a || !a.dataset.mail) return;
  var m = a.dataset.mail.split('').reverse().join('').replace('|', '@');
  a.href = 'mailto:' + m;
  var v = a.querySelector('.cval');
  if (v) v.innerHTML = m + ' <span class="arrow">→</span>';
})();
</script>'''

HEAD = '''<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="ocean">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0B1626">
<link id="favicon" rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ctext y='13' font-size='13' fill='%234FA3D1' font-family='Georgia'%3EA.%3C/text%3E%3C/svg%3E">
{prejs}
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Spline+Sans+Mono:wght@400;500&family=Spectral:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<nav class="topnav">
  <div class="nav-inner">
    <a class="brand" href="index.html">{brand}<span class="dot">.</span></a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation menu">
    <label for="nav-toggle" class="nav-burger" aria-label="Menu"><span></span></label>
    <div class="nav-links">
      {links}
      <span class="nav-tools">
        <button type="button" class="accent-toggle" id="accent-toggle" aria-label="Switch to Paper palette" aria-pressed="false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/></svg>
        </button>
        <button type="button" class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode" aria-pressed="false">
          <svg class="ic-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4m11.4-11.4 1.4-1.4"/></svg>
          <svg class="ic-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        </button>
      </span>
    </div>
  </div>
</nav>
{toggjs}
<main id="main">
'''

def head(active, title, desc):
    # NOTE: nav labels / brand / kicker are RAW HTML by convention (site.json
    # may carry &amp; / <span>); free-text fields from JSON are escaped in the
    # page builders below.
    _c = json.dumps(THEME_COLORS['chrome'])
    _f = json.dumps(THEME_COLORS['fav'])
    prejs = THEME_JS_PRE.replace('__CHROME__', _c).replace('__FAV__', _f)
    toggjs = THEME_JS_TOGGLES.replace('__CHROME__', _c).replace('__FAV__', _f)
    return HEAD.format(prejs=prejs, title=title, desc=desc,
                       brand=SITE['brand'], links=nav_html(active),
                       toggjs=toggjs)

def contact_block():
    rows = []
    for c in SITE['contact']:
        if c.get('mail'):
            rows.append('''        <a id="mail-btn" data-mail="{mail}">
          <span class="clabel">{label}</span>
          <span class="cval">…</span>
        </a>'''.format(mail=c['mail'], label=c['label']))
        else:
            rows.append('''        <a href="{url}" target="_blank" rel="noopener">
          <span class="clabel">{label}</span>
          <span class="cval">{val} <span class="arrow">→</span></span>
        </a>'''.format(url=c['url'], label=c['label'], val=c['val']))
    return '''    <div class="contact-list">
''' + '\n'.join(rows) + '''
    </div>'''

FOOTER = None  # built in build_footer() from site.json (single source of truth)

def build_footer():
    items = []
    for c in SITE['contact']:
        if c.get('label') in ('GitHub', 'ORCID', 'LinkedIn') and c.get('url'):
            items.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (c['url'], c['label']))
    links = ' · '.join(items)
    return '''</main>
<footer class="footbar">
  <div class="wrap">
    <span class="cr">%s</span>
    <span class="fl">
      %s
    </span>
  </div>
</footer>''' % (SITE['footer'], links)

def page(active, title, desc, body, mail=False, noindex=False):
    head_part = head(active, title, desc)
    if noindex:
        head_part = head_part.replace('<title>', '<meta name="robots" content="noindex">\n<title>', 1)
    p = head_part + body + build_footer() + '\n'
    if mail:
        p += MAIL_JS
    p += '\n</body>\n</html>\n'
    return p

# ---------------------------------------------------------------- blocks ----
def _pub_sort_key(x):
    # in-press / undated works sort first; then year desc; then title
    yr = x.get('year') or ''
    pending = 0 if (yr.upper() in ('IN PRESS', 'UNDATED', '')) else 1
    return (pending, -(int(yr) if yr.isdigit() else 0), x.get('title', ''))

def pub_rows():
    rows = []
    for s in sorted(PUBS, key=_pub_sort_key):
        t = re.sub(r'\s+', ' ', H.unescape(s.get('title') or '')).strip()
        doi = s.get('doi') or ''
        t_attr = t.replace('"', chr(39))
        doi_html = ('<a class="doi" href="https://doi.org/' + H.escape(doi, quote=True) +
                    '" target="_blank" rel="noopener" aria-label="DOI for: ' + t_attr +
                    '">DOI \u2197</a>' if doi else '')
        yr = H.escape(s.get('year') or '\u2014')
        rows.append('      <li>\n        <span class="year">%s</span>\n        <span class="cite">%s</span>\n        %s\n      </li>' % (yr, H.escape(t), doi_html))
    return '\n'.join(rows)

def project_row(p):
    meta = '\n        <div class="rmeta"><span>%s</span></div>' % p['meta'] if p.get('meta') else ''
    return '''      <a class="row" href="%s" target="_blank" rel="noopener">
        <div class="rhead"><span class="rnum">%s</span><span class="rtitle">%s <span class="lang">%s</span></span></div>
        <p class="rdesc">%s</p>%s
      </a>''' % (p['href'], p['num'], p['title'], p['lang'], p['desc'], meta)

def sw_row(n, title, lang, desc, href, meta=''):
    m = f'<div class="rmeta">{meta}</div>' if meta else ''
    return f'''      <a class="row" href="{href}" target="_blank" rel="noopener">
        <div class="rhead"><span class="rnum">{n:02d}</span><span class="rtitle">{title} <span class="lang">{lang}</span></span></div>
        <p class="rdesc">{desc}</p>
        {m}
      </a>'''

# ---------------------------------------------------------------- pages ----
def build_home():
    N = SITE['name']
    all_rows = pub_rows().strip()
    # each <li> block — take the first five
    lis = re.findall(r'<li>.*?</li>', all_rows, flags=re.S)
    recent = '\n'.join(lis[:5])
    # overview stats from the data layer (single source of truth)
    ov = (HOME_OVERVIEW
          .replace('{{PUBS}}', str(len(PUBS)))
          .replace('{{CITES}}', SITE['stats']['citations'])
          .replace('{{HINDEX}}', SITE['stats']['hindex'])
          .replace('{{REPOS}}', str(len(SW))))
    body = '''<header class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">''' + SITE['kicker'] + '''</p>
      <h1>''' + N + '''</h1>
      <p class="org">''' + SITE['org'] + '''</p>
      <p class="tagline">''' + SITE['tagline'] + '''</p>
    </div>
    <img class="portrait" src="avatar.jpg" width="360" height="360" alt="Portrait of ''' + N + '''">
  </div>
</header>
''' + ov + '''

''' + HOME_RESEARCH + '''

  <!-- LATEST PUBLICATIONS preview -->
  <section class="section tint">
    <div class="wrap">
      <h2 class="section-title"><span class="idx">04</span> Recent Publications</h2>
      <p class="section-intro">The five most recent — the full record lives on the
      <a href="publications.html">publications page</a>.</p>
      <ul class="pubs" style="margin-top:28px">
''' + recent + '''
      </ul>
    </div>
  </section>

  <!-- CONTACT -->
  <section id="contact" class="section">
    <div class="wrap">
      <h2 class="section-title"><span class="idx">05</span> Contact</h2>
''' + contact_block() + '''
    </div>
  </section>'''
    return page('home', N + ' — Researcher at AIP',
                N + ' — astrophysics, HPC, and machine learning for science. Researcher at the Leibniz Institute for Astrophysics Potsdam (AIP).',
                body, mail=True)

def build_pubs():
    n = len(PUBS)
    body = '''<div class="pagehead"><div class="wrap">
  <h1>Publications</h1>
  <p class="meta"><span class="n">%d</span> works · %s · %s · <a href="https://orcid.org/0000-0002-8913-0690" target="_blank" rel="noopener">full record on ORCID</a></p>
</div></div>
<section class="section">
  <div class="wrap">
    <ul class="pubs">
%s
    </ul>
  </div>
</section>''' % (n, SITE['stats']['citations'], SITE['stats']['hindex'], pub_rows())
    return page('publications', 'Publications — ' + SITE['name'],
                'Publication record of %s: %d works, %s, %s.' % (SITE['name'], n, SITE['stats']['citations'], SITE['stats']['hindex']),
                body)

def build_projects():
    rows = []
    for p in PROJECTS:
        rows.append(project_row(p))
        if p.get('details'):
            rows.append('\n' + frag(p['details']))
    body = '''<div class="pagehead"><div class="wrap">
  <h1>Projects</h1>
  <p class="meta"><span class="n">%d</span> active research &amp; infrastructure projects</p>
</div></div>
<section class="section">
  <div class="wrap">
    <div class="ledger">
%s
    </div>
  </div>
</section>''' % (len(PROJECTS), '\n'.join(rows))
    return page('projects', 'Projects — ' + SITE['name'],
                'Research projects: ' + ', '.join(p['title'].split(' (')[0] for p in PROJECTS[:5]) + '.',
                body)

def build_bench():
    body = '''<div class="pagehead"><div class="wrap">
  <h1>Benchmarks</h1>
  <p class="meta">S3 object storage · LLM / SQL generation · <a href="https://github.com/arm2arm/dbbench-benchmarks" target="_blank" rel="noopener">dbbench-benchmarks repo</a></p>
</div></div>
''' + BENCH_SECTIONS
    return page('benchmarks', 'Benchmarks — ' + SITE['name'],
                'S3 object-storage and LLM/SQL-generation benchmarks with full result plots (dbbench-benchmarks).',
                body)

def build_gallery():
    figs = GALLERY['figures']
    items = []
    for i, f in enumerate(figs):
        lazy = '' if i == 0 else ' loading="lazy" fetchpriority="low"'
        fetch = ' fetchpriority="high"' if i == 0 else ''
        w = f.get('w', f.get('width', ''))
        h = f.get('h', f.get('height', ''))
        alt = H.escape(f.get('alt', ''), quote=True)
        items.append('''      <figure>
        <img src="%s" width="%s" height="%s" alt="%s"%s%s>
        <figcaption>%s</figcaption>
      </figure>''' % (f['src'], w, h, alt, fetch, lazy, f['caption']))
    # single figure: centered; multiple: auto-flow grid (CSS handles count)
    cls = 'gallery single' if len(figs) == 1 else 'gallery'
    body = '''<div class="pagehead"><div class="wrap">
  <h1>Gallery</h1>
  <p class="meta">%s%s</p>
</div></div>
<section class="section">
  <div class="wrap">
    <div class="%s">
%s
    </div>
  </div>
</section>''' % (GALLERY['head'],
                ('&nbsp;·&nbsp; %d figures' % len(figs)) if len(figs) > 1 else '',
                cls, '\n'.join(items))
    alts = ' · '.join(H.escape(f.get('alt', '')) for f in figs[:3])
    more = (' · +%d more' % (len(figs) - 3)) if len(figs) > 3 else ''
    desc = 'Figure gallery (%d): %s%s' % (len(figs), alts, more)
    return page('gallery', 'Gallery — ' + SITE['name'], desc, body)

def build_software():
    rows = '\n'.join(sw_row(i+1, *s) for i, s in enumerate(SW))
    body = '''<div class="pagehead"><div class="wrap">
  <h1>Software</h1>
  <p class="meta"><span class="n">%d</span> repositories · full list on <a href="https://github.com/arm2arm" target="_blank" rel="noopener">GitHub</a></p>
</div></div>
<section class="section">
  <div class="wrap">
    <div class="ledger">
%s
    </div>
  </div>
</section>''' % (len(SW), rows)
    return page('software', 'Software — ' + SITE['name'],
                'Software and tools: pipelines, viewers, agents, and HPC utilities — %d repositories.' % len(SW),
                body)

def build_404():
    body = '''<div class="pagehead"><div class="wrap">
  <h1>404 — not found</h1>
  <p class="meta">this page does not exist (or moved)</p>
</div></div>
<section class="section">
  <div class="wrap">
    <p class="section-intro" style="font-size:17px">The page you asked for is not part of this site.
    Head back to the <a href="index.html">home page</a>, or browse the full
    <a href="publications.html">publication record</a>, <a href="projects.html">projects</a>,
    and <a href="software.html">software</a>.</p>
  </div>
</section>'''
    return page(None, 'Page not found — ' + SITE['name'], 'This page does not exist.', body, noindex=True)

PAGES = {
    'index.html':        build_home,
    'publications.html': build_pubs,
    'projects.html':     build_projects,
    'benchmarks.html':   build_bench,
    'gallery.html':      build_gallery,
    'software.html':     build_software,
    '404.html':          build_404,
}

# ------------------------------------------------------------ validation --
def validate(name, out):
    """Static checks over one generated page. Returns a list of issues."""
    issues = []
    for tag in ('a','div','ul','li','section','header','footer','main','nav','figure','p','span','table','details'):
        o = len(re.findall(r'<%s[ >]' % tag, out))
        c = len(re.findall(r'</%s>' % tag, out))
        if o != c:
            issues.append('%s tag imbalance: %d open / %d close' % (tag, o, c))
    # missing local targets (href/src that are not external or anchors)
    for attr in ('href', 'src'):
        for ref in re.findall(r'%s="([^"]+)"' % attr, out):
            if ref.startswith(('http://','https://','mailto:','data:','#')):
                continue
            target = ref.split('#')[0]
            if target and not os.path.exists(os.path.join(BASE, target)):
                issues.append('missing local %s: %s' % (attr, ref))
    # unbalanced tags in every inlined fragment surface above; also flag
    # nested anchors (parser force-close hazard)
    for m in re.finditer(r'<a [^>]*>(?:(?!</a>).)*<a ', out, re.S):
        issues.append('nested <a> at offset %d' % m.start())
    return issues

def check_content():
    issues = []
    for f in GALLERY.get('figures', []):
        for k in ('src', 'alt', 'caption'):
            if k not in f:
                issues.append('gallery figure missing key %r: %s' % (k, f.get('src', '?')))
        if 'w' not in f and 'width' not in f:
            issues.append('gallery figure missing w/width (CLS guard): %s' % f.get('src'))
    for s in PUBS:
        if not s.get('title'):
            issues.append('publication entry without title')
    return issues

if __name__ == '__main__':
    problems = []
    if CHECK_ONLY:
        problems += check_content()
    for name, fn in PAGES.items():
        out = fn()
        if not CHECK_ONLY:
            with open(os.path.join(BASE, name), 'w') as f:
                f.write(out)
        issues = validate(name, out)
        problems += ['%s: %s' % (name, i) for i in issues]
        print('  %-18s %d bytes%s%s' % (name, len(out), ' (check only)' if CHECK_ONLY else '',
                                        '  ' + ', '.join(issues) if issues else ''))
    print('generated %d pages' % len(PAGES))
    if CHECK_ONLY:
        if problems:
            print('CHECK FAILED (%d issues):' % len(problems))
            for p in problems:
                print('  - ' + p)
            sys.exit(1)
        print('check passed — no issues')
