import os
import pandas as pd

from google.cloud import bigquery
from config import AppConfig
from utils.logger import logger

class BigQueryConnector:
    """Class to manage connection and data loading into BigQuery"""

    def __init__(self, config: AppConfig):
        self.project_id = config.pipeline_settings.project_id

        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID is missing")
        
        self.client = bigquery.Client(project=self.project_id)
        logger.debug(f"BigQuery client successfully initialized for project: {self.project_id}")
        
        self.test_connection()

    def test_connection(self) -> bool:
        try:
            list(self.client.list_datasets(max_results=1))
        except Exception as e:
            logger.critical(f"Failed connection to BigQuery: {e}")
            raise ConnectionError(f"Failed to connect to BigQuery: {e}")

    def load_dataframe(
            self,
            dataframe: pd.DataFrame,
            dataset_id: str,
            table_id: str,
            partition_column: str | None, 
            write_disposition: str = "WRITE_APPEND",
            is_first_batch: bool = False,
        ) -> None:
        """
        Uploads a data chunk to BigQuery with dynamic partitioning support.
        """
        table_logger = logger.bind(table=table_id)

        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"

        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            write_disposition=write_disposition.upper(),            
        )

        # Dynamically configure partitioning only if a partition column is provided        
        if partition_column:
            job_config.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_column
            )
            if is_first_batch:
                table_logger.debug(f"BQ Job config: partitioning enabled on field: '{partition_column}'")
        else:
            if is_first_batch:
                table_logger.debug(f"BQ config: loading into a standard(non-partitioned) table.")
        
        try:
            table_logger.debug(f"Starting batch upload to {table_ref}")
            job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
            job.result()

            table_logger.debug(f"BQ Job Success: loaded chunk into {dataset_id}.{table_id}. Rows: {len(dataframe)}")
        
        except Exception as e:
            table_logger.error(f"BigQuery API error while loading into {table_id}: {e}")
            raise e
        