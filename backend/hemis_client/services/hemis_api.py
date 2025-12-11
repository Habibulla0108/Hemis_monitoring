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
        
        # Initialize Persistent Session
        self.session = requests.Session()
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retries = Retry(
            total=3,
            backoff_factor=0.3, 
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=50, pool_maxsize=50)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        try:
            # logger.debug(f"HEMIS GET Request: {url} | Params: {params}")
            resp = self.session.get(url, headers=self.headers, params=params, timeout=10)
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

    def get_student_list(self, limit: int = 200, page: int = 1, **kwargs) -> dict:
        """
        Fetch paginated student list from HEMIS.
        Endpoint: /v1/data/student-list
        """
        endpoint = settings.HEMIS_API_STUDENT_CONTINGENT_ENDPOINT
        params = {
            "limit": limit,
            "page": page,
            **kwargs
        }
        return self._get(endpoint, params=params)

    def get_department_list(self, limit: int = 1000, **kwargs) -> dict:
        """
        Fetch departments (faculties, chairs, etc.).
        Endpoint: /v1/data/department-list
        """
        # Hardcoded endpoint as it wasn't in settings yet, but standard for HEMIS
        endpoint = "v1/data/department-list"
        params = {
            "limit": limit,
            **kwargs
        }
        return self._get(endpoint, params=params)

    def get_student_count(self, **kwargs) -> int:
        """
        Quickly fetch total count of students matching criteria.
        Uses limit=1 to minimize data transfer.
        """
        try:
            # Re-use get_student_list but with limit=1
            data = self.get_student_list(limit=1, page=1, **kwargs)
            # Safe extraction of totalCount
            if isinstance(data, dict):
                return data.get('data', {}).get('pagination', {}).get('totalCount', 0)
            return 0
        except HemisAPIError:
            return 0
