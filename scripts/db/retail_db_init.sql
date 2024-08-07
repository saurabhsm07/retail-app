CREATE DATABASE retail_db;

--Connect to database
\connect retail_db;


--create use for hive connections
CREATE USER retail_user PASSWORD 'retail_pwd';

CREATE SEQUENCE unique_id_seq;

CREATE TABLE products(
id SERIAL PRIMARY KEY,
transaction_id VARCHAR(255) DEFAULT 'TRXCN-' || nextval('unique_id_seq') || '-' || TO_CHAR(current_timestamp, 'DDMMYYHH24MISS'),
sku VARCHAR(250) UNIQUE NOT NULL,
version INTEGER DEFAULT 0
);

CREATE TABLE batches(
id SERIAL PRIMARY KEY,
reference VARCHAR(255),
sku VARCHAR(250) REFERENCES PRODUCTS(SKU),
quantity INTEGER NOT NULL,
eta DATE
);

CREATE TABLE order_lines(
id SERIAL PRIMARY KEY,
sku VARCHAR(250) REFERENCES PRODUCTS(SKU),
quantity INTEGER NOT NULL,
order_id VARCHAR(250) NOT NULL
);

--CREATE TABLE allocations(
--id SERIAL PRIMARY KEY,
--order_line_id INTEGER REFERENCES ORDER_LINES(ID),
--batch_id INTEGER REFERENCES BATCHES(ID)
--);

GRANT USAGE, CREATE ON SCHEMA public TO retail_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO retail_user;

--GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to hive_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to retail_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to retail_user;