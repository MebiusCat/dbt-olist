import os
import urllib.request
import json
from logger import logger

def alert_discord(message: str) -> None:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL was not set up")
        return
    
    payload = {"content": message}
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                logger.debug("Message send to Discord")
            else:
                logger.warning(f"Unusual status was sent by Discord: {response.status}")
    except Exception as e:
        logger.error(f"Sending failed: {e}")