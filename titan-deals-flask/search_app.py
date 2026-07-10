"""
search_app.py — reference wiring for templates/index.html

This shows the exact context variables index.html expects. Merge this
into your existing search_app.py rather than replacing it if you've
already got FTS5 query logic in place — the important part is the
variable names passed to render_template().
"""

import sqlite3
import time
from flask import Flask, request, render_template, g

DB_PATH = "deals.db"
PAGE_SIZE = 24

app = Flask(__name__)

STORES = ["Walmart", "Target", "Lowe's", "Costco", "Home Depot", "Best Buy"]
CATEGORIES = ["Power Tools", "LEGO", "Patio", "TVs", "Kitchen", "Furniture", "Electronics", "Camping"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    db = get_db()

    query = request.args.get("q", "").strip()
    store = request.args.get("store", "")
    category = request.args.get("category", "")
    min_discount = request.args.get("min_discount", type=int)
    page = request.args.get("page", 1, type=int)

    where = []
    params = []

    start = time.perf_counter()

    if query:
        # FTS5 prefix match first
        cur = db.execute(
            "SELECT rowid FROM deals_fts WHERE deals_fts MATCH ? ORDER BY rank LIMIT 500",
            (query + "*",),
        )
        rowids = [r["rowid"] for r in cur.fetchall()]
        if rowids:
            where.append(f"deals.id IN ({','.join('?' * len(rowids))})")
            params.extend(rowids)
        else:
            # LIKE fallback for partial / non-tokenized matches
            where.append("(deals.title LIKE ? OR deals.store LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

    if store:
        where.append("deals.store = ?")
        params.append(store)
    if category:
        where.append("deals.category = ?")
        params.append(category)
    if min_discount:
        where.append("deals.discount >= ?")
        params.append(min_discount)

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    offset = (page - 1) * PAGE_SIZE
    rows = db.execute(
        f"""
        SELECT id, store, title, msrp, price, discount, city, state,
               category, updated_minutes_ago
        FROM deals
        {where_clause}
        ORDER BY updated_minutes_ago ASC
        LIMIT ? OFFSET ?
        """,
        (*params, PAGE_SIZE + 1, offset),
    ).fetchall()

    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    has_more = len(rows) > PAGE_SIZE
    deals = [dict(r) for r in rows[:PAGE_SIZE]]

    total = db.execute("SELECT COUNT(*) AS c FROM deals").fetchone()["c"]
    avg_discount = db.execute("SELECT AVG(discount) AS a FROM deals").fetchone()["a"] or 0

    stats = {
        "deals_indexed": f"{total:,}",
        "latency_ms": latency_ms,
        "avg_discount": round(avg_discount),
    }

    return render_template(
        "index.html",
        query=query,
        stores=STORES,
        categories=CATEGORIES,
        selected_store=store,
        selected_category=category,
        min_discount=min_discount,
        deals=deals,
        stats=stats,
        has_more=has_more,
        next_page=page + 1,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
