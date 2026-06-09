# ecommerce-analytics-dbt

# Olist E-Commerce ELT Pipeline & Analytics

A robust data ingestion pipeline designed to emulate incremental data collection (Data Ingestion/EL) from flat files of the Brazilian Olist marketplace into a Google BigQuery cloud data warehouse, followed by downstream transformation using dbt.

## 🎯 Architecture & Core Concept
Rather than using a heavy full-refresh approach, this project follows modern **ELT principles** and implements an **Append-Only / Incremental Ingestion** pattern. Data is filtered by a dynamic time window during the extraction phase and appended to the warehouse in batches. This preserves historical records in the raw layer (Data Lake) and offloads all heavy business logic and analytical modeling to **dbt** inside BigQuery.

---

## 🛠️ Tech Stack
* **Language**: Python 3.12+ (leveraging modern type hinting and syntax improvements)
* **Data Processing**: Pandas (stream-like processing via generators)
* **DWH**: Google BigQuery
* **Data Transformation**: dbt (Data Build Tool)
* **Logging & Monitoring**: Loguru, Discord Webhooks (Operational alerting)
* **Configuration**: YAML

---

## 📂 Project Structure
```
my_project/
├── dbt_project/          # dbt transformation models, macros, and schema tests
├── src/                  # Core Python application logic
│   ├── connectors/
│   │   └── bq.py         # BigQueryConnector class (Health check, DataFrame ingestion)
│   ├── pipelines/
│   │   └── olist.py      # Abstract pipeline logic & custom data extractor generator using yield
│   ├── utils/
│   │   ├── alerts.py     # Operational alerts (Success/Failure notifications via Discord)
│   │   └── logger.py     # Loguru advanced logging configuration
│   └── main.py           # Application entry point
├── config.yaml           # Metadata catalog for all 9 Olist tables and time windows
├── .env.example          # Environment variables template for secure credentials
└── README.md             # Project documentation
```

---

## 🚀 Key Engineering Highlights (Under the Hood)

1. **Memory Efficiency via Generators (`yield`)**: 
   To prevent Out-Of-Memory (OOM) errors when dealing with large datasets, raw CSV files are processed using a custom Python generator. Data is streamed and loaded into BigQuery in configurable chunks (`chunksize`), keeping the RAM footprint minimal and constant.
2. **Configuration-Driven Development**: 
   Metadata for all 9 Olist tables (file paths, target BigQuery tables, date-filtering keys) is entirely externalized into `config.yaml`. The Python pipeline is fully decoupled from the schema; onboarding a new dataset requires zero code changes—only a new entry in the YAML config.
3. **Dynamic DWH Optimization (Partitioning)**: 
   The `BigQueryConnector` dynamically inspects the table metadata. Transactional tables (e.g., `orders`) are automatically provisioned with daily time-partitioning on the fly, drastically reducing downstream SQL query costs. Static lookups (e.g., `customers`) are seamlessly loaded into standard tables within the same interface.
4. **Fail-Fast Principle**: 
   Upon initializing the BigQuery client, the pipeline triggers an immediate, lightweight API health check (pinging dataset lists). If credentials or service accounts are expired or missing, execution halts instantly before any heavy file processing begins.
5. **Separation of Logging Concerns**: 
   Detailed technical logs (debug levels, batch upload statuses) are written locally via `loguru`. High-level business milestones (e.g., Pipeline Success / Critical Failure for a specific time window) are pushed asynchronously to a designated Discord channel.

---

## ⚙️ Setup & Installation

### 1. Environment Variables
Create a `.env` file in the root directory (this file is included in `.gitignore` to keep credentials secure):
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/gcp-key.json
DISCORD_WEBHOOK_URL=https://discord.com...
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Adjust the Ingestion Window
Modify the ingestion dates in `config.yaml` to simulate incremental loads over different time frames:
```yaml
ingestion_window:
  start_date: "2017-01-01"
  end_date: "2017-01-31"
  chunk_size: 5000
```

### 4. Execute the Pipeline
Run the project as a module from the root directory:
```bash
python -m src.main
```

---

