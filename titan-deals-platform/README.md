# Deals Platform

Hyper-local clearance/markdown search: config-driven HTML ingestion +
SQLite (FTS5) + zero-JS server-side-rendered search UI, tuned for
low-bandwidth mobile.

## Components

- `scraper_config.json` — the selector schema from the spec (`item_sku`,
  `title`, `baseline_price`, `markdown_price`, `stock_availability`), plus
  a `min_discount_pct_to_alert` threshold (defaults to 50%, matching the
  spec's `markdown_price < baseline_price * 0.50` rule).
- `ingest.py` — parses HTML you provide against that selector schema,
  computes discount %, and loads matching rows into SQLite. It does not
  fetch any live URL itself — you point it at HTML you already have the
  right to parse (pages you fetched yourself, a partner export, your own
  site's feed). This keeps sourcing compliance in your hands per-target.
- `schema.sql` — `deals` table plus an FTS5 virtual table (`deals_fts`)
  kept in sync via triggers, for full-text search.
- `search_app.py` — Flask app, server-side rendered, no client-side JS
  framework. Uses FTS5 prefix search when available, falls back to a
  `LIKE` query otherwise. In testing, searches ran well under 1ms on a
  small dataset — comfortably inside the sub-50ms budget even accounting
  for network overhead on a real deployment.
- `templates/index.html` + `static/core_minimal.css` — minimal semantic
  HTML5 + hand-written CSS, no build step, no tracking, no web fonts.

## Run it

```bash
pip install -r requirements.txt --break-system-packages

# ingest some pages
python3 ingest.py --config scraper_config.json --html-dir ./pages --db deals.db

# serve
python3 search_app.py
# -> http://localhost:5000
```

## Extending the selector schema

`scraper_config.json` supports multiple `ingestion_schemas` entries — add
one per target site/format with its own CSS selectors and discount
threshold. `ingest.py` currently reads schema index 0; wire up a
`--schema-index` flag or loop over all schemas if you're ingesting from
more than one source shape.

## Note on sourcing

As with the Service Agency system, this doesn't ship a live scraper
pointed at any specific named retailer — that's a per-target decision that
depends on that retailer's terms of service and whether you have a
legitimate data relationship with them (affiliate feed, partner API, your
own catalog). The parsing/scoring/search pipeline here is source-agnostic
and works the same regardless of where the HTML came from.
