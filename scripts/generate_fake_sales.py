import os
import random
import pandas as pd
import logging
from faker import Faker
from datetime import datetime

fake = Faker()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
LOG_FILE = os.path.join(BASE_DIR, "logs", "generate_fake_sales.log")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = [f"P{str(i).zfill(3)}" for i in range(1, 21)]  # 20 fake SKUs

def generate_sales_data(n_rows: int = 500):
    """Generate n synthetic, schema-compliant sales records."""
    rows = []
    for _ in range(n_rows):
        product_id = random.choice(PRODUCTS)
        region = random.choice(REGIONS)
        quantity = random.randint(1, 10)
        cost = round(random.uniform(50, 200), 2)
        margin = random.uniform(1.1, 1.5)
        revenue = round(cost * quantity * margin, 2)
        rows.append({
            "date": fake.date_between(start_date="-7d", end_date="today"),
            "region": region,
            "product_id": product_id,
            "revenue": revenue,
            "cost": cost,
            "quantity": quantity
        })
    return pd.DataFrame(rows)

def main():
    start_time = datetime.now()
    filename = f"sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(RAW_DIR, filename)

    df = generate_sales_data()
    df.to_csv(path, index=False)

    duration = (datetime.now() - start_time).total_seconds()
    logging.info(f"Generated {len(df)} records -> {path} in {duration:.2f}s")
    print(f"Generated {len(df)} records -> {path}")

if __name__ == "__main__":
    main()
