import json
import sys
import time
import urllib.request
from loguru import logger
from config import AppConfig
from . import creatures


class PipelineLogger:

    _DISCORD_TITLES = {
        "success": {
            True: " ☂[o_o] Mission Accomplished!",
            False: "Pipeline Execution Success"
        },
        "error": {
            True: " ＼(〇_ｏ)／ CRITICAL! Mission Failed!",
            False: "Pipeline Execution Failure"
        }
    }

    def __init__(self, config: AppConfig) -> None:
        settings = config.pipeline_settings
        log_level = settings.logging_level

        self.fun_mode = settings.fun_mode
        self.webhook_url = settings.discord_webhook_url
        self._timers = {}

        logger.configure(extra={"table": ""})
        logger.remove()

        if settings.log_to_console:
            console_format = (
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<magenta>{extra[table]: <15}</magenta> | "
                "{message}"
            )
            logger.add(sys.stderr, format=console_format, level="INFO")
        
        if settings.log_to_file:
            file_format = (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "[{extra[table]}] - "
                "{message}"
            )
            logger.add(
                settings.log_path,
                format=file_format,
                rotation="10 MB",
                retention="5 days",
                level=log_level,
                encoding="utf-8",
            )    
        self.logger = logger.bind(table="")    

    def pipeline_start(self) -> None:
        self.logger.info(
            creatures.get_log_format("start", self.fun_mode)
        )
    
    def connection(self) -> None:
        self.logger.info("Establishing connection to Google BigQuery storage...")

    def pipeline_success(self) -> None:
        self.logger.info(
            creatures.get_log_format("success", self.fun_mode)
        )
    
    def config_error(self) -> None:
        self.logger.error("Initialization failed: Configuration file error.")
    
    def pipeline_crash(self) -> None:
        self.logger.error("Critical error during BigQuery payload upload pipeline.")

    def init_table(self, table_name: str, chunk_size: int) -> None:
        self._timers[table_name] = {
            "start_time": time.time(),
            "chunk_size": chunk_size,
            "total_rows_loaded": 0,
        }
        self.logger = logger.bind(table=table_name)
        self.logger.info(f"Start loading table. Chunk size: {chunk_size}")
    
    def log_batch(self, table_name: str, batch_num: int, rows_loaded: int) -> None:
        table_meta = self._timers.get(table_name)

        if table_meta:
            table_meta["total_rows_loaded"] += rows_loaded
            total_rows = table_meta["total_rows_loaded"]
        else:
            total_rows = rows_loaded

        self.logger.debug(
            f"Successfully loaded batch #{batch_num:03d}. "
            f"Rows in batch: {rows_loaded} | Total rows loaded: {total_rows}"
        )
    
    def complete_table(self, table_name: str) -> None:
        timer_data = self._timers.get(table_name)
        if timer_data:
            cur_loop = time.time() - timer_data["start_time"]
            total_rows = timer_data["total_rows_loaded"]

            self.logger.info(
                f"Table fully downloaded. "
                f"Total rows: {total_rows} | Time elapsed: {cur_loop:.2f}s"
            )
        self.logger = logger.bind(table="")

    def table_error(self, table_name: str, e: Exception) -> None:
        self.logger.error(f"Upload was failed for table '{table_name}': {e} ")

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    def alert_discord(self, status: str, message: str, details: str = None) -> None:
        if not self.webhook_url:
            self.logger.warning(" Discord webhook URL is missing. Skipping alert.")
            return
        
        if status == "success":
            color = 3066993  # Green (#2ECC71)
            title = self._DISCORD_TITLES["success"][self.fun_mode]
        else:
            color = 15158332 # Red (#E74C3C)
            title = self._DISCORD_TITLES["error"][self.fun_mode]
        
        footer_text = "🤖 BQ Loader Subsystem" if self.fun_mode else "Production Data Pipeline"

        embed = {
            "title": title,
            "description": message,
            "color": color,
            "footer": {"text": footer_text}
        }

        if details:
            embed["fields"] = [{
                "name": "Technical Details" if self.fun_mode else "Error Trace",
                "value": f"```python\n{details}\n```",
                "inline": False        
            }]
        
        payload = {"embeds": [embed]}

        try:
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req):
                pass
        except Exception as e:
            self.logger.critical(f"Failed to send Discord webhook: {e}")

logger = logger