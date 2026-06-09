import pandas as pd
from connectors import BigQueryConnector
from utils import logger

def batch_data_extractor(
        file_path: str, 
        date_col: str | None, 
        start_dt: str, 
        end_dt: str, 
        chunk_size: int
):

    df = pd.read_csv(file_path)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]
        logger.info(f"Applied filter by date [{date_col}]. Rows remains: {len(df)}")
    else:
        logger.info(f"Upload table without filtration")

    if df.empty:
        return
    
    total_rows = len(df)
    for i in range(0, total_rows, chunk_size):
        chunk = df.iloc[i: i + chunk_size]
        yield chunk


def run_olist(config: dict):
    start_dt = config["pipeline_settings"]["start_date"]
    end_dt = config["pipeline_settings"]["end_date"]
    chunk_size = config["pipeline_settings"]["chunk_size"]

    bq = BigQueryConnector()

    for table_cfg in config["sources"]:
        table_name = table_cfg["table_name"]
        file_path = table_cfg["file_path"]
        date_col = table_cfg["date_col"]

        logger.info(f"Start loading table: {table_name}")

        try:
            batches = batch_data_extractor(
                file_path=file_path,
                date_col=date_col,
                start_dt=start_dt,
                end_dt=end_dt, 
                chunk_size=chunk_size,
            )

            for batch_num, chunk in enumerate(batches, start=1):
                logger.debug(f"Loading batch #{batch_num} for table {table_name}...")

                if not date_col and batch_num == 1:
                    write_disposition = "WRITE_TRUNCATE"
                else:
                    write_disposition = "WRITE_APPEND"

                bq.load_dataframe(
                    dataframe=chunk,
                    dataset_id=config["destination"]["dataset_id"],
                    table_id=table_name,
                    partition_column=date_col,
                    write_disposition=write_disposition,
                )
            logger.info(f"Table {table_name} fully downloaded.\n")
        except Exception as e:
            logger.error(f"Upload was failed for table {table_name}: {e} ")
            raise e



