-- =============================================================
-- ERP Sales & Supply Chain Analytics
-- Oracle Autonomous Database (OCI)
-- Dataset: DataCo Smart Supply Chain (180K+ transactions)
-- =============================================================


-- -------------------------------------------------------------
-- Q1: Top 10 Product Categories by Total Revenue
-- Tables: Order_Items, Products
-- -------------------------------------------------------------
SELECT
    p.category_name,
    COUNT(DISTINCT oi.order_id)         AS total_orders,
    SUM(oi.quantity)                    AS total_units_sold,
    ROUND(SUM(oi.sales), 2)            AS total_revenue,
    ROUND(AVG(oi.sales), 2)            AS avg_revenue_per_line
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
GROUP BY p.category_name
ORDER BY total_revenue DESC
FETCH FIRST 10 ROWS ONLY;


-- -------------------------------------------------------------
-- Q2: Late Delivery Rate by Shipping Mode
-- Tables: Orders
-- -------------------------------------------------------------
SELECT
    shipping_mode,
    COUNT(*)                                                        AS total_orders,
    SUM(late_delivery_risk)                                         AS late_orders,
    ROUND(SUM(late_delivery_risk) * 100.0 / COUNT(*), 2)           AS late_delivery_pct,
    ROUND(AVG(days_for_shipping_real - days_for_shipment_scheduled), 2) AS avg_delay_days
FROM Orders
GROUP BY shipping_mode
ORDER BY late_delivery_pct DESC;


-- -------------------------------------------------------------
-- Q3: Top 10 Customers by Lifetime Spend
-- Tables: Customers, Orders, Order_Items
-- -------------------------------------------------------------
SELECT
    c.customer_id,
    c.fname || ' ' || c.lname           AS customer_name,
    c.segment,
    c.country,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(oi.sales), 2)            AS lifetime_spend,
    ROUND(AVG(oi.sales), 2)            AS avg_order_value
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN Order_Items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.fname, c.lname, c.segment, c.country
ORDER BY lifetime_spend DESC
FETCH FIRST 10 ROWS ONLY;


-- -------------------------------------------------------------
-- Q4: Monthly Order Volume Trend (2015-2018)
-- Tables: Orders
-- -------------------------------------------------------------
SELECT
    TO_CHAR(order_date, 'YYYY-MM')      AS order_month,
    COUNT(DISTINCT order_id)            AS total_orders,
    ROUND(SUM(
        CASE WHEN late_delivery_risk = 1 THEN 1 ELSE 0 END
    ) * 100.0 / COUNT(*), 2)           AS late_delivery_pct
FROM Orders
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY order_month;


-- -------------------------------------------------------------
-- Q5: Profit & Revenue by Market
-- Tables: Orders, Order_Items
-- -------------------------------------------------------------
SELECT
    o.market,
    COUNT(DISTINCT o.order_id)                                          AS total_orders,
    ROUND(SUM(oi.sales), 2)                                            AS total_revenue,
    ROUND(SUM(oi.benefit_per_order), 2)                                AS total_profit,
    ROUND(SUM(oi.benefit_per_order) * 100.0 / SUM(oi.sales), 2)       AS profit_margin_pct
FROM Orders o
JOIN Order_Items oi ON o.order_id = oi.order_id
GROUP BY o.market
ORDER BY total_profit DESC;


-- -------------------------------------------------------------
-- Q6: Customer Segment Analysis
-- Tables: Customers, Orders, Order_Items
-- -------------------------------------------------------------
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)                                       AS total_customers,
    COUNT(DISTINCT o.order_id)                                          AS total_orders,
    ROUND(SUM(oi.sales), 2)                                            AS total_revenue,
    ROUND(SUM(oi.sales) / COUNT(DISTINCT c.customer_id), 2)            AS revenue_per_customer,
    ROUND(AVG(oi.discount_rate) * 100, 2)                              AS avg_discount_pct
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN Order_Items oi ON o.order_id = oi.order_id
GROUP BY c.segment
ORDER BY total_revenue DESC;


-- -------------------------------------------------------------
-- Q7: Top 10 Best-Selling Products by Quantity
-- Tables: Order_Items, Products
-- -------------------------------------------------------------
SELECT
    p.product_name,
    p.category_name,
    p.department_name,
    SUM(oi.quantity)                        AS total_units_sold,
    ROUND(SUM(oi.sales), 2)                AS total_revenue,
    ROUND(AVG(oi.discount_rate) * 100, 2)  AS avg_discount_pct
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
GROUP BY p.product_name, p.category_name, p.department_name
ORDER BY total_units_sold DESC
FETCH FIRST 10 ROWS ONLY;


-- -------------------------------------------------------------
-- Q8: Order Status Distribution
-- Tables: Orders
-- -------------------------------------------------------------
SELECT
    order_status,
    COUNT(*)                                                AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)     AS pct_of_total
FROM Orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- -------------------------------------------------------------
-- Q9: Delivery Performance by Region
-- Tables: Orders
-- -------------------------------------------------------------
SELECT
    order_region,
    COUNT(*)                                                            AS total_orders,
    ROUND(SUM(late_delivery_risk) * 100.0 / COUNT(*), 2)               AS late_delivery_pct,
    ROUND(AVG(days_for_shipping_real), 2)                              AS avg_actual_days,
    ROUND(AVG(days_for_shipment_scheduled), 2)                         AS avg_scheduled_days,
    ROUND(AVG(days_for_shipping_real - days_for_shipment_scheduled), 2) AS avg_delay_days
FROM Orders
GROUP BY order_region
ORDER BY late_delivery_pct DESC
FETCH FIRST 15 ROWS ONLY;


-- -------------------------------------------------------------
-- Q10: High-Value Orders with Late Delivery Risk
-- Identifies urgent orders needing intervention
-- Tables: Orders, Order_Items, Customers
-- -------------------------------------------------------------
SELECT
    o.order_id,
    c.fname || ' ' || c.lname           AS customer_name,
    c.segment,
    o.order_date,
    o.shipping_mode,
    o.order_region,
    ROUND(SUM(oi.sales), 2)            AS order_value,
    o.days_for_shipping_real,
    o.days_for_shipment_scheduled,
    o.delivery_status
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
JOIN Order_Items oi ON o.order_id = oi.order_id
WHERE o.late_delivery_risk = 1
  AND o.order_status NOT IN ('CANCELED', 'SUSPECTED_FRAUD')
GROUP BY
    o.order_id, c.fname, c.lname, c.segment,
    o.order_date, o.shipping_mode, o.order_region,
    o.days_for_shipping_real, o.days_for_shipment_scheduled,
    o.delivery_status
HAVING ROUND(SUM(oi.sales), 2) > (
    SELECT AVG(total_order_value)
    FROM (
        SELECT order_id, SUM(sales) AS total_order_value
        FROM Order_Items
        GROUP BY order_id
    )
)
ORDER BY order_value DESC
FETCH FIRST 20 ROWS ONLY;
