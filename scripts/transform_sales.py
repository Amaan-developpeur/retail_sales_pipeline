import os
import pandas as pd
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INGESTED_DIR = os.path.join(BASE_DIR, "data", "ingested")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PRODUCT_CATALOG = os.path.join(BASE_DIR, "data", "product_catalog.csv")
LOG_FILE = os.path.join(BASE_DIR, "logs", "transform_sales.log")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_latest_ingested():
    files = sorted(
        [f for f in os.listdir(INGESTED_DIR) if f.endswith(".csv")],
        key=lambda x: os.path.getmtime(os.path.join(INGESTED_DIR, x)),
        reverse=True
    )
    if not files:
        raise FileNotFoundError("No ingested files found.")
    latest = files[0]
    logging.info(f"Loaded latest ingested file: {latest}")
    return pd.read_csv(os.path.join(INGESTED_DIR, latest))

def transform_sales():
    start = datetime.now()

    sales_df = load_latest_ingested()
    product_df = pd.read_csv(PRODUCT_CATALOG)

    # Merge with product catalog
    merged = pd.merge(sales_df, product_df, on="product_id", how="left")

    # Clean and compute KPIs
    merged["date"] = pd.to_datetime(merged["date"])
    merged["total_cost"] = merged["cost"] * merged["quantity"]
    merged["profit"] = merged["revenue"] - merged["total_cost"]
    merged["margin_percent"] = ((merged["profit"] / merged["revenue"]) * 100).round(2)

    # Transactional output
    transactional_path = os.path.join(PROCESSED_DIR, "sales_transactional.csv")
    merged.to_csv(transactional_path, index=False)
    logging.info(f"Transactional dataset saved: {transactional_path} ({len(merged)} rows)")

    # Aggregated table (daily × region × product)
    aggregated = (
        merged.groupby(["date", "region", "product_id"], as_index=False)
        .agg({
            "revenue": "sum",
            "total_cost": "sum",
            "profit": "sum",
            "margin_percent": "mean",
            "quantity": "sum"
        })
    )
    aggregated["margin_percent"] = aggregated["margin_percent"].round(2)

    aggregated_path = os.path.join(PROCESSED_DIR, "sales_aggregated.csv")
    aggregated.to_csv(aggregated_path, index=False)
    logging.info(f"Aggregated dataset saved: {aggregated_path} ({len(aggregated)} rows)")

    duration = (datetime.now() - start).total_seconds()
    logging.info(f"Transformation completed in {duration:.2f}s")

if __name__ == "__main__":
    logging.info("==== Transformation Run Started ====")
    transform_sales()
    logging.info("==== Transformation Run Completed ====")
