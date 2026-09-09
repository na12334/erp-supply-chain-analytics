"""
ERP Sales & Supply Chain Analytics
DataCo Smart Supply Chain — descriptive and diagnostic analysis

Run locally:  streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Analytics",
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sales Overview",
    "Delivery Performance",
    "Delivery Root Cause",
    "Profitability",
    "Customers",
])

# ------------------------------------------------------------ sales overview

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

# ------------------------------------------------------- delivery performance

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

# --------------------------------------------------------- delivery root cause

with tab3:
    st.subheader("Why is expedited shipping the worst performer?")
    st.write(
        "First Class shows the highest late rate despite being the premium "
        "option. Two competing explanations: either expedited fulfilment is "
        "genuinely slower, or the promised delivery window is unrealistic. "
        "Comparing scheduled against actual transit time separates the two."
    )

    promise = (
        f.groupby("SHIPPING_MODE")
        .agg(
            SCHEDULED=("DAYS_FOR_SHIPMENT_SCHEDULED", "mean"),
            ACTUAL=("DAYS_FOR_SHIPPING_REAL", "mean"),
            LATE_PCT=("LATE_DELIVERY_RISK", "mean"),
            ORDERS=("ORDER_ID", "nunique"),
        )
        .reset_index()
    )
    promise["GAP"] = promise["ACTUAL"] - promise["SCHEDULED"]
    promise["LATE_PCT"] = promise["LATE_PCT"] * 100
    promise = promise.sort_values("SCHEDULED")

    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        fig.add_bar(
            x=promise["SHIPPING_MODE"],
            y=promise["SCHEDULED"],
            name="Promised",
            text=promise["SCHEDULED"].round(1),
        )
        fig.add_bar(
            x=promise["SHIPPING_MODE"],
            y=promise["ACTUAL"],
            name="Actual",
            text=promise["ACTUAL"].round(1),
        )
        fig.update_layout(
            title="Promised vs Actual Transit Days",
            barmode="group",
            height=430,
            yaxis_title="Days",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            promise,
            x="GAP",
            y="LATE_PCT",
            size="ORDERS",
            color="SHIPPING_MODE",
            text="SHIPPING_MODE",
            title="Promise Gap vs Late Rate",
            labels={"GAP": "Actual minus promised (days)", "LATE_PCT": "Late %"},
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    spread_actual = promise["ACTUAL"].max() - promise["ACTUAL"].min()
    spread_sched = promise["SCHEDULED"].max() - promise["SCHEDULED"].min()

    st.dataframe(
        promise[["SHIPPING_MODE", "SCHEDULED", "ACTUAL", "GAP", "LATE_PCT", "ORDERS"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "SHIPPING_MODE": "Shipping mode",
            "SCHEDULED": st.column_config.NumberColumn("Promised days", format="%.2f"),
            "ACTUAL": st.column_config.NumberColumn("Actual days", format="%.2f"),
            "GAP": st.column_config.NumberColumn("Gap", format="%.2f"),
            "LATE_PCT": st.column_config.NumberColumn("Late %", format="%.1f%%"),
            "ORDERS": "Orders",
        },
    )

    st.info(
        f"Actual transit time varies by {spread_actual:.2f} days across shipping "
        f"modes, while the promised window varies by {spread_sched:.2f} days. "
        "The wider the spread in promises relative to actual performance, the "
        "more the late-delivery metric reflects SLA design rather than "
        "fulfilment capability — meaning the lever is the promise, not the "
        "warehouse."
    )

# ------------------------------------------------------------- profitability

with tab4:
    loss_rows = f[f["BENEFIT_PER_ORDER"] < 0]
    loss_share = len(loss_rows) / len(f) * 100
    loss_value = loss_rows["BENEFIT_PER_ORDER"].sum()

    p1, p2, p3 = st.columns(3)
    p1.metric("Loss-making line items", f"{loss_share:.1f}%")
    p2.metric("Value destroyed", f"${abs(loss_value) / 1e6:.2f}M")
    p3.metric("Avg profit ratio", f"{f['PROFIT_RATIO'].mean():.3f}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        bands = pd.cut(
            f["DISCOUNT_RATE"],
            bins=[-0.01, 0.05, 0.10, 0.15, 0.20, 1.0],
            labels=["0-5%", "5-10%", "10-15%", "15-20%", "20%+"],
        )
        by_disc = (
            f.assign(BAND=bands)
            .groupby("BAND", observed=True)
            .agg(
                MARGIN=("PROFIT_RATIO", "mean"),
                ORDERS=("ORDER_ID", "count"),
            )
            .reset_index()
        )
        fig = px.bar(
            by_disc,
            x="BAND",
            y="MARGIN",
            title="Average Profit Ratio by Discount Band",
            labels={"BAND": "Discount applied", "MARGIN": "Mean profit ratio"},
            text_auto=".3f",
        )
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        by_dept = (
            f.groupby("DEPARTMENT_NAME")
            .agg(
                PROFIT=("BENEFIT_PER_ORDER", "sum"),
                REVENUE=("SALES", "sum"),
            )
            .reset_index()
        )
        by_dept["MARGIN_PCT"] = by_dept["PROFIT"] / by_dept["REVENUE"] * 100
        by_dept = by_dept.sort_values("MARGIN_PCT")
        fig = px.bar(
            by_dept,
            x="MARGIN_PCT",
            y="DEPARTMENT_NAME",
            orientation="h",
            title="Net Margin % by Department",
            labels={"MARGIN_PCT": "Margin %", "DEPARTMENT_NAME": ""},
            text_auto=".1f",
        )
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Products Destroying the Most Value")

    worst = (
        f.groupby(["CATEGORY_NAME", "PRODUCT_NAME"])
        .agg(
            ORDERS=("ORDER_ID", "nunique"),
            REVENUE=("SALES", "sum"),
            PROFIT=("BENEFIT_PER_ORDER", "sum"),
            AVG_DISCOUNT=("DISCOUNT_RATE", "mean"),
        )
        .reset_index()
        .nsmallest(15, "PROFIT")
    )
    worst["AVG_DISCOUNT"] = (worst["AVG_DISCOUNT"] * 100).round(1)

    st.dataframe(
        worst,
        use_container_width=True,
        hide_index=True,
        column_config={
            "CATEGORY_NAME": "Category",
            "PRODUCT_NAME": "Product",
            "ORDERS": "Orders",
            "REVENUE": st.column_config.NumberColumn("Revenue", format="$%.0f"),
            "PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
            "AVG_DISCOUNT": st.column_config.NumberColumn(
                "Avg discount", format="%.1f%%"
            ),
        },
    )

# ---------------------------------------------------------------- customers

with tab5:
    cust = (
        f.groupby("CUSTOMER_ID")
        .agg(
            REVENUE=("SALES", "sum"),
            ORDERS=("ORDER_ID", "nunique"),
            PROFIT=("BENEFIT_PER_ORDER", "sum"),
        )
        .reset_index()
        .sort_values("REVENUE", ascending=False)
    )
    cust["CUM_REVENUE_PCT"] = cust["REVENUE"].cumsum() / cust["REVENUE"].sum() * 100
    cust["CUST_PCT"] = np.arange(1, len(cust) + 1) / len(cust) * 100

    top_20_share = cust.loc[cust["CUST_PCT"] <= 20, "REVENUE"].sum() / cust["REVENUE"].sum() * 100
    repeat_share = (cust["ORDERS"] > 1).mean() * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Revenue from top 20%", f"{top_20_share:.1f}%")
    m2.metric("Repeat customers", f"{repeat_share:.1f}%")
    m3.metric("Avg orders per customer", f"{cust['ORDERS'].mean():.2f}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        curve = cust.iloc[:: max(1, len(cust) // 300)]
        fig = px.line(
            curve,
            x="CUST_PCT",
            y="CUM_REVENUE_PCT",
            title="Revenue Concentration (Pareto)",
            labels={
                "CUST_PCT": "% of customers",
                "CUM_REVENUE_PCT": "% of cumulative revenue",
            },
        )
        fig.add_shape(
            type="line", x0=0, y0=0, x1=100, y1=100,
            line=dict(dash="dot", width=1),
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        seg = (
            f.groupby("SEGMENT")
            .agg(
                REVENUE=("SALES", "sum"),
                CUSTOMERS=("CUSTOMER_ID", "nunique"),
                PROFIT=("BENEFIT_PER_ORDER", "sum"),
            )
            .reset_index()
        )
        seg["REVENUE_PER_CUSTOMER"] = seg["REVENUE"] / seg["CUSTOMERS"]
        fig = px.bar(
            seg.sort_values("REVENUE_PER_CUSTOMER"),
            x="REVENUE_PER_CUSTOMER",
            y="SEGMENT",
            orientation="h",
            title="Revenue per Customer by Segment",
            labels={"REVENUE_PER_CUSTOMER": "Revenue per customer", "SEGMENT": ""},
            text_auto=".0f",
        )
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 20 Customers by Revenue")

    top_cust = (
        f.groupby(["CUSTOMER_ID", "SEGMENT", "COUNTRY"])
        .agg(
            ORDERS=("ORDER_ID", "nunique"),
            REVENUE=("SALES", "sum"),
            PROFIT=("BENEFIT_PER_ORDER", "sum"),
        )
        .reset_index()
        .nlargest(20, "REVENUE")
    )

    st.dataframe(
        top_cust,
        use_container_width=True,
        hide_index=True,
        column_config={
            "CUSTOMER_ID": "Customer ID",
            "SEGMENT": "Segment",
            "COUNTRY": "Country",
            "ORDERS": "Orders",
            "REVENUE": st.column_config.NumberColumn("Revenue", format="$%.0f"),
            "PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
        },
    )

    st.info(
        f"The top 20% of customers account for {top_20_share:.1f}% of revenue. "
        f"{repeat_share:.1f}% of customers ordered more than once, at an average "
        f"of {cust['ORDERS'].mean():.2f} orders each — concentration and repeat "
        "behaviour together set the ceiling on retention-led growth."
    )
