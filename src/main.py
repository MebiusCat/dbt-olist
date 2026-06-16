from config import load_config
from pipelines.olist_pipeline import run_olist
from utils import PipelineLogger
   

def main():  
    config = load_config()

    if not config:
        print("CRITICAL: Pipeline initialization failed. Configuration file is missing or corrupted.")
        return
    
    log = PipelineLogger(config=config)
    log.pipeline_start()
    
    start_dt = config.pipeline_settings.start_date
    end_dt = config.pipeline_settings.end_date

    try:
        run_olist(config=config, log=log)

        success_msg = f"Pipeline olist was uploaded for period `{start_dt}` - `{end_dt}`. All tables uploaded to BigQuery."
        log.pipeline_success()
        log.alert_discord(status="success", message=success_msg)

    except Exception as e:
        error_msg = f"Pipeline olist failed for period`{start_dt}` - `{end_dt}`. Error: {e}"
        log.log_error(f"{error_msg} Error: {e}")
        log.pipeline_crash()

        log.alert_discord(status="error", message=error_msg, details=str(e))
        raise e
    
    
if __name__ == '__main__':
    main()