## 📈 Next Steps (dbt Analytics Layer)
Once the raw layer (`olist_raw`) is populated in BigQuery, the dbt project takes over to:
* Cleanse, cast, and deduplicate incremental batches (Staging layer).
* Structure data into Star/Snowflake schemas (Marts layer).
* Implement dbt incremental materializations to optimize DWH processing costs.



--------------------- v2
# Olist E-Commerce ELT Pipeline

This is a Python-based data ingestion tool that loads the Olist marketplace dataset into Google BigQuery. It simulates an incremental data loading process (ELT approach) where data is filtered by date and appended in batches, preparing it for downstream transformations with dbt.

## 🛠️ Tech Stack
* Python 3.12+ (Pandas)
* Google BigQuery
* dbt (Data Build Tool)
* Loguru (Logging) & Discord Webhooks (Alerts)
* YAML (Configuration)

---

## 📂 Project Structure
```
my_project/
├── dbt_project/          # dbt models and tests
├── src/                  # Python source code
│   ├── connectors/
│   │   └── bq.py         # BigQueryConnector class (handles client and loading)
│   ├── pipelines/
│   │   └── olist.py      # Main pipeline logic and data batching
│   ├── utils/
│   │   ├── alerts.py     # Discord webhook notifications
│   │   └── logger.py     # Loguru config
│   └── main.py           # Entry point
├── config.yaml           # Table metadata and ingestion parameters
├── .env.example          # Environment variables template
└── README.md
```

---

## 🚀 How it Works & Engineering Decisions

* **Memory Management**: Instead of loading huge CSV files into memory at once, the pipeline uses a custom Python generator with `yield`. It filters the data by date and splits it into chunks (`chunksize`) before sending it to BigQuery. This keeps RAM usage low and stable.
* **Config-Driven Architecture**: All 9 tables from the Olist dataset are registered in `config.yaml`. The Python code is fully generic. If you need to add a new table, you just add its path and name to the YAML file without modifying any Python scripts.
* **Dynamic Table Partitioning**: The `BigQueryConnector` automatically checks if a table has a date column. For transactional data (like `orders`), it enables daily partitioning in BigQuery to optimize future query costs. For static lookups (like `customers`), it loads data normally.
* **Fail-Fast Verification**: When the script starts, it immediately pings BigQuery (`list_datasets`) to check the service account credentials. If the credentials are expired or invalid, the pipeline stops right away before wasting time processing files.
* **Alerting and Logs**: Detailed debugging steps are written to local files using `loguru`. High-level events—such as a successful pipeline run or a critical failure—are sent as a single notification to a Discord channel via webhooks.

---

## ⚙️ Setup

### 1. Environment Variables
Create a `.env` file in the root directory (do not commit this file to GitHub):
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/gcp-key.json
DISCORD_WEBHOOK_URL=https://discord.com...
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Ingestion Window
You can change the simulation period in `config.yaml`:
```yaml
ingestion_window:
  start_date: "2017-01-01"
  end_date: "2017-01-31"
  chunk_size: 5000
```

### 4. Run the Pipeline
Run the project as a module from the root directory:
```bash
python -m src.main
```


-------------------------------- OP 3
# BigQuery Olist Data Pipeline 🚀

A lightweight, robust Python data pipeline designed to extract local data chunks, apply time-based filtering, and upload them efficiently to Google BigQuery. 

The pipeline includes standard enterprise-ready features like strict logging levels, automated Discord notifications via webhooks, and an optional **Sci-Fi Hybrid Mode** to keep local development entertaining.

---

## 🛠️ Key Features

* **Smart Data Extraction**: Processes large CSV datasets in memory-efficient chunks (`pandas` generators) preventing OOM (Out of Memory) issues.
* **Dynamic Truncate/Append Logic**: Automatically handles data refreshes (`WRITE_TRUNCATE` for fresh initialization) and continuous streaming (`WRITE_APPEND`).
* **Time Partitioning Support**: Integrates directly with BigQuery's native day-partitioning engine.
* **Dual-State System Dashboard**: 
  * `prod`: Clean, standard, formal logs ready for enterprise environments.
  * `fun`: An immersive Sci-Fi themed telemetry feed featuring interactive ASCII-kaomoji characters (`[o_o]7`).
