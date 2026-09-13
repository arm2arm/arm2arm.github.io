# cv-page — how to extend the site

Data-driven static site. **Never hand-edit the `*.html` files** — they are
generated. Edit the data files, run the builder, push.

## The one command

```bash
cd /home/hermes/projects/cv-page
python3 build.py --check          # validates: tags, local hrefs/srcs, nested <a>,
                                  # gallery/pubs keys — exits 1 on any issue
python3 build.py                  # regenerate all 7 pages in the repo root
```

Then deploy (see `DEPLOY.md`): copy into `existing/` and git push.

## Where content lives

| Content                     | File                              | Format            |
|-----------------------------|-----------------------------------|-------------------|
| Identity, nav, contact, hero, **stats** (citations/h-index) | `content/site.json` | JSON |
| Publications (34)           | `content/pubs.json`               | JSON (ORCID works) |
| Gallery figures + page head | `content/gallery.json`            | JSON |
| Projects (incl. deep-dives) | `build.py` → `PROJECTS`           | Python list (raw-HTML values OK) |
| Software repos              | `build.py` → `SW`                 | Python list |
| Benchmark sections          | `content/pages/bench_sections.html` | raw HTML fragment |
| Home prose                  | `content/pages/home_*.html`       | raw HTML (`{{PUBS}}`/`{{CITES}}`/`{{HINDEX}}`/`{{REPOS}}` auto-filled) |
| Project deep-dives          | `content/pages/<id>_deepdive.html`| raw HTML fragment |
| Theme (4 palettes)          | `style.css` variable blocks       | CSS |

**Escaping convention:** free text from JSON (pub titles/years/DOIs, gallery
alt text) is HTML-escaped by the builder. The `PROJECTS`/`SW` lists and the
raw-HTML fragments are the exception — they may contain markup
(`<b>`, `<span>`, `<a>`), and are inlined verbatim.

## Add a gallery figure

1. Drop the image in `img/` (WebP keeps pages light; name it `something.webp`).
2. Add an entry to `content/gallery.json` → `figures`:
   ```json
   { "src": "img/something.webp", "w": 1200, "h": 800,
     "alt": "what the figure shows",
     "caption": "one-line caption — <a href=\"...\">links</a> allowed (caption is raw HTML)" }
   ```
   `w`/`h` are the NATURAL pixel dimensions (the CLS guard) — `width`/`height`
   are accepted too, but `w`/`h` is the convention.
3. Rebuild + deploy. The gallery auto-flows: 1 figure = centered, 2–3 per row
   on desktop as it grows; the first figure is `fetchpriority="high"` (LCP),
   the rest lazy. If the page context (currently SHBoost 2024) no longer fits,
   update the `head` field in `gallery.json` (raw HTML).

## Add a project

Append a dict to `PROJECTS` in `build.py`:

```python
dict(num='08', title='New Project', lang='Python · Dask',
     href='https://example.com',
     desc='One or two sentences — HTML allowed (<b>, <span>, <a>).',
     meta='optional one-line stat line',            # optional
     details='newproject_deepdive.html'),            # optional, see below
```

`num` is the visible index. Keep the list in display order.

### Give a project its own descriptive area (deep-dive)

1. Create `content/pages/newproject_deepdive.html` — a self-contained HTML
   fragment. Copy the structure of `drp_deepdive.html` (a `<details>` panel
   with `<h4>` sections, `.ladder`, `.roles`, `.statline`).
2. **The fragment must have balanced tags** — it is inlined verbatim. Wrap it
   in one outer `<div style="padding:0 8px"> … </div>` like the DRP one.
3. Add `details='newproject_deepdive.html'` to the project dict.
4. Rebuild + deploy. The panel renders as a collapsible `<details>` directly
   under that project's row — no JS involved.

## Add a publication

Append to `content/pubs.json`:

```json
{ "title": "…", "year": "2026", "doi": "10.xxxx/yyy" }
```

`doi` is optional (works without one just don't get a DOI link).
"IN PRESS" years sort to the top. Both the publications page and the
home-page "Recent Publications" (top 5) update automatically; the work count
in the home overview and page meta update too.

## Add a software repo / benchmark section

- Software: append `('Name', 'Lang', 'description — HTML allowed', 'https://…', 'meta or ''')`
  to `SW` in `build.py`.
- Benchmarks: edit `content/pages/bench_sections.html` (raw HTML). Plots:
  1200px-wide WebP q80 in `img/`, with exact `width`/`height` to avoid CLS.

## Adding a whole new page

1. Add a `build_<name>()` function in `build.py` using
   `page(active, title, desc, body, …)` — `active` is the **lowercased nav
   label** from `site.json` (e.g. `"team"`), or `None` for no highlight (404).
   The home page passes `'home'`, which matches the `index.html` href.
2. Add `'<name>.html': build_<name>` to `PAGES`.
3. Add the nav link `["Team", "team.html"]` to `content/site.json` → `nav`.
4. Rebuild + deploy.

## Adding a theme (5th palette)

1. Add one variable block (`[data-accent="x"][data-theme="light|dark"]`,
   9 vars, AA-checked) to `style.css`.
2. Add two entries to `THEME_COLORS` in `build.py` (`chrome` + `fav`) and the
   `x` value to the two `if (a !== …)` guard lines in `THEME_JS_PRE`.
3. Rebuild + deploy.

## Invariants the builder enforces

- Email is only ever in the reversed `data-mail` attribute — never plaintext.
- First gallery figure: no `loading="lazy"`, gets `fetchpriority="high"`.
- All external links: `target="_blank" rel="noopener"`.
- Default theme: `data-theme="dark" data-accent="ocean"` on `<html>` (blue).
- 404 page: no nav highlight + `noindex`.
- `--check` verifies: tag balance (14 tags), every local `href`/`src` exists,
  no nested `<a>`, gallery figures have `src`/`alt`/`caption`/`w`/`h`, every
  publication has a title.
