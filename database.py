import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("warehouse.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            location TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            priority TEXT NOT NULL CHECK(priority IN ('EXPRESS','STANDARD','LOW')),
            priority_rank INTEGER NOT NULL,
            delivery_note TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sku) REFERENCES products(sku)
        );
        CREATE INDEX IF NOT EXISTS idx_orders_queue
        ON orders(status, priority_rank, created_at);
        """)

def add_product(sku, name, quantity, location):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO products(sku,name,quantity,location) VALUES(?,?,?,?)
        ON CONFLICT(sku) DO UPDATE SET name=excluded.name,
        quantity=excluded.quantity, location=excluded.location
        """, (sku, name, quantity, location))

def list_products():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM products ORDER BY sku")]

def update_stock(sku, delta):
    with get_conn() as conn:
        row = conn.execute("SELECT quantity FROM products WHERE sku=?", (sku,)).fetchone()
        if row is None:
            raise ValueError("Product not found.")
        new_qty = row["quantity"] + delta
        if new_qty < 0:
            raise ValueError("Stock cannot become negative.")
        conn.execute("UPDATE products SET quantity=? WHERE sku=?", (new_qty, sku))

def add_order(sku, product_name, quantity, priority, delivery_note=""):
    ranks = {"EXPRESS": 0, "STANDARD": 1, "LOW": 2}
    with get_conn() as conn:
        cur = conn.execute("""
        INSERT INTO orders(sku,product_name,quantity,priority,priority_rank,delivery_note)
        VALUES(?,?,?,?,?,?)
        """, (sku, product_name, quantity, priority, ranks[priority], delivery_note))
        return cur.lastrowid

def list_orders():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("""
        SELECT * FROM orders ORDER BY priority_rank, created_at, id
        """)]

def update_order_status(order_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))

def seed_demo_data(force=False):
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0 or force:
            if force:
                conn.execute("DELETE FROM orders")
                conn.execute("DELETE FROM products")
            sample_products = [
                ("SKU-1001", "Heavy Duty Shipping Cartons", 145, "A1"),
                ("SKU-1002", "Industrial Pallet Stretch Film", 88, "A2"),
                ("SKU-1003", "Air-Bubble Cushioning Roll 100m", 52, "A3"),
                ("SKU-1004", "Barcode Thermal Transfer Labels", 220, "B1"),
                ("SKU-1005", "Reinforced Filament Tape 50mm", 7, "B2"),
                ("SKU-1006", "Handheld Android Barcode Scanner", 12, "B3"),
                ("SKU-1007", "Steel Pallet Strapping Tensioner", 4, "C1"),
                ("SKU-1008", "Electronic Platform Scale 300kg", 9, "C2"),
                ("SKU-1009", "Ergonomic Heavy Tape Dispenser", 36, "C3"),
                ("SKU-1010", "Safety Auto-Retract Box Cutters", 18, "A1"),
                ("SKU-1011", "Anti-Static Cushion Pouches (100pk)", 8, "A2"),
                ("SKU-1012", "Poly Mailers 10x13 Self-Seal (500pk)", 180, "B1"),
                ("SKU-1013", "Molded Pallet Corner Protectors", 6, "C2"),
                ("SKU-1014", "High-Grip Nitrile Work Gloves (L)", 75, "B2"),
                ("SKU-1015", "Self-Adhesive Packing List Envelopes", 195, "A3"),
            ]
            for sku, name, qty, loc in sample_products:
                conn.execute("""
                INSERT INTO products(sku,name,quantity,location) VALUES(?,?,?,?)
                ON CONFLICT(sku) DO UPDATE SET name=excluded.name,
                quantity=excluded.quantity, location=excluded.location
                """, (sku, name, qty, loc))

            sample_orders = [
                ("SKU-1004", "Barcode Thermal Transfer Labels", 10, "EXPRESS", "Urgent production line replenishment", "PENDING"),
                ("SKU-1001", "Heavy Duty Shipping Cartons", 25, "EXPRESS", "Priority dispatch dock 4", "PENDING"),
                ("SKU-1005", "Reinforced Filament Tape 50mm", 4, "STANDARD", "Restock packing station B", "PENDING"),
                ("SKU-1009", "Ergonomic Heavy Tape Dispenser", 2, "LOW", "Routine floor equipment refill", "PENDING"),
                ("SKU-1002", "Industrial Pallet Stretch Film", 12, "STANDARD", "Outbound pallet wrapping", "PICKED"),
                ("SKU-1014", "High-Grip Nitrile Work Gloves (L)", 8, "LOW", "Staff safety renewal", "PICKED"),
                ("SKU-1012", "Poly Mailers 10x13 Self-Seal (500pk)", 40, "EXPRESS", "E-commerce rush order #884", "PICKED"),
                ("SKU-1006", "Handheld Android Barcode Scanner", 2, "EXPRESS", "Expedited handheld replacement", "PICKED"),
            ]
            ranks = {"EXPRESS": 0, "STANDARD": 1, "LOW": 2}
            for sku, name, qty, priority, note, status in sample_orders:
                conn.execute("""
                INSERT INTO orders(sku,product_name,quantity,priority,priority_rank,delivery_note,status)
                VALUES(?,?,?,?,?,?,?)
                """, (sku, name, qty, priority, ranks[priority], note, status))
