import logging
from typing import Any

import requests

from app.config import Settings

logger = logging.getLogger(__name__)


class InstagramClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = f"https://graph.facebook.com/{settings.api_version}"

    def send_text_message(self, recipient_igid: str, message_text: str) -> dict[str, Any]:
        if not self.settings.instagram_business_account_id:
            raise RuntimeError("INSTAGRAM_BUSINESS_ACCOUNT_ID is not configured")
        if not self.settings.meta_access_token:
            raise RuntimeError("META_ACCESS_TOKEN is not configured")

        url = f"{self.base_url}/{self.settings.instagram_business_account_id}/messages"
        payload = {
            "recipient": {"id": recipient_igid},
            "message": {"text": message_text},
            "messaging_type": "RESPONSE",
        }
        params = {"access_token": self.settings.meta_access_token}
        response = requests.post(url, params=params, json=payload, timeout=30)
        self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return
        try:
            error_payload = response.json()
        except Exception:
            error_payload = {"raw": response.text}
        logger.error("Meta API error: %s", error_payload)
        response.raise_for_status()
