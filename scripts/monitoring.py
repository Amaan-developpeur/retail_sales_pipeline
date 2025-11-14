import os
import json
import logging
import sqlite3
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pandas as pd
from alerts import send_alert

# --------------------------
# PROJECT ROOT PATHS
# --------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "retail_sales.db")
LOG_FILE = os.path.join(BASE_DIR, "logs", "monitoring.log")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema_config.json")
MONITOR_TABLE = "monitoring_log"

# --------------------------
# Logging
# --------------------------
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)
logger = logging.getLogger("monitoring")

# --------------------------
# Import alert function (optional)
# --------------------------
try:
    from scripts.alerts import send_alert
except Exception:
    # fallback: define noop if alerts unavailable
    def send_alert(subject, message):
        logger.warning("Alert requested but send_alert not available: %s | %s", subject, message)


# --------------------------
# Thresholds (tweakable)
# --------------------------
ROW_DROP_PCT_THRESHOLD = 0.5   # 50% drop considered critical
REVENUE_CHANGE_PCT_THRESHOLD = 0.3  # 30% revenue change considered critical
MISSING_COLS_CRITICAL = True


# --------------------------
# Helpers
# --------------------------
def _get_conn():
    return sqlite3.connect(DB_PATH)


def _ensure_monitor_table():
    q = f"""
    CREATE TABLE IF NOT EXISTS {MONITOR_TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        duration_secs REAL,
        transactional_rows INTEGER,
        aggregated_rows INTEGER,
        total_revenue REAL,
        notes TEXT
    );
    """
    conn = _get_conn()
    conn.execute(q)
    conn.commit()
    conn.close()


def _last_monitor_row():
    conn = _get_conn()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {MONITOR_TABLE} ORDER BY id DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception:
        conn.close()
        return None


# --------------------------
# Core monitor function
# --------------------------
def monitor_pipeline(duration: float):
    """
    Run a set of monitoring checks after a successful pipeline run.
    duration: total pipeline runtime in seconds
    """
    logger.info("Starting monitoring checks (duration: %.2fs)", duration)
    _ensure_monitor_table()

    conn = _get_conn()
    try:
        # Read transactional and aggregated counts
        try:
            trans_df = pd.read_sql_query("SELECT COUNT(*) AS cnt FROM sales_transactional", conn)
            agg_df = pd.read_sql_query("SELECT COUNT(*) AS cnt FROM sales_aggregated", conn)
            trans_count = int(trans_df["cnt"].iloc[0])
            agg_count = int(agg_df["cnt"].iloc[0])
        except Exception as e:
            logger.error("Failed to read table counts: %s", e)
            send_alert("Monitoring failure: DB read error", f"Could not read processed tables: {e}")
            return

        # Basic KPI: total revenue from aggregated
        try:
            rev_df = pd.read_sql_query("SELECT SUM(revenue) AS total_revenue FROM sales_aggregated", conn)
            total_revenue = float(rev_df["total_revenue"].iloc[0] or 0.0)
        except Exception as e:
            logger.error("Failed to compute total revenue: %s", e)
            total_revenue = 0.0

        # Schema check vs schema_config.json (transactional)
        schema_warnings = []
        try:
            with open(SCHEMA_FILE, "r") as f:
                schema = json.load(f).get("sales", {})
                expected_cols = set(schema.get("columns", {}).keys())
            tcols_df = pd.read_sql_query("PRAGMA table_info(sales_transactional);", conn)
            actual_cols = set(tcols_df["name"].tolist())
            missing = expected_cols - actual_cols
            extra = actual_cols - expected_cols
            if missing:
                msg = f"Missing required columns in sales_transactional: {sorted(list(missing))}"
                logger.warning(msg)
                schema_warnings.append(msg)
            if extra:
                msg = f"Extra columns in sales_transactional: {sorted(list(extra))}"
                logger.info(msg)
                schema_warnings.append(msg)
        except Exception as e:
            logger.error("Schema check failed: %s", e)
            schema_warnings.append(f"Schema check error: {e}")

        # Compare with last monitoring result
        last = _last_monitor_row()
        anomalies = []
        if last is not None:
            try:
                prev_trans = int(last.get("transactional_rows") or 0)
                prev_rev = float(last.get("total_revenue") or 0.0)

                # Row drop detection
                if prev_trans > 0:
                    drop_pct = (prev_trans - trans_count) / prev_trans
                    if drop_pct >= ROW_DROP_PCT_THRESHOLD:
                        anomalies.append(f"Transactional rows dropped by {drop_pct:.2%} (prev={prev_trans} current={trans_count})")

                # Revenue spike/drop detection (relative change)
                if prev_rev > 0:
                    rev_change = abs(total_revenue - prev_rev) / prev_rev
                    if rev_change >= REVENUE_CHANGE_PCT_THRESHOLD:
                        anomalies.append(f"Revenue changed by {rev_change:.2%} (prev={prev_rev:.2f} current={total_revenue:.2f})")
            except Exception as e:
                logger.error("Failed to compare with previous monitoring row: %s", e)

        # Schema critical
        if MISSING_COLS_CRITICAL and any("Missing required columns" in s for s in schema_warnings):
            anomalies.append("CRITICAL: Missing required columns detected.")

        # Persist monitoring record
        notes = "; ".join(schema_warnings + anomalies) or "OK"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_q = f"""
            INSERT INTO {MONITOR_TABLE} (ts, duration_secs, transactional_rows, aggregated_rows, total_revenue, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        conn.execute(insert_q, (ts, duration, trans_count, agg_count, total_revenue, notes))
        conn.commit()

        logger.info("Monitoring recorded: trans=%d agg=%d revenue=%.2f notes=%s", trans_count, agg_count, total_revenue, notes)

        # If anomalies detected, send alert
        if anomalies:
            subject = "Retail Pipeline Monitoring Alert ❗"
            message = (
                f"Timestamp: {ts}\n"
                f"Duration: {duration:.2f}s\n"
                f"Transactional rows: {trans_count}\n"
                f"Aggregated rows: {agg_count}\n"
                f"Total revenue: {total_revenue:.2f}\n\n"
                f"Issues:\n- " + "\n- ".join(anomalies + schema_warnings)
            )
            # Non-blocking send with error handling already inside send_alert
            send_alert(subject, message)

    except Exception as final_e:
        logger.exception("Unexpected error during monitoring: %s", final_e)
        send_alert("Monitoring internal error", f"Monitoring crashed: {final_e}")
    finally:
        conn.close()
