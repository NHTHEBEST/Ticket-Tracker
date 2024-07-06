DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;


CREATE TABLE customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  phone TEXT,
  authkey TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_no INTEGER,
  cutomer_id INTEGER,
  contents TEXT,
  order_stat TEXT,
  due_date DATE,
  expected_date DATE,
  price INTEGER,
  paid INTEGER,
  done INTEGER DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (cutomer_id) REFERENCES customers
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  password TEXT,
  perm INTEGER,
  authkey TEXT,
  key_exp TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- create admin api user admin:notsosecure
INSERT INTO users (username, password, perm) VALUES ('admin', 'pbkdf2:sha256:600000$d2bp01YZqaJNNkaG$0bcb7faa74e6255adcffe3df9af68764493a90facda54daf5fdcb046fa2a3260', 0); 

-- create testing customer

INSERT INTO customers (name) VALUES ('CASHSALE');
