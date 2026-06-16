# Olist E-Commerce Ingestion Pipeline

A config-driven batch data ingestion pipeline designed to extract e-commerce data from local CSV files and load it into Google BigQuery. This repository acts as the **RAW** layer provider in an ELT (Extract-Load-Transform) architecture. All subsequent data cleansing, type casting, and analytical modeling are decoupled and handled inside BigQuery using **dbt**.

## Tech Stack
[![Python 3.12](https://shields.io)](https://python.org)
[![Pandas](https://shields.io)](https://pydata.org)
[![Google BigQuery](https://shields.io)](https://google.com)
[![dbt](https://shields.io)](https://getdbt.com)
[![Loguru](https://shields.io)](https://github.com)


---

### Core Engineering Decisions

* **Memory Optimization (Streaming Architecture)**: To prevent Out-Of-Memory (OOM) crashes on larger datasets, files are processed sequentially in blocks using `pd.read_csv(chunksize=...)`. This ensures a flat and predictable RAM footprint regardless of the source file size.
* **On-the-Fly Filtering**: Time-window filters (`start_date` / `end_date`) are evaluated inside a lazy generator for each batch. An explicit `.copy()` call is enforced after filtering to eliminate Pandas `SettingWithCopyWarning` when appending metadata.
* **Separation of Concerns (Low Coupling)**: The `BigQueryConnector` is completely stateless and isolated. It has no knowledge of pipeline orchestration or logging wrappers. Its sole responsibility is to stream a DataFrame into BigQuery and provision native daily time-partitioning if a partition field is specified in the configuration.
* **Idempotency & Load Strategies**: The pipeline runs `WRITE_APPEND` for transactional tables with dates. For static dictionaries or lookup tables without date fields, it applies a `WRITE_TRUNCATE` strategy on the very first batch and appends the rest. This allows safely re-running the pipeline without data duplication.
* **Audit Columns**: Every processed row is enriched with a `_loaded_at` UTC timestamp. This serves as a vital audit field for downstream dbt data freshness checks and incremental model rebuilds.

---

### Logging & Monitoring (`PipelineLogger`)

All tracking logic is encapsulated in a dedicated wrapper over `loguru`, routing logs into distinct operational streams:
* **Console Output**: Set to `INFO` level to block internal Google SDK API noise. Target table names are dynamically padded and aligned into a clean vertical column using contextual `.bind()`.
* **Log File**: Captures a deep `DEBUG` trace (including module names, exact functions, and line numbers) for incident post-mortems. Automated file rotation is triggered once a file reaches 10 MB.
* **Discord Alerts**: Upon pipeline initialization, success, or unhandled exceptions, the logger automatically pushes a structured card with technical tracebacks to a Discord channel via webhooks.
* **Personalized Touch (Fun Mode)**: When enabled, the initialization phase selects a single random Kaomoji text assistant (e.g., `☂[o_o]` or `(⌐■_■)`) from a curated list, giving the terminal interface a clean yet unique style without adding log spam.

---

### 📁 Project Structure
```
dbt-olist/
├── dbt_project/          # dbt models, macros, and schema tests
├── src/                  # Python pipeline source code
│   ├── connectors/
│   │   └── bq.py         # BigQueryConnector (Stateless DataFrame upload)
│   ├── pipelines/
│   │   └── olist.py      # Pipeline orchestrator & lazy batch data generator
│   ├── utils/
│   │   └── logger.py     # PipelineLogger (Loguru config, Discord alerts & context)
│   ├── config.py         # Strongly-typed AppConfig schema (Dataclasses)
│   └── main.py           # Execution entry point (Initializes config, logs, and runs pipeline)
├── config.yaml           # Metadata catalog and settings for all Olist source files
├── .env.example          # Environment variables template
└── README.md
```

---

### ⚙ How to Run

#### 1. Environment Setup
Create a local `.env` file in the project root matching the template:
```env
GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/gcp-key.json
DISCORD_WEBHOOK_URL=https://discord.com...
```

#### 2. Configuration Settings (`config.yaml`)
Control runtime parameters and output routing dynamically without modifying Python files:
```yaml
pipeline_settings:
  chunk_size: 50000
  logging_level: "DEBUG"
  log_to_console: true
  log_to_file: true
  fun_mode: true
```

#### 3. Execution
```bash
pip install -r requirements.txt
python -m src.main
```

---

## ◈ Next Steps (dbt Analytics Layer)
Once the `raw_olist` dataset is successfully populated by this pipeline, the dbt engine takes control to:
* Cleanse, cast data types, and deduplicate historical load records (Staging layer).
* Execute automated data quality checks via native schema tests.
* Materialize dimensional star/snowflake schemas (Marts layer) optimized for BI reporting.