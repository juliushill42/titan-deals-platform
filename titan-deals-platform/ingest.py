#!/usr/bin/env python3
"""
ingest.py

Generic, config-driven HTML ingestion for the Deals platform. Reads a
selector schema (scraper_config.json) and applies it to HTML pages you
provide (already-downloaded pages you have the rights to parse — e.g.
pages you fetched yourself in a browser, an export a retailer partner
gave you, or your own site's clearance feed). This script does not fetch
any live third-party URL on its own; you supply the HTML, which keeps
the ingestion logic decoupled from any specific target and puts sourcing
compliance in your hands (respect robots.txt / ToS for whatever you point
it at).

Usage:
    python3 ingest.py --config scraper_config.json --html page1.html page2.html --db deals.db
    python3 ingest.py --config scraper_config.json --html-dir ./pages --db deals.db
"""
import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

from bs4 import BeautifulSoup

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def parse_price(text: str):
    if not text:
        return None
    cleaned = re.sub(r"[^0-9.]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_items(html: str, schema: dict, source_url: str = None):
    soup = BeautifulSoup(html, "html.parser")
    sel = schema["selectors"]
    stock_attr = schema.get("stock_attr", "data-stock")
    min_discount = schema.get("min_discount_pct_to_alert", 0.0)

    # Each "product card" is assumed to be a repeating container; we look
    # for the SKU selector as the anchor and walk up to a common ancestor
    # if present, otherwise treat the whole document as a single item.
    sku_nodes = soup.select(sel["item_sku"])
    if not sku_nodes:
        return []

    results = []
    for sku_node in sku_nodes:
        card = sku_node
        # walk up a couple levels to find a container with the other fields too
        for _ in range(3):
            if card.parent is None:
                break
            card = card.parent
            if card.select_one(sel["title"]) and card.select_one(sel["markdown_price"]):
                break

        title_node = card.select_one(sel["title"])
        baseline_node = card.select_one(sel["baseline_price"])
        markdown_node = card.select_one(sel["markdown_price"])
        stock_node = card.select_one(sel["stock_availability"])

        if not (title_node and markdown_node):
            continue

        baseline_price = parse_price(baseline_node.get_text()) if baseline_node else None
        markdown_price = parse_price(markdown_node.get_text())
        stock = stock_node.get(stock_attr) if stock_node else None

        if markdown_price is None:
            continue
        if baseline_price is None or baseline_price <= 0:
            discount_pct = 0.0
        else:
            discount_pct = round((1 - (markdown_price / baseline_price)) * 100, 2)

        item = {
            "item_sku": sku_node.get_text(strip=True),
            "title": title_node.get_text(strip=True),
            "domain_scope": schema["domain_scope"],
            "baseline_price": baseline_price or markdown_price,
            "markdown_price": markdown_price,
            "discount_pct": discount_pct,
            "stock_availability": stock,
            "source_url": source_url,
            "alert": discount_pct >= min_discount,
        }
        results.append(item)

    return results


def load_config(path: str):
    with open(path) as f:
        cfg = json.load(f)
    return cfg["scraper_target_manifest"]["ingestion_schemas"][0]


def ensure_db(db_path: str):
    conn = sqlite3.connect(db_path)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    return conn


def ingest_files(conn, schema, html_paths):
    inserted, alerts = 0, 0
    for path in html_paths:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        items = extract_items(html, schema, source_url=path)
        for item in items:
            conn.execute(
                """INSERT INTO deals
                   (item_sku, title, domain_scope, baseline_price, markdown_price,
                    discount_pct, stock_availability, source_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item["item_sku"], item["title"], item["domain_scope"],
                    item["baseline_price"], item["markdown_price"], item["discount_pct"],
                    item["stock_availability"], item["source_url"],
                ),
            )
            inserted += 1
            if item["alert"]:
                alerts += 1
                print(f"ALERT: {item['title']} at {item['discount_pct']}% off (${item['markdown_price']})")
    conn.commit()
    return inserted, alerts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--html", nargs="*", default=[])
    ap.add_argument("--html-dir", default=None)
    ap.add_argument("--db", default="deals.db")
    args = ap.parse_args()

    schema = load_config(args.config)
    conn = ensure_db(args.db)

    html_paths = list(args.html)
    if args.html_dir:
        html_paths.extend(glob.glob(os.path.join(args.html_dir, "*.html")))

    if not html_paths:
        print("No HTML input provided. Use --html file1.html [file2.html ...] or --html-dir DIR", file=sys.stderr)
        sys.exit(1)

    inserted, alerts = ingest_files(conn, schema, html_paths)
    print(f"Ingested {inserted} items ({alerts} above alert threshold) into {args.db}")


if __name__ == "__main__":
    main()
