import json
import sys
import urllib.request

from loguru import logger

LOG_PATH = "logs/bigquery_loader.log"

# def setup_logging(config: dict) -> None:
#     settings = config["pipeline_settings"]
#     log_level = settings["logging_level"].upper()

#     logger.remove()
#     logger.info(" (o_o)7 Blackbox activated. Scanning space...")

#     if not config["pipeline_settings"]["console_log"]:
#         logger.remove()

#     logger.add(
#         LOG_PATH,
#         rotation="10 MB",
#         retention="5 days",
#         level=log_level,
#         encoding="utf-8",
#     )

class PipelineLogger:
    # logger.info(" [o_o]7 SHIELDS UP! Deflecting incoming pipeline errors.")
    _PHRASES = {
        "start": {
            True: " [o_o]7 SHIELDS UP! Deflecting incoming pipeline errors.",
            True: " (o_o)7 Blackbox activated. Scanning space...",
            False: "Pipeline telemetry enabled. Monitoring system state..."
        },
        "connecting": {
            True: " (⌐■_■) Establishing secure uplink to BigQuery...",
            True: " (⌐■_–) Connecting to BigQuery. Initiating data beam...",
            False: "Establishing connection to Google BigQuery storage..."
        },
        "success": {
            True: " ヘ( ^o^ )ノ * . * . Mission accomplished! Data delivered.",
            False: "Pipeline finished successfully. Data transfer completed."
        },
        "config_error": {
            True: " ＼(〇_ｏ)／ Shields CRITICAL! Bad config.",
            False: "Initialization failed: Configuration file error."
        },
        "crash": {
            True: " ＼(〇_ｏ)／ Deflector shields offline! Systems failing.",
            False: "Critical error during BigQuery payload upload pipeline."
        }
    }

    _DISCORD_TITLES = {
        "success": {
            True: " ヘ( ^o^ )ノ * . * . Mission Accomplished!",
            False: "Pipeline Execution Success"
        },
        "error": {
            True: " ＼(〇_ｏ)／ Shields CRITICAL!",
            False: "Pipeline Execution Failure"
        }
    }

    def __init__(self, config: dict) -> None:
        settings = config.get("pipeline_settings", {})
        log_level = settings.get("logging_level", "INFO").upper()

        self.fun_mode = settings.get("fun_mode", False)
        self.webhook_url = settings.get("DISCORD_WEBHOOK_URL")

        logger.remove()
        # logger.info(" (o_o)7 Blackbox activated. Scanning space...")

        if not settings.get("console_log", False):
            logger.add(sys.stderr, level=log_level)

        logger.add(
            LOG_PATH,
            rotation="10 MB",
            retention="5 days",
            level=log_level,
            encoding="utf-8",
        )

    def start(self) -> None:
        logger.info(self._PHRASES["start"][self.fun_mode])
    
    def connecting(self) -> None:
        logger.info(self._PHRASES["connecting"][self.fun_mode])

    def success(self) -> None:
        logger.info(self._PHRASES["success"][self.fun_mode])
    
    def config_error(self) -> None:
        logger.error(self._PHRASES["config_error"][self.fun_mode])
    
    def crash(self) -> None:
        logger.error(self._PHRASES["crash"][self.fun_mode])

    def alert_discord(self, status: str, message: str, details: str = None) -> None:
        if not self.webhook_url:
            logger.warning(" Discord webhook URL is missing. Skipping alert.")
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
            logger.critical(f"Failed to send Discord webhook: {e}")

logger = logger