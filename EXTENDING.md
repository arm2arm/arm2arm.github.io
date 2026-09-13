# cv-page — how to extend the site

Data-driven static site. **Never hand-edit the `*.html` files** — they are
generated. Edit the data files, run the builder, push.

## The one command

```bash
cd /home/hermes/projects/cv-page
python3 build.py          # regenerate all pages
python3 build.py --check  # validate only, write nothing
```

Then deploy (see `DEPLOY.md`): copy into `existing/` and git push.

## Where content lives

| Content              | File                          | Format        |
|----------------------|-------------------------------|---------------|
| Identity, nav, contact, hero | `content/site.json`   | JSON          |
| Publications (34)    | `content/publications.json`   | JSON (ORCID export) |
| Gallery figures      | `content/gallery.json`        | JSON          |
| Projects (incl. deep-dives) | `build.py` → `PROJECTS` | Python list   |
| Software repos       | `build.py` → `SW`             | Python list   |
| Benchmark sections   | `build.py` → `BENCH`          | Python list   |
| Home prose           | `content/pages/home_*.html`   | raw HTML fragment |
| Project deep-dives   | `content/pages/<id>_deepdive.html` | raw HTML fragment |
| Theme (4 palettes)   | `style.css` `:root` blocks    | CSS variables |

## Add a gallery figure

1. Drop the image in `img/` (name it `something.webp` — WebP keeps pages light).
2. Add an entry to `content/gallery.json` → `figures`:
   ```json
   { "src": "img/something.webp", "width": 1200, "height": 800,
     "alt": "what the figure shows", "caption": "one-line caption, with <a href>links</a>" }
   ```
3. Rebuild + deploy. The gallery auto-flows: 1 figure = centered, 2–3 per row
   on desktop as it grows. Meta count updates itself.

## Add a project

Append a dict to `PROJECTS` in `build.py`:

```python
dict(num='08', title='New Project', lang='Python · Dask',
     href='https://example.com',
     desc='One or two sentences — HTML allowed (<b>, <span>, <a>).'),
     # meta='optional one-line stat line',
     # details='newproject_deepdive.html'),   # see below
```

`num` is the visible index (`08`). Keep the list in the order you want shown.

### Give a project its own descriptive area (deep-dive)

1. Create `content/pages/newproject_deepdive.html` — a self-contained HTML
   fragment. Copy the structure of `drp_deepdive.html` (the `<details>` panel
   with `<h4>` sections, `.ladder`, `.roles`, `.statline`).
2. **The fragment must have balanced tags** — it is inlined verbatim. Wrap it
   in one outer `<div style="padding:0 8px"> … </div>` like the DRP one.
3. Add `details='newproject_deepdive.html'` to the project dict.
4. Rebuild + deploy. The panel renders as a collapsible `<details>` directly
   under that project's row — no JS, works with everything else.

## Add a publication

Append to `content/publications.json` (ORCID shape):

```json
{ "title": "…", "year": "2026", "venue": "Journal", "doi": "10.xxxx/yyy" }
```

Both the publications page and the home-page "Recent Publications" (top 5,
year-desc) update automatically.

## Add a software repo / benchmark plot

Same pattern: append to `SW` (repo rows) or `BENCH` (benchmark sections with
`img/*.webp` plots) in `build.py`. Plots: generate 1200px-wide WebP q80.

## Adding a whole new page

1. Add a `build_<name>()` function in `build.py` using `page(active=…, title=…,
   desc=…, body=…)` — `active` is the nav file name (e.g. `"team.html"`).
2. Add `'<name>.html': build_<name>` to `PAGES`.
3. Add the nav link to `content/site.json` → `nav`.
4. Rebuild + deploy.

## Adding a theme (5th palette)

1. Add `data-accent="<name>"` block (8 vars, AA-checked) to `style.css`.
2. Add it to the `chrome`/`fav` maps and the `accent` switch logic in the two
   `<script>` blocks in `head()` / `page()` in `build.py`.
3. Rebuild + deploy.

## Invariants the builder enforces (don't break them)

- Email is only ever in the reversed `data-mail` attribute — never plaintext.
- First gallery figure has no `loading="lazy"` (LCP).
- All external links: `target="_blank" rel="noopener"`.
- Default theme is `data-theme="dark" data-accent="ocean"` on `<html>`.
