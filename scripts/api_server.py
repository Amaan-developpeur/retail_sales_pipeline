from fastapi import FastAPI, HTTPException
import sqlite3
import pandas as pd

DB_PATH = "db/retail_sales.db"
app = FastAPI(title="Retail Sales Analytics API")

def query_db(query, params=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params or [])
        conn.close()
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API and database reachable"}

@app.get("/kpi/revenue")
def get_revenue():
    query = """
        SELECT region,
               ROUND(SUM(revenue),2) AS total_revenue,
               ROUND(SUM(profit),2) AS total_profit,
               ROUND(AVG(margin_percent),2) AS avg_margin
        FROM sales_aggregated
        GROUP BY region
        ORDER BY total_revenue DESC;
    """
    df = query_db(query)
    return df.to_dict(orient="records")

@app.get("/kpi/top-products")
def top_products(limit: int = 5):
    query = """
        SELECT product_id,
               ROUND(SUM(revenue),2) AS total_revenue,
               ROUND(SUM(profit),2) AS total_profit,
               ROUND(AVG(margin_percent),2) AS avg_margin
        FROM sales_aggregated
        GROUP BY product_id
        ORDER BY total_revenue DESC
        LIMIT ?;
    """
    df = query_db(query, [limit])
    return df.to_dict(orient="records")
