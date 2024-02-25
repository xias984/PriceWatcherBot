CREATE TABLE IF NOT EXISTS "users" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idtelegram TEXT NOT NULL, 
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS "products" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    price REAL NOT NULL,
    url TEXT,
    asin TEXT,
    category TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "variation_price" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idprodotto INTEGER, 
    oldprice REAL NOT NULL, 
    newprice REAL NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (idprodotto) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS "product_user" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);