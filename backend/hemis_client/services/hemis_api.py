import requests
import logging
from typing import Any, Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class HemisAPIError(Exception):
    pass


class HemisClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or settings.HEMIS_BASE_URL).rstrip("/")
        self.token = token or settings.HEMIS_TOKEN

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        try:
            logger.debug(f"HEMIS GET Request: {url} | Params: {params}")
            resp = requests.get(url, headers=self.headers, params=params, timeout=30)
        except requests.RequestException as e:
            logger.error(f"HEMIS Connection Error: {str(e)}")
            raise HemisAPIError(f"Connection failed: {str(e)}")

        if resp.status_code != 200:
            logger.error(f"HEMIS Error {resp.status_code}: {resp.text[:500]}")
            raise HemisAPIError(f"HEMIS GET error {resp.status_code}: {resp.text}")

        try:
            payload = resp.json()
        except ValueError:
             logger.error("HEMIS returned non-JSON response")
             raise HemisAPIError("Invalid JSON response from HEMIS")

        # Agar HEMIS success + error formatda kelsa:
        if isinstance(payload, dict) and payload.get("success") is False:
            msg = payload.get("error") or "HEMIS success=False"
            logger.warning(f"HEMIS logic error: {msg}")
            raise HemisAPIError(msg)

        return payload
