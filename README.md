# Titan Deals Platform

A hyper-local clearance and markdown search engine designed for ultra-low bandwidth mobile environments. Built with a zero-JS server-side-rendered architecture, config-driven HTML ingestion, and an embedded SQLite FTS5 index executing queries in **< 1ms**.

## ⚡ Core Architectural Moats

* **Zero Infrastructure Cost:** Completely eliminates reliance on expensive third-party scraping APIs or cloud-hosted search engines (like Algolia or Elasticsearch). It runs entirely on standard Python and local storage.
* **Legal Decoupling:** The ingestion engine processes local HTML files directly (e.g., partner feeds, offline exports, or local browser caches). Sourcing compliance stays completely in the runner's hands, safeguarding the core software module.
* **Extreme Performance:** Bypasses client-side JavaScript framework bloat. Delivers pure semantic HTML and hand-crafted CSS, running comfortably under a 50ms total network budget.

---

## 🛠️ Components

* `scraper_config.json` — Schema defining target CSS selectors (`item_sku`, `title`, `baseline_price`, `markdown_price`, `stock_availability`) and custom discount thresholds.
* `ingest.py` — Config-driven parser utilizing BeautifulSoup4 to process HTML dumps, compute markdown price metrics, flag deep discounts, and commit them to the database.
* `schema.sql` — Core `deals` table equipped with an FTS5 virtual search table kept instantly in sync using database triggers.
* `search_app.py` — Lightweight Flask application utilizing SQLite FTS5 token prefix match indexing with a fast SQL `LIKE` fallback.
* `templates/index.html` + `static/core_minimal.css` — High-speed, semantic UI with zero tracking scripts, external fonts, or runtime dependencies.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Parse local HTML pages into the local SQLite database
python3 ingest.py --config scraper_config.json --html-dir ./pages --db deals.db

# Start the high-speed local search server
python3 search_app.py
