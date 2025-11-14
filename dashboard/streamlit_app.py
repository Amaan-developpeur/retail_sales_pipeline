import sqlite3
import pandas as pd
import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "retail_sales.db")

@st.cache_data
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("Retail Sales Analytics Dashboard")
st.caption("Local-first data engineering pipeline — powered by SQLite & Streamlit")

# --- KPIs ---
st.subheader("Overall Performance")
kpi_df = load_data("""
    SELECT 
        ROUND(SUM(revenue),2) AS total_revenue,
        ROUND(SUM(profit),2) AS total_profit,
        ROUND(AVG(margin_percent),2) AS avg_margin
    FROM sales_aggregated;
""")
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${kpi_df['total_revenue'][0]:,.2f}")
col2.metric("Total Profit", f"${kpi_df['total_profit'][0]:,.2f}")
col3.metric("Avg Margin %", f"{kpi_df['avg_margin'][0]:.2f}%")

# --- Regional Breakdown ---
st.subheader("Revenue by Region")
region_df = load_data("""
    SELECT region, SUM(revenue) AS revenue, SUM(profit) AS profit, AVG(margin_percent) AS margin
    FROM sales_aggregated
    GROUP BY region
    ORDER BY revenue DESC;
""")
st.bar_chart(region_df.set_index("region")[["revenue", "profit"]])

# --- Top Products ---
st.subheader("Top 10 Products by Revenue")
product_df = load_data("""
    SELECT product_id, SUM(revenue) AS revenue, SUM(profit) AS profit, AVG(margin_percent) AS margin
    FROM sales_aggregated
    GROUP BY product_id
    ORDER BY revenue DESC
    LIMIT 10;
""")
st.dataframe(product_df)

# --- Daily Trend ---
st.subheader("Daily Revenue Trend")
trend_df = load_data("""
    SELECT date, SUM(revenue) AS revenue
    FROM sales_aggregated
    GROUP BY date
    ORDER BY date;
""")
st.line_chart(trend_df.set_index("date"))

# --- Rolling Weekly Average (Last 10 Days) ---
st.subheader("Rolling 7-Day Average — Revenue Trend")

trend_df = load_data("""
    SELECT date, SUM(revenue) AS revenue
    FROM sales_aggregated
    GROUP BY date
    ORDER BY date;
""")

# Ensure date is datetime and sorted
trend_df["date"] = pd.to_datetime(trend_df["date"])
trend_df = trend_df.sort_values("date")

# Compute 7-day rolling average
trend_df["rolling_avg_revenue"] = trend_df["revenue"].rolling(window=7, min_periods=1).mean()

# Limit to last 10 days for clarity
recent_trend = trend_df.tail(10)

st.line_chart(
    recent_trend.set_index("date")[["revenue", "rolling_avg_revenue"]],
    height=350
)
st.caption("Show actual vs 7-day rolling average of daily revenue (last 10 days)")


# --- Business Summary Insights ---
st.subheader("Business Summary Insights")

# Compute revenue growth % (last day vs previous day)
if len(trend_df) >= 2:
    revenue_growth = ((trend_df["revenue"].iloc[-1] - trend_df["revenue"].iloc[-2]) / trend_df["revenue"].iloc[-2]) * 100
else:
    revenue_growth = 0

# Compute top region contribution %
total_revenue = region_df["revenue"].sum()
top_region = region_df.iloc[0]["region"]
top_region_share = (region_df.iloc[0]["revenue"] / total_revenue) * 100 if total_revenue > 0 else 0

# Compute low-margin product share
low_margin_threshold = 15  # below 15% margin = low profitability
product_df["low_margin_flag"] = product_df["margin"] < low_margin_threshold
low_margin_share = (product_df["low_margin_flag"].sum() / len(product_df)) * 100 if len(product_df) > 0 else 0

# --- Generate insights summary ---
summary = []

if revenue_growth > 0:
    summary.append(f"Revenue increased by **{revenue_growth:.1f}%** since the previous day.")
else:
    summary.append(f"Revenue dropped by **{abs(revenue_growth):.1f}%**, investigate key regions.")

if top_region_share > 50:
    summary.append(f"Region **{top_region}** contributes **{top_region_share:.1f}%** of total revenue — high dependency risk.")
else:
    summary.append("Healthy regional revenue distribution observed.")

if low_margin_share > 40:
    summary.append(f"{low_margin_share:.1f}% of SKUs have low profitability (<{low_margin_threshold}%). Consider pricing review.")
else:
    summary.append(f"Only {low_margin_share:.1f}% of products have low margins. Profitability mix looks stable.")

# Display insights
for line in summary:
    st.markdown(f"- {line}")


