import os
import yaml
from datetime import date
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv(override=True)

@dataclass
class PipelineSettings:
    dataset_id: str
    start_date: str
    end_date: str
    logging_level: str
    log_path: str
    log_to_console: bool
    log_to_file: bool

    chunk_size: int = 10000
    console_log: bool = True
    fun_mode: bool = True
    project_id: str | None = None
    raw_data_dir: str | None = None
    discord_webhook_url: str | None = None


@dataclass
class SourceTable:
    file_path: str
    table_name: str
    date_col: str| None


@dataclass
class AppConfig:
    pipeline_settings: PipelineSettings
    sources: list[SourceTable]


def load_config(config_path: str = "src/config.yml") -> AppConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    settings_data = data.get("pipeline_settings", {})
    pipeline_settings = PipelineSettings(
        dataset_id=settings_data.get("dataset_id"),
        start_date=settings_data.get("start_date"),
        end_date=settings_data.get("end_date"),
        logging_level=settings_data.get("logging_level", "INFO"),
        log_path=settings_data.get("log_path"),
        log_to_console=settings_data.get("log_to_console"),
        log_to_file=settings_data.get("log_to_file"),
        chunk_size=int(settings_data.get("chunk_size", 10000)),
        console_log=bool(settings_data.get("console_log", True)),
        fun_mode=bool(settings_data.get("fun_mode", True)),
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
        raw_data_dir=os.getenv("RAWDATA_DIR"),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
    )

    sources = []
    for src in data.get("sources", []):
        sources.append(
            SourceTable(
                file_path=src.get("file_path"),
                table_name=src.get("table_name"),
                date_col=src.get("date_col"),
            )
        )

    return AppConfig(
        pipeline_settings=pipeline_settings,
        sources=sources,
    )

