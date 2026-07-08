CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_sku TEXT NOT NULL,
    title TEXT NOT NULL,
    domain_scope TEXT NOT NULL,
    baseline_price REAL NOT NULL,
    markdown_price REAL NOT NULL,
    discount_pct REAL NOT NULL,
    stock_availability TEXT,
    source_url TEXT,
    ingested_at INTEGER DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_deals_title ON deals(title);
CREATE INDEX IF NOT EXISTS idx_deals_domain ON deals(domain_scope);
CREATE INDEX IF NOT EXISTS idx_deals_discount ON deals(discount_pct);

CREATE VIRTUAL TABLE IF NOT EXISTS deals_fts USING fts5(
    title, item_sku, content='deals', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS deals_ai AFTER INSERT ON deals BEGIN
    INSERT INTO deals_fts(rowid, title, item_sku) VALUES (new.id, new.title, new.item_sku);
END;

CREATE TRIGGER IF NOT EXISTS deals_ad AFTER DELETE ON deals BEGIN
    INSERT INTO deals_fts(deals_fts, rowid, title, item_sku) VALUES ('delete', old.id, old.title, old.item_sku);
END;

CREATE TRIGGER IF NOT EXISTS deals_au AFTER UPDATE ON deals BEGIN
    INSERT INTO deals_fts(deals_fts, rowid, title, item_sku) VALUES ('delete', old.id, old.title, old.item_sku);
    INSERT INTO deals_fts(rowid, title, item_sku) VALUES (new.id, new.title, new.item_sku);
END;
