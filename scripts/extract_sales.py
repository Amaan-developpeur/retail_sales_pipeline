import os
import json
import pandas as pd
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
INGESTED_DIR = os.path.join(BASE_DIR, "data", "ingested")
LOG_FILE = os.path.join(BASE_DIR, "logs", "extract_sales.log")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema_config.json")

os.makedirs(INGESTED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_schema():
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)["sales"]

def validate_schema(df, schema):
    cols = df.columns.tolist()
    required = schema["required"]

    missing = [col for col in required if col not in cols]
    extra = [col for col in cols if col not in schema["columns"]]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if extra:
        logging.warning(f"Extra columns detected: {extra}")

    # Type conversion
    for col, dtype in schema["columns"].items():
        if col in df.columns:
            try:
                if "datetime" in dtype:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                elif dtype == "float64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
                elif dtype == "int64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                else:
                    df[col] = df[col].astype("string")
            except Exception as e:
                logging.warning(f"Type conversion issue for '{col}': {e}")

    return df

def ingest_sales_files():
    schema = load_schema()

    for file in os.listdir(RAW_DIR):
        if not file.endswith(".csv"):
            continue
        src = os.path.join(RAW_DIR, file)
        dst = os.path.join(INGESTED_DIR, file)

        if os.path.exists(dst):
            logging.info(f"Skipped already ingested file: {file}")
            continue

        try:
            df = pd.read_csv(src)
            df = validate_schema(df, schema)
            df.to_csv(dst, index=False)
            logging.info(f"Ingested: {file} ({len(df)} rows)")
        except Exception as e:
            logging.error(f"Error processing {file}: {e}")

if __name__ == "__main__":
    logging.info("==== Ingestion Run Started ====")
    ingest_sales_files()
    logging.info("==== Ingestion Run Completed ====")
