| **Project Title** | **Retail Sales Analytics & Monitoring Pipeline** |
|-----------------------|--------------------------------------------------|
| *An end-to-end local data engineering system — automated, observable, and built for business decision intelligence.* |

## Project Overview  

The **Retail Sales Analytics & Monitoring Pipeline** is a fully automated, **local-first data engineering system** designed to simulate how modern retail companies process, monitor, and visualize daily sales performance.

It ingests synthetic retail transactions, validates schemas, transforms raw data into KPI-rich insights, and exposes them via both **API** and **interactive Streamlit dashboard** — all powered by **SQLite** and **Python**.

The goal is to showcase **real-world data engineering principles**:  
automation, idempotent ETL, observability, and business-aligned analytics — without relying on cloud or paid services.

---

### Highlights
- Built to **mimic real enterprise pipelines**, end-to-end.  
- Uses **automated scheduling (APScheduler)** for daily ETL execution.  
- Provides **real-time health monitoring** and **Slack failure alerts**.  
- Empowers decision-makers with **live dashboards** and **actionable insights**.  
- 100% **local, lightweight, and production-structured** — runs anywhere.

## 💼 Business Impact  

| 🧩 **Business Challenge** | 🚀 **Implemented Solution** | 💡 **Impact / Outcome** |
|----------------------------|-----------------------------|--------------------------|
| Sales data scattered across CSVs, inconsistent formats | Automated ingestion with schema validation | Centralized, reliable single source of truth |
| Manual daily reporting caused delays | End-to-end ETL pipeline with scheduler automation | Zero manual intervention — data updates daily |
| No visibility into real-time performance | Interactive Streamlit dashboard with KPIs and charts | Instant insight into revenue, profit, and trends |
| Undetected schema drift and data errors | Automated monitoring with Slack alerts | Early detection of anomalies before they break reporting |
| No long-term performance trend analysis | Rolling 7-day analytics integrated into dashboard | Consistent visibility into business momentum |
| Poor scalability of ad-hoc scripts | Modular, idempotent pipeline architecture | Extensible and production-like for enterprise scale |

---
## System Architecture  

Below is the complete architecture of the **Retail Sales Analytics & Monitoring Pipeline**, designed to emulate a real-world, production-ready data engineering ecosystem.

```text
                          ┌──────────────────────────────────────────┐
                          │   Retail Sales Analytics Pipeline (ETL)  │
                          └──────────────────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │  [M2] Data Generator (Faker - Synthetic CSVs) │
                   └──────────────────────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │  [M3] Ingestion Layer (Schema Validation)    │
                   └──────────────────────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │  [M4] Transformation Layer (KPI Computation) │
                   └──────────────────────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │  [M5] Load Layer (SQLite Warehouse)          │
                   └──────────────────────────────────────────────┘
                                           │
               ┌───────────────────────────┴──────────────────────────┐
               ▼                                                      ▼
   ┌───────────────────────────────┐                   ┌──────────────────────────────┐
   │ [M6] FastAPI Service          │                   │ [M6] Streamlit Dashboard     │
   │ → `/kpi/revenue`, `/health`   │                   │ → KPIs, Trends, Summary      │
   └───────────────────────────────┘                   └──────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │ [M7] Scheduler (APScheduler Automation)      │
                   └──────────────────────────────────────────────┘
                                           │
                                           ▼
                   ┌──────────────────────────────────────────────┐
                   │ [M8] Monitoring & Slack Alerts               │
                   │  → Schema Drift | KPI Anomalies | Health     │
                   └──────────────────────────────────────────────┘

## Project Structure  

The project follows a **clean, modular directory layout** — designed for clarity, maintainability, and real-world scalability.

```text
retail_sales_pipeline/
│
│   .gitignore                 ← ignored files & logs
│   requirements.txt           ← dependency list
│   run_all.py                 ← optional master runner
│   schema_config.json         ← schema definitions for ingestion
│
├───dashboard/                 ← Streamlit visualization layer
│       streamlit_app.py
│
├───data/                      ← All data lifecycle stages
│   │   product_catalog.csv    ← reference dataset
│   │
│   ├───raw/                   ← newly generated daily CSVs
│   ├───ingested/              ← validated and logged files
│   ├───processed/             ← transformed outputs (transactional + aggregated)
│   └───exchange_rates/        ← unused (kept for optional extensions)
│
├───db/                        ← local analytical database
│       retail_sales.db
│
├───images/                    ← screenshots for README
│       dashboard_kpis.png
│       dashboard_region_chart.png
│       dashboard_summary.png
│       dashboard_top_products.png
│       monitoring_log.png
│       revenue_trends.png
│       scheduler_run.png
│
├───logs/                      ← pipeline & system logs
│       extract_sales.log
│       generate_fake_sales.log
│       load_to_db.log
│       monitoring.log
│       pipeline_health.json
│       scheduler.log
│       transform_sales.log
│
├───scripts/                   ← modular ETL and utility scripts
│       alerts.py              ← Slack notification system
│       api_server.py          ← FastAPI endpoints
│       extract_sales.py       ← schema validation + ingestion
│       generate_fake_sales.py ← synthetic data generator
│       load_to_db.py          ← database loading layer
│       monitoring.py          ← drift & anomaly tracking
│       scheduler.py           ← APScheduler automation
│       transform_sales.py     ← KPI enrichment and aggregation
│
└───tests/                     ← placeholder for test scripts

