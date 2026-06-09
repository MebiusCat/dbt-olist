import os
import yaml

from dotenv import load_dotenv

from connectors import bq
from pipelines.olist_pipeline import run_olist
from utils import logger, alert_discord, PipelineLogger

CONFIG_PATH = "config.yml"

load_dotenv()

def load_config(config_path: str = CONFIG_PATH) -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            if "pipeline_settings" in config:
                config["pipeline_settings"]["discord_webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL")
            return config
    except FileNotFoundError:
        return {}
        

def main():  
    config = load_config()
    log = PipelineLogger()

    log.start()

    if not config:
        log.config_error()
        log.alert_discord(status="error", message="Pipeline initialization failed. Bad config.")

    start_dt = config["pipeline_settings"]["start_date"]
    end_dt = config["pipeline_settings"]["end_date"]

    # try:
    #     config = load_config("config.yaml")     
    #     start_dt = config["pipeline_settings"]["start_date"]
    #     end_dt = config["pipeline_settings"]["end_date"]
    # except (FileNotFoundError, KeyError) as e:
    #     logger.error(f"Failed to load config or settings: {e}")
    #     alert_discord(f"Pipeline initialization failed. Bad config: {e}")        
    #     raise e

    try:
        log.connecting()
        run_olist(config=config)

        success_msg = f"Pipeline olist was uploaded for period `{start_dt}` - `{end_dt}`. All tables uploaded to BigQuery."
        log.success()
        log.alert_discord(status="success", message=success_msg)
        # alert_discord(success_msg)
    except Exception as e:
        error_msg = f"Pipeline olist failed for period`{start_dt}` - `{end_dt}`. Error: {e}"
        logger.error(f"{error_msg} Error: {e}")
        log.crash()

        log.alert_discord(status="error", message=error_msg, details=str(e))
        raise e
    
        # try:
        #     alert_discord(error_msg)
        # except Exception as webhook_err:
        #     logger.critical(f"Failed to send Discord webhook: {webhook_err}")
        # raise e
    
if __name__ == '__main__':
    main()

    # logger.info(f'Your data: {os.environ['POSTGRES_USER']} leak to our pipe ahaahahaha')
    # logger.info('main')
    # logger.info('I\'m here, among the shadows')
    # logger.warning('Finish line')

    # conn = bq.get_client()
    # source_file = "../raw_bq/olist_customers_dataset.csv"
    # target_table = "ecom_olist.raw_customers"

    # try:
    #     data_stream = extract_from_csv(source_file)
    #     load_data(conn, data_stream, target_table)
    #     logger.info("My data moving, moving (o_o)ﾉﾞ POKA NEUDACHNIKI, YA V GUGL")
    # except Exception as e:
    #     logger.error(f"Pipelne error, alert!")
# 
    # logger.info(check_bigquery_connection())