#!/usr/bin/env python3
"""
search_app.py
Zero-JS server-side-rendered search interface for the Deals platform.
Uses SQLite FTS5 when available, falling back to a LIKE query, to keep
execution comfortably under 50ms on typical result sets.
"""
import sqlite3
import time
from pathlib import Path

from flask import Flask, request, render_template, g

DB_PATH = Path(__file__).parent / "deals.db"

app = Flask(__name__, static_folder="static", template_folder="templates")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def fts_available(conn) -> bool:
    try:
        conn.execute("SELECT 1 FROM deals_fts LIMIT 1")
        return True
    except sqlite3.OperationalError:
        return False


def run_search(conn, query: str, limit: int = 50):
    if not query:
        return []

    if fts_available(conn):
        # FTS5 prefix search on each token
        tokens = [t.strip() for t in query.split() if t.strip()]
        fts_query = " ".join(f"{t}*" for t in tokens) if tokens else query
        try:
            rows = conn.execute(
                """SELECT d.* FROM deals d
                   JOIN deals_fts f ON d.id = f.rowid
                   WHERE deals_fts MATCH ?
                   ORDER BY d.discount_pct DESC
                   LIMIT ?""",
                (fts_query, limit),
            ).fetchall()
            return rows
        except sqlite3.OperationalError:
            pass  # fall through to LIKE

    like_term = f"%{query}%"
    rows = conn.execute(
        """SELECT * FROM deals
           WHERE title LIKE ? OR item_sku LIKE ?
           ORDER BY discount_pct DESC
           LIMIT ?""",
        (like_term, like_term, limit),
    ).fetchall()
    return rows


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    conn = get_db()

    start = time.perf_counter()
    if query:
        results = run_search(conn, query)
    else:
        results = []
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return render_template(
        "index.html",
        query=query,
        results=[dict(r) for r in results],
        elapsed_ms=elapsed_ms,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
