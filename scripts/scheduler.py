import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from datetime import datetime
import json
import os, sys 
from monitoring import monitor_pipeline




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)   
from alerts import send_alert

LOG_FILE = os.path.join(BASE_DIR, "logs", "scheduler.log")
HEALTH_FILE = os.path.join(BASE_DIR, "logs", "pipeline_health.json")
MAX_LOG_SIZE = 1_000_000  # 1 MB
BACKUP_COUNT = 5          # keep last 5 log files

# Setup rotating logs
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)

scheduler = BlockingScheduler()

def update_health(status: str, message: str):
    """Write current pipeline health to JSON file."""
    health = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message
    }
    with open(HEALTH_FILE, "w") as f:
        json.dump(health, f, indent=2)
    logging.info(f"Health updated: {health}")

def run_pipeline():
    logging.info("==== Automated ETL Run Started ====")
    start_time = datetime.now()   # <<< you forgot this

    steps = [
        "scripts/generate_fake_sales.py",
        "scripts/extract_sales.py",
        "scripts/transform_sales.py",
        "scripts/load_to_db.py"
    ]

    try:
        for step in steps:
            logging.info(f"Running: {step}")
            subprocess.run(["python", step], check=True)

        # ---- RUN MONITORING AFTER SUCCESS ----
        duration = (datetime.now() - start_time).total_seconds()
        monitor_pipeline(duration)
        # ---------------------------------------

        update_health("OK", "Pipeline completed successfully.")
        logging.info("==== Automated ETL Run Completed ====")

    except subprocess.CalledProcessError as e:
        logging.error(f"Pipeline step failed: {e}")
        update_health("FAIL", f"Pipeline failed at {step}")
        try:
            send_alert(
                subject="Retail Sales Pipeline Failure 🚨",
                message=f"Step failed: {step}\nError: {e}\nCheck logs/scheduler.log for details."
            )
        except Exception as alert_exc:
            logging.error(f"Failed to send alert: {alert_exc}")
        raise




# Schedule once per 24 hours
scheduler.add_job(run_pipeline, "interval", hours=24, id="daily_etl_job")

if __name__ == "__main__":
    logging.info(f"Scheduler started at {datetime.now()}")
    print("Scheduler running with rotating logs. Press CTRL+C to stop.")
    try:
        run_pipeline()  # immediate first run
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped manually.")
