import sqlite3

def get_all_products():
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    c.execute('SELECT code, name, stock FROM products')
    products = c.fetchall()
    conn.close()
    return products  # tuple (code, name, stock)

def init_db():
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    

    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    products_list = [
        ('A1', 'Product A1', 10),
        ('A2', 'Product A2', 10),
        ('A3', 'Product A3', 10),
        ('B1', 'Product B1', 10),
        ('B2', 'Product B2', 10),
        ('B3', 'Product B3', 10),
    ]

    for code, name, stock in products_list:
    # update stock
        c.execute('''
            INSERT INTO products (code, name, stock)
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET stock=excluded.stock
        ''', (code, name, stock))
    conn.commit()
    conn.close()
