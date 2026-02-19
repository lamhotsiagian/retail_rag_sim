DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  full_name TEXT,
  email TEXT
);

CREATE TABLE orders (
  order_id TEXT PRIMARY KEY,
  customer_id INTEGER,
  status TEXT,
  purchase_date TEXT,
  pickup_store_id TEXT,
  tax_cents INTEGER,
  shipping_cents INTEGER,
  total_cents INTEGER,
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT,
  sku TEXT,
  product_name TEXT,
  quantity INTEGER,
  unit_price_cents INTEGER,
  FOREIGN KEY(order_id) REFERENCES orders(order_id)
);

INSERT INTO customers(customer_id, full_name, email) VALUES
(1, 'Jordan Rivera', 'jordan.rivera@example.com'),
(2, 'Avery Chen', 'avery.chen@example.com');

INSERT INTO orders(order_id, customer_id, status, purchase_date, pickup_store_id, tax_cents, shipping_cents, total_cents) VALUES
('R-10001', 1, 'READY_FOR_PICKUP', '2026-02-10', 'ST-CHI-01', 875, 0, 35874),
('R-10002', 2, 'DELIVERED', '2026-02-01', NULL, 1250, 499, 51448);

INSERT INTO order_items(order_id, sku, product_name, quantity, unit_price_cents) VALUES
('R-10001', 'SKU-HEADPHONES-01', 'Noise-Canceling Headphones', 1, 34999),
('R-10002', 'SKU-LAPTOP-13', '13-inch Laptop', 1, 47999);
