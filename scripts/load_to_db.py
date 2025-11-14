import os
import sqlite3
import pandas as pd
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "retail_sales.db")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
LOG_FILE = os.path.join(BASE_DIR, "logs", "load_to_db.log")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_csv_to_sqlite(csv_path, table_name, conn):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    logging.info(f"Loaded {len(df)} rows into table '{table_name}'")

def create_indexes(conn):
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_txn_date ON sales_transactional(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_txn_region ON sales_transactional(region);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_aggr_date ON sales_aggregated(date);")
    conn.commit()
    logging.info("Indexes created successfully")

def main():
    start = datetime.now()
    conn = sqlite3.connect(DB_PATH)

    txn_path = os.path.join(PROCESSED_DIR, "sales_transactional.csv")
    aggr_path = os.path.join(PROCESSED_DIR, "sales_aggregated.csv")

    load_csv_to_sqlite(txn_path, "sales_transactional", conn)
    load_csv_to_sqlite(aggr_path, "sales_aggregated", conn)
    create_indexes(conn)

    conn.close()
    duration = (datetime.now() - start).total_seconds()
    logging.info(f"Database load completed in {duration:.2f}s → {DB_PATH}")
    print(f"Loaded data into {DB_PATH}")

if __name__ == "__main__":
    logging.info("==== DB Load Run Started ====")
    main()
    logging.info("==== DB Load Run Completed ====")
