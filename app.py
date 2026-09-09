"""
Supply Chain & Delivery Performance Dashboard
DataCo Smart Supply Chain analysis

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

# ---------------------------------------------------------------- data


@st.cache_data
def load_data():
    """Load the four tables and join them into one analysis frame."""
    orders = pd.read_csv("data/orders.csv")
    order_items = pd.read_csv("data/order_items.csv")
    products = pd.read_csv("data/products.csv")
    customers = pd.read_csv("data/customers.csv")

    # normalise column names so the joins below are predictable
    for df in (orders, order_items, products, customers):
        df.columns = df.columns.str.strip().str.upper()

    orders["ORDER_DATE"] = pd.to_datetime(orders["ORDER_DATE"], errors="coerce")

    # same star schema as the Power BI model:
    # ORDER_ITEMS is the fact table, everything else joins onto it
    df = (
        order_items
        .merge(orders, on="ORDER_ID", how="left")
        .merge(products, on="PRODUCT_ID", how="left")
        .merge(customers, on="CUSTOMER_ID", how="left")
    )
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Could not find the CSV files. Put orders.csv, order_items.csv, "
        "products.csv and customers.csv inside a `data/` folder next to app.py."
    )
    st.stop()

# ---------------------------------------------------------------- filters

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
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask &= df["ORDER_DATE"].between(start, end)

f = df[mask]

if f.empty:
    st.warning("No records match the current filters.")
    st.stop()

# ---------------------------------------------------------------- measures


def measures(data):
    """Equivalent of the DAX measures from the Power BI model."""
    return {
        "revenue": data["SALES"].sum(),
        "orders": data["ORDER_ID"].nunique(),
        "customers": data["CUSTOMER_ID"].nunique(),
        "profit": data["BENEFIT_PER_ORDER"].sum(),
        "late_pct": data["LATE_DELIVERY_RISK"].sum() / len(data) * 100,
        "actual_days": data["DAYS_FOR_SHIPPING_REAL"].mean(),
        "sched_days": data["DAYS_FOR_SHIPMENT_SCHEDULED"].mean(),
    }


m = measures(f)
m["gap"] = m["actual_days"] - m["sched_days"]

# ---------------------------------------------------------------- layout

st.title("Supply Chain & Delivery Performance")
st.caption(
    "DataCo Smart Supply Chain — revenue, profitability and delivery reliability"
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${m['revenue'] / 1e6:.2f}M")
k2.metric("Total Orders", f"{m['orders'] / 1e3:.0f}K")
k3.metric("Total Profit", f"${m['profit'] / 1e6:.2f}M")
k4.metric("Total Customers", f"{m['customers'] / 1e3:.0f}K")
k5.metric("Late Delivery %", f"{m['late_pct']:.1f}%")

st.divider()

tab1, tab2 = st.tabs(["Sales Overview", "Delivery Performance"])

# ---------------------------------------------------------------- tab 1

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
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        monthly = (
            f.set_index("ORDER_DATE")
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
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        by_mode = (
            f.groupby("SHIPPING_MODE")
            .apply(
                lambda g: g["LATE_DELIVERY_RISK"].sum() / len(g) * 100,
                include_groups=False,
            )
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
        by_market = (
            f.groupby("MARKET")["BENEFIT_PER_ORDER"].sum().reset_index()
        )
        fig = px.pie(
            by_market,
            names="MARKET",
            values="BENEFIT_PER_ORDER",
            title="Profit by Market",
            hole=0.45,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- tab 2

with tab2:
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Avg Scheduled Days", f"{m['sched_days']:.2f}")
    d2.metric("Avg Actual Days", f"{m['actual_days']:.2f}")
    d3.metric("Shipping Delay Gap", f"{m['gap']:.2f}", delta=f"{m['gap']:.2f} days late")
    d4.metric("Late Delivery %", f"{m['late_pct']:.1f}%")

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
        fig.update_layout(height=420, showlegend=False)
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
        scatter["LATE_PCT"] *= 100
        fig = px.scatter(
            scatter,
            x="PROFIT",
            y="LATE_PCT",
            size="ORDERS",
            color="CATEGORY_NAME",
            title="Profit vs Delivery Risk by Category",
            labels={"PROFIT": "Total Profit", "LATE_PCT": "Late Delivery %"},
            hover_name="CATEGORY_NAME",
        )
        fig.update_layout(height=420, showlegend=False)
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
        f"Late delivery holds near {m['late_pct']:.0f}% across categories, markets "
        f"and price points, while orders ship {m['gap']:.2f} days behind schedule "
        "on average — the issue is systemic rather than category-specific."
    )
