# Olist E-Commerce Ingestion Pipeline

An incremental data pipeline (ELT) that extracts e-commerce data from flat files, applies time-based filtering, and loads it into Google BigQuery for downstream transformations with dbt.

## Tech Stack

![Python](https://shields.io)
![Pandas](https://shields.io)
![Google BigQuery](https://shields.io)
![dbt](https://shields.io)

---

### ◈ Approach & Core Concept
The pipeline uses an **Append-Only / Incremental Ingestion** pattern instead of full-refresh loads. Data is filtered by a configurable date window during the extraction phase and appended to BigQuery. This keeps historical records intact in the raw layer, offloading all heavy transformations and analytical modeling to dbt.

---

### ◈ Engineering Decisions & Implementation Details

* **Memory Optimization (`yield` generators)**: To prevent Out-Of-Memory (OOM) issues on larger CSVs, data is streamed and loaded into BigQuery in configurable chunks (`chunk_size`). This keeps RAM usage flat and stable.
* **Config-Driven Architecture**: Table metadata (file paths, target names, date columns) and pipeline parameters are fully separated into `config.yaml`. The Python script parses this file into strongly-typed **Dataclasses**. Onboarding a new dataset requires zero code changes.
* **Dynamic Table Partitioning**: The `BigQueryConnector` checks table metadata on the fly. Transactional data (like `orders`) is automatically provisioned with daily time-partitioning in BigQuery to minimize future query costs, while static lookups are loaded normally.
* **Fail-Fast Credential Check**: Upon initialization, the pipeline immediately runs a lightweight API call (`list_datasets`). If GCP service account keys are expired or invalid, the execution stops before processing any source files.
* **Separated Logs and Alerts**: Technical tracking and stack traces are captured locally via `loguru`. High-level milestones (Pipeline Success / Critical Failures) are sent asynchronously to a Discord channel for operational alerting.

---

### 📁 Project Structure
```
my_project/
├── dbt_project/          # dbt models, macros, and schema tests
├── src/                  # Python source code
│   ├── connectors/│   
│   └── bq.py             # BigQueryConnector (Authentication & batch ingestion)
│   ├── pipelines/
│   │   └── olist.py      # Pipeline execution and date-filtering logic
│   ├── utils/
│   │   ├── alerts.py     # Discord notifications
│   │   └── logger.py     # Loguru configuration
│   └── main.py           # Entry point and config parsing
├── config.yaml           # Metadata catalog for all 9 Olist tables
├── .env.example          # Environment variables template
└── README.md
```
---


---

### ⚙ How to Run

#### 1. Environment Variables
Create a local `.env` file based on `.env.example`:
```env
GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/gcp-key.json
DISCORD_WEBHOOK_URL=https://discord.com...
```

#### 2. Execution
```bash
pip install -r requirements.txt
python -m src.main
```

---

## ◈ Next Steps (dbt Analytics Layer)
Once the raw layer (`olist_raw`) is populated, the dbt project takes over to:
* Cleanse, cast, and deduplicate incremental batches (Staging layer).
* Structure data into Star/Snowflake schemas (Marts layer) for analytical reporting.