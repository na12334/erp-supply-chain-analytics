"""
ERP Sales & Supply Chain Analytics
DataCo Smart Supply Chain — revenue, profitability and delivery reliability

Run locally:  streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Performance",
    page_icon="📦",
    layout="wide",
)


@st.cache_data
def load_data():
    """Load the four normalized tables and join them into one analysis frame."""
    orders = pd.read_csv("orders_clean.csv")
    order_items = pd.read_csv("order_items_clean.csv")
    products = pd.read_csv("products_clean.csv")
    customers = pd.read_csv("customers_clean.csv")

    for table in (orders, order_items, products, customers):
        table.columns = table.columns.str.strip().str.upper()

    orders["ORDER_DATE"] = pd.to_datetime(orders["ORDER_DATE"], errors="coerce")

    merged = (
        order_items
        .merge(orders, on="ORDER_ID", how="left")
        .merge(products, on="PRODUCT_ID", how="left")
        .merge(customers, on="CUSTOMER_ID", how="left")
    )
    return merged


try:
    df = load_data()
except FileNotFoundError as err:
    st.error(f"Could not load the data files: {err}")
    st.stop()

st.sidebar.header("Filters")

markets = sorted(df["MARKET"].dropna().unique())
selected_markets = st.sidebar.multiselect("Market", markets, default=markets)

modes = sorted(df["SHIPPING_MODE"].dropna().unique())
selected_modes = st.sidebar.multiselect("Shipping mode", modes, default=modes)

min_date = df["ORDER_DATE"].min()
max_date = df["ORDER_DATE"].max()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

mask = df["MARKET"].isin(selected_markets) & df["SHIPPING_MODE"].isin(selected_modes)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1])
    mask = mask & df["ORDER_DATE"].between(start, end)

f = df[mask]

if f.empty:
    st.warning("No records match the current filters.")
    st.stop()

revenue = f["SALES"].sum()
total_orders = f["ORDER_ID"].nunique()
total_customers = f["CUSTOMER_ID"].nunique()
profit = f["BENEFIT_PER_ORDER"].sum()
late_pct = f["LATE_DELIVERY_RISK"].mean() * 100
actual_days = f["DAYS_FOR_SHIPPING_REAL"].mean()
sched_days = f["DAYS_FOR_SHIPMENT_SCHEDULED"].mean()
gap = actual_days - sched_days

st.title("ERP Sales & Supply Chain Analytics")
st.caption("DataCo Smart Supply Chain — 180,519 transactions across 5 global markets")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${revenue / 1e6:.2f}M")
k2.metric("Total Orders", f"{total_orders / 1e3:.0f}K")
k3.metric("Total Profit", f"${profit / 1e6:.2f}M")
k4.metric("Total Customers", f"{total_customers / 1e3:.0f}K")
k5.metric("Late Delivery %", f"{late_pct:.1f}%")

st.divider()

tab1, tab2 = st.tabs(["Sales Overview", "Delivery Performance"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        top_cats = (
            f.groupby("CATEGORY_NAME")["SALES"]
            .sum()
            .nlargest(10)
            .reset_index()
            .sort_values("SALES")
        )
        fig = px.bar(
            top_cats,
            x="SALES",
            y="CATEGORY_NAME",
            orientation="h",
            title="Top 10 Categories by Revenue",
            labels={"SALES": "Revenue", "CATEGORY_NAME": ""},
        )
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        monthly = (
            f.dropna(subset=["ORDER_DATE"])
            .set_index("ORDER_DATE")
            .resample("ME")["ORDER_ID"]
            .nunique()
            .reset_index(name="ORDERS")
        )
        fig = px.line(
            monthly,
            x="ORDER_DATE",
            y="ORDERS",
            title="Orders Over Time",
            labels={"ORDER_DATE": "", "ORDERS": "Orders"},
            markers=True,
        )
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        by_mode = (
            f.groupby("SHIPPING_MODE")["LATE_DELIVERY_RISK"]
            .mean()
            .mul(100)
            .reset_index(name="LATE_PCT")
            .sort_values("LATE_PCT", ascending=False)
        )
        fig = px.bar(
            by_mode,
            x="SHIPPING_MODE",
            y="LATE_PCT",
            title="Late Delivery % by Shipping Mode",
            labels={"SHIPPING_MODE": "", "LATE_PCT": "Late %"},
            text_auto=".1f",
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        by_market = f.groupby("MARKET")["BENEFIT_PER_ORDER"].sum().reset_index()
        fig = px.pie(
            by_market,
            names="MARKET",
            values="BENEFIT_PER_ORDER",
            title="Profit by Market",
            hole=0.45,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Avg Scheduled Days", f"{sched_days:.2f}")
    d2.metric("Avg Actual Days", f"{actual_days:.2f}")
    d3.metric("Shipping Delay Gap", f"{gap:.2f}")
    d4.metric("Late Delivery %", f"{late_pct:.1f}%")

    st.divider()

    c1, c2 = st.columns([1, 2])

    with c1:
        status = (
            f.groupby("DELIVERY_STATUS")["ORDER_ID"]
            .nunique()
            .reset_index(name="ORDERS")
            .sort_values("ORDERS", ascending=False)
        )
        fig = px.bar(
            status,
            x="DELIVERY_STATUS",
            y="ORDERS",
            title="Orders by Delivery Status",
            labels={"DELIVERY_STATUS": "", "ORDERS": "Orders"},
            text_auto=".2s",
        )
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        scatter = (
            f.groupby("CATEGORY_NAME")
            .agg(
                PROFIT=("BENEFIT_PER_ORDER", "sum"),
                ORDERS=("ORDER_ID", "nunique"),
                LATE_PCT=("LATE_DELIVERY_RISK", "mean"),
            )
            .reset_index()
        )
        scatter["LATE_PCT"] = scatter["LATE_PCT"] * 100
        fig = px.scatter(
            scatter,
            x="PROFIT",
            y="LATE_PCT",
            size="ORDERS",
            color="CATEGORY_NAME",
            hover_name="CATEGORY_NAME",
            title="Profit vs Delivery Risk by Category",
            labels={"PROFIT": "Total Profit", "LATE_PCT": "Late Delivery %"},
        )
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product-Level Delivery Detail")

    detail = (
        f.groupby(["CATEGORY_NAME", "PRODUCT_NAME"])
        .agg(
            ORDERS=("ORDER_ID", "nunique"),
            LATE_PCT=("LATE_DELIVERY_RISK", "mean"),
            PROFIT=("BENEFIT_PER_ORDER", "sum"),
        )
        .reset_index()
    )
    detail["LATE_PCT"] = (detail["LATE_PCT"] * 100).round(1)
    detail["PROFIT"] = detail["PROFIT"].round(2)
    detail = detail.sort_values("LATE_PCT", ascending=False)

    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True,
        column_config={
            "CATEGORY_NAME": "Category",
            "PRODUCT_NAME": "Product",
            "ORDERS": "Orders",
            "LATE_PCT": st.column_config.NumberColumn("Late %", format="%.1f%%"),
            "PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
        },
    )

    st.info(
        f"Late delivery holds near {late_pct:.0f}% across categories, markets and "
        f"price points, while orders ship {gap:.2f} days behind schedule on "
        "average — the issue is systemic rather than category-specific."
    )
