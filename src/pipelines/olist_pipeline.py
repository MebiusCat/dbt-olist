import pandas as pd
from connectors import BigQueryConnector
from config import AppConfig
from pathlib import Path
from utils import PipelineLogger

def batch_data_extractor(
        file_path: str, 
        date_col: str | None, 
        start_dt: str, 
        end_dt: str, 
        chunk_size: int
):

    with pd.read_csv(file_path, chunksize=chunk_size) as data:
        for batch in data:
            if date_col:
                batch[date_col] = pd.to_datetime(batch[date_col])

                start_date = pd.to_datetime(start_dt)
                end_date = pd.to_datetime(end_dt)

                batch = batch[(batch[date_col] >= start_date) & (batch[date_col] < end_date)].copy()
                if batch.empty:
                    continue

            batch.loc[:, "_loaded_at"] = pd.Timestamp.now(tz="UTC")

            yield batch
    
def run_olist(config: AppConfig, log: PipelineLogger):
    start_dt = config.pipeline_settings.start_date
    end_dt = config.pipeline_settings.end_date
    chunk_size = config.pipeline_settings.chunk_size

    try:
        bq = BigQueryConnector(config)
        log.connection()
    except Exception as e:
        log.config_error()
        log.alert_discord("error", "Pipeline failed at initialization stage", details=str(e))
        return

    for table_cfg in config.sources:
        table_name = table_cfg.table_name
        file_path = table_cfg.file_path
        date_col = table_cfg.date_col

        log.init_table(table_name, chunk_size)
        base_path = Path(config.pipeline_settings.raw_data_dir)

        try:
            batches = batch_data_extractor(
                file_path=base_path / file_path,
                date_col=date_col,
                start_dt=start_dt,
                end_dt=end_dt, 
                chunk_size=chunk_size,
            )

            batch_num = 0
            for chunk in batches:
                batch_num += 1
                if not date_col and batch_num == 1:
                    write_disposition = "WRITE_TRUNCATE"
                else:
                    write_disposition = "WRITE_APPEND"

                bq.load_dataframe(
                    dataframe=chunk,
                    dataset_id=config.pipeline_settings.dataset_id,
                    table_id=table_name,
                    partition_column=date_col,
                    write_disposition=write_disposition,
                    is_first_batch=(batch_num == 1),
                )
                log.log_batch(
                    table_name=table_name,
                    batch_num=batch_num,
                    rows_loaded=len(chunk)
                )
            
            if batch_num == 0:
                log.logger.warning("No data matched the date filters. Nothing was uploaded.")
            log.complete_table(table_name=table_name)

        except Exception as e:
            log.table_error(table_name=table_name, e=e)
            log.alert_discord(
                status="error",
                message=f"Critical error during BigQuery payload upload for table: {table_name}", 
                details=str(e)
            )
            log.pipeline_crash()

            raise e
        
