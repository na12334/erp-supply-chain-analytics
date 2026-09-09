-- ============================================================
-- DROP OLD SCHEMA (run this first to clear out the sample-data tables)
-- ============================================================
DROP TABLE Order_Items PURGE;
DROP TABLE Purchase_Orders PURGE;
DROP TABLE Orders PURGE;
DROP TABLE Inventory PURGE;
DROP TABLE Products PURGE;
DROP TABLE Customers PURGE;
DROP TABLE Suppliers PURGE;

-- ============================================================
-- NEW SCHEMA — matched to the real DataCo Supply Chain dataset
-- ============================================================

-- ========================================
-- 1. CUSTOMERS
-- ========================================
CREATE TABLE Customers (
    customer_id     NUMBER PRIMARY KEY,
    fname           VARCHAR2(50),
    lname           VARCHAR2(50),
    segment         VARCHAR2(30),
    city            VARCHAR2(50),
    state           VARCHAR2(50),
    country         VARCHAR2(50),
    zipcode         VARCHAR2(20)
);

-- ========================================
-- 2. PRODUCTS
-- ========================================
CREATE TABLE Products (
    product_id          NUMBER PRIMARY KEY,
    product_name        VARCHAR2(200),
    category_id         NUMBER,
    category_name       VARCHAR2(100),
    department_id       NUMBER,
    department_name     VARCHAR2(100),
    price               NUMBER(10,2)
);

-- ========================================
-- 3. ORDERS
-- ========================================
CREATE TABLE Orders (
    order_id                        NUMBER PRIMARY KEY,
    customer_id                     NUMBER NOT NULL,
    order_date                      DATE,
    shipping_date                   DATE,
    order_status                    VARCHAR2(30),
    delivery_status                 VARCHAR2(30),
    late_delivery_risk              NUMBER(1),
    shipping_mode                   VARCHAR2(30),
    days_for_shipping_real          NUMBER(4),
    days_for_shipment_scheduled     NUMBER(4),
    market                          VARCHAR2(30),
    order_region                    VARCHAR2(50),
    order_country                   VARCHAR2(80),
    order_state                     VARCHAR2(80),
    order_city                      VARCHAR2(80),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- ========================================
-- 4. ORDER_ITEMS
-- ========================================
CREATE TABLE Order_Items (
    order_item_id       NUMBER PRIMARY KEY,
    order_id            NUMBER NOT NULL,
    product_id          NUMBER NOT NULL,
    quantity             NUMBER(6),
    product_price        NUMBER(10,2),
    discount             NUMBER(10,2),
    discount_rate        NUMBER(5,4),
    sales                NUMBER(12,2),
    profit_ratio         NUMBER(6,4),
    order_item_total     NUMBER(12,2),
    benefit_per_order    NUMBER(12,2),
    CONSTRAINT fk_orderitems_order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    CONSTRAINT fk_orderitems_product
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