## Core Features  

| Feature | Description |
|----------|--------------|
| **Automated ETL Pipeline** | End-to-end ingestion → transform → load using APScheduler |
| **Schema Validation** | Detects missing or extra columns before ingestion |
| **Data Transformation** | Cleans, enriches, and computes key retail KPIs |
| **SQLite Data Warehouse** | Centralized analytical store for all processed data |
| **FastAPI Service** | Exposes KPIs via REST endpoints (`/kpi/revenue`, `/health`) |
| **Streamlit Dashboard** | Interactive BI interface for KPIs, trends, and insights |
| **Monitoring & Alerts** | Detects schema drift, anomalies, and posts Slack alerts |
| **Rolling 7-Day Analytics** | Replaces forecasting with a lightweight moving average trend |
| **Business Insight Layer** | Auto-generated narrative explaining revenue and margin shifts |

## Key Business KPIs  

| KPI | Purpose |
|-----|----------|
| **Total Revenue** | Overall sales performance metric |
| **Total Profit** | Net profitability from all transactions |
| **Average Margin %** | Efficiency of pricing and cost management |
| **Revenue Growth %** | Daily business momentum indicator |
| **Top Region Contribution %** | Identifies dependency or concentration risk |
| **Low-Margin Product Share %** | Tracks proportion of low-profit SKUs |
| **Rolling 7-Day Average Revenue** | Smooth trendline showing business stability |
| **Business Summary Insights** | Auto-generated one-line recommendations (e.g., growth, risk, margin issues) to guide immediate decisions |

## Dashboard Overview  

The **Streamlit Dashboard** acts as the visualization and decision interface — turning clean, processed retail data into **real-time business insights**.  
It connects directly to the SQLite data warehouse and updates dynamically after every ETL run.

---

### KPI Overview  
![Dashboard KPIs](images/dashboard_kpis.png)  
Displays key performance metrics: **Total Revenue, Total Profit, and Average Margin %**.  
These top-line figures give instant visibility into business performance.

---

### Revenue by Region  
![Revenue by Region](images/dashboard_region_chart.png)  
Bar chart comparing **revenue and profit** across regions — used to identify strong vs. underperforming markets.

---

### Top Products by Revenue  
![Top Products Table](images/dashboard_top_products.png)  
Shows top-performing SKUs with **revenue, profit, and margin %**, helping the business focus on high-impact products.

---

### Daily Revenue Trend (Rolling Average)  
![Revenue Trends](images/revenue_trends.png)  
Line chart visualizing daily revenue with a **7-day rolling average**, offering a smooth view of sales momentum and performance stability.

---

### Business Summary Insights  
![Business Summary](images/dashboard_summary.png)  
Automatically generated, data-driven **business insights** summarizing the day’s performance —  
e.g., revenue growth, regional dependency risk, and profitability warnings — built to support quick decisions.

---

**All visuals update automatically** after every scheduled ETL run, ensuring the dashboard always reflects the latest business state.

---

###  System Logs & Drift Detection  
![Monitoring Log](images/monitoring_log.png)  
Captures every ETL run — with transactional row counts, revenue totals, and schema status.

---

###  Automated Scheduler Execution  
![Scheduler Run](images/scheduler_run.png)  
Shows the APScheduler in action — running daily ETL jobs and posting Slack alerts on success or failure.

---
## Tech Stack  

| Layer | Tools & Technologies |
|--------|-----------------------|
| **Language** | Python 3.11+ |
| **Data Handling** | Pandas, Faker, NumPy |
| **Database** | SQLite (lightweight local warehouse) |
| **API Layer** | FastAPI + Uvicorn |
| **Dashboard Layer** | Streamlit |
| **Scheduling & Automation** | APScheduler |
| **Monitoring & Alerts** | Slack Webhooks, RotatingFileHandler |
| **Version Control** | Git + GitHub |
| **Environment** | Anaconda / venv (cross-platform) |

## Business Value Summary  

This project demonstrates the **real-world lifecycle of data intelligence** —  
from raw retail transactions to decision-ready insights.

It replaces manual reporting and unmonitored scripts with a **fully automated, observable pipeline** that:

- Generates, ingests, and transforms data autonomously.  
- Monitors every run for schema drift and KPI anomalies.  
- Pushes live business insights through a dashboard.  
- Sends instant Slack alerts on failures or performance shifts.  