* **Discord Integration**: Rich `Embed` alert cards sent directly to your server on pipeline failure or successful deployment cycles.

---

## 📂 Project Structure

```text
├── connectors/
│   └── bq.py                # BigQuery connection manager & batch uploader
├── pipelines/
│   └── olist_pipeline.py    # Main data extraction and processing generator
├── utils/
│   ├── __init__.py          # Simplifies core routing and flat imports
│   └── logger.py            # Custom PipelineLogger class wrapper with Discord handler
├── logs/
│   └── bigquery_loader.log  # Local rolling file logging storage
├── .env                     # Local environment file for credentials (gitignored)
├── config.yaml              # Global pipeline settings and source mappings
└── main.py                  # Pipeline execution gatekeeper
```

---

## ⚙️ Configuration Setup

### 1. Environment Variables (`.env`)
Create a `.env` file in the root directory to store your sensitive credentials safely:

```env
GOOGLE_CLOUD_PROJECT_ID="your-gcp-project-id"
DISCORD_WEBHOOK_URL="https://discord.com"
```

### 2. Configuration Settings (`config.yaml`)
Control the source mappings, date scopes, partition behaviors, and visual themes seamlessly:

```yaml
pipeline_settings:
  logging_level: "INFO"       # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console_log: true           # Set false to completely suppress terminal logging
  fun_mode: true              # Switch to FALSE for strict corporate logging style
  start_date: "2016-01-01"    # Lower bound execution boundary
  end_date: "2018-12-31"      # Upper bound execution boundary
  chunk_size: 50000           # Rows allocation size processed per transaction batch

sources:
  - table_name: "olist_orders"
    file_path: "data/olist_orders_dataset.csv"
    date_col: "order_purchase_timestamp"

destination:
  dataset_id: "olist_raw_data"
```

---

## 🛫 Quick Start

1. Ensure your Google Application Credentials are validly configured locally or inside your shell instance.
2. Initialize and kick off the workflow:

```bash
python main.py
```

## 🛡️ Error Boundary & Resilience

The pipeline encapsulates critical processes within dedicated fallback structures. If a core process faults, the system captures the specific stack trace, safely attempts a diagnostic transfer to your Discord incident channel, and raises an explicit termination code to maintain data consistency.


## 🛫 Installation & Quick Start

### 1. Clone the repository and navigate to the project root:
```bash
cd bq-olist-pipeline
```

### 2. Set up a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install all required dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the pipeline:
```bash
python main.py
```

### Telemetry Preview (`fun_mode: true`)
```text
[2026-06-08 22:15:00] INFO |  [o_o]7 SHIELDS UP! Deflecting incoming pipeline errors.
[2026-06-08 22:15:01] INFO |  (⌐■_–) Connecting to BigQuery. Initiating data beam...
[2026-06-08 22:15:05] SUCCESS |  ヘ( ^o^ )ノ * . * . Mission accomplished! Data delivered.
```
## 📂 Project Structure

```text
my_project/
├── dbt_project/             # dbt models for downstream data transformation
├── src/                     # Core pipeline source code
│   ├── connectors/
│   │   └── bq.py            # BigQuery connection manager & batch uploader
│   ├── pipelines/
│   │   └── olist_pipeline.py # Main data extraction and processing generator
│   ├── utils/  
│   │   └── logger.py        # Custom PipelineLogger class wrapper with Discord handler
│   └── main.py              # Pipeline execution gatekeeper
├── config.yaml              # Global pipeline settings and source mappings
├── .env.example             # Template for environment variables (copy to .env)
└── README.md                # Project documentation
```
### 1. Environment Variables
Copy the template file to create your local `.env`:
```bash
cp .env.example .env
```
Now, open `.env` and fill in your actual credentials:
```env
GOOGLE_CLOUD_PROJECT_ID="your-gcp-project-id"
DISCORD_WEBHOOK_URL="https://discord.com"
```
### 4. Run the pipeline:
```bash
python src/main.py
```
