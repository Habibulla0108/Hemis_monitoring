# backend/hemis_client/services/hemis_api.py
import logging

logger = logging.getLogger(__name__)


import requests
from django.conf import settings

class HemisClient:
    def __init__(self):
        self.api_url = settings.HEMIS_BASE_URL
        self.api_token = settings.HEMIS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint, params=None):
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HEMIS API Error ({endpoint}): {e}")
            raise

    def get_department_list(self, limit=200):
        """
        HEMIS dan fakultet/kafedra ro'yxatini oladi.
        endpoint: /v1/data/department-list
        """
        return self._get("/v1/data/department-list", params={"limit": limit})

    def get_education_forms(self) -> list[dict]:
        """
        HEMIS dan 'Ta'lim shakllari' (h_education_form) klassifikatorini oladi.
        """
        endpoint = "/v1/data/classifier-list"
        
        # Method 1: Try filtering by classifier code
        try:
            payload = self._get(endpoint, params={"classifier": "h_education_form"})
            items = payload.get("data", {}).get("items", [])
            # If API supports filtering and returns 1 item, use it.
            if items:
                 options = items[0].get("options", [])
                 if options:
                     return self._normalize_forms(options)
        except Exception:
             pass

        # Method 2: Fallback to fetching all (limit=200) and finding it
        try:
             payload = self._get(endpoint, params={"limit": 200})
             items = payload.get("data", {}).get("items", [])
             for item in items:
                 if item.get("classifier") == "h_education_form":
                     return self._normalize_forms(item.get("options", []))
        except Exception as e:
            logger.error(f"Failed to fetch education forms: {e}")

        # Static Fallback (Last Resort)
        return [
            {"id": 11, "name": "Kunduzgi", "code": "11"},
            {"id": 12, "name": "Kechki", "code": "12"},
            {"id": 13, "name": "Sirtqi", "code": "13"},
            {"id": 14, "name": "Masofaviy", "code": "14"},
            {"id": 15, "name": "Ikkinchi oliy (sirtqi)", "code": "15"},
            {"id": 16, "name": "Ikkinchi oliy (kunduzgi)", "code": "16"},
            {"id": 17, "name": "Magistratura (kunduzgi)", "code": "17"},
        ]

    def _normalize_forms(self, options: list) -> list[dict]:
        """
        Convert classifier options to standard format {id, name, code}.
        """
        result = []
        for opt in options:
            try:
                # Classifier options usually have 'code' and 'name'.
                # We use 'code' as 'id' (int) and logic elsewhere uses int id.
                code = opt.get("code")
                name = opt.get("name")
                if code and name:
                    result.append({
                        "id": int(code),
                        "code": str(code),
                        "name": name
                    })
            except (ValueError, TypeError):
                continue
        return result

    def get_student_count(
        self,
        *,
        department_id: int | None = None,
        education_form_id: int | None = None,
        student_status_id: int | None = None,
    ) -> int:
        """
        /v1/data/student-list endpointiga limit=1 bilan so'rov yuboradi
        va faqat pagination.totalCount ni qaytaradi.

        department_id  – fakultet / bo'lim ID (biz oldin qaysi maydonni ishlatgan bo'lsak,
                          o'shani _department yoki _struct orqali yuboramiz)
        education_form_id – ta'lim shakli ID (_education_form)
        student_status_id – talaba statusi (_student_status), active = 11
        """
        endpoint = "/v1/data/student-list"
        params: dict[str, object] = {
            "page": 1,
            "limit": 1,
        }

        # ⚠️ MUHIM: oldingi kodda fakultet uchun qaysi filter ishlatilgan bo'lsa,
        # shu yerda ham o'shani ishlating.
        # Agar avval `_struct` deb ishlatgan bo'lsangiz, pastdagi `_department`ni
        # `_struct`ga almashtiring.
        # Verified parameters from diagnosis
        if department_id is not None:
            params["_department"] = department_id

        if education_form_id is not None:
            params["_education_form"] = education_form_id

        if student_status_id is not None:
            params["_student_status"] = student_status_id

        try:
            payload = self._get(endpoint, params=params)
        except Exception as exc:  # requests.HTTPError va boshqalar
            logger.error("HEMIS student_count error: %s", exc, exc_info=True)
            return 0  # Return 0 on error to prevent 500s

        # Handle nested pagination (common in HEMIS v1/data endpoints)
        # Check root first, then data.pagination
        pagination = payload.get("pagination")
        
        if not pagination:
             data_node = payload.get("data")
             if isinstance(data_node, dict):
                 pagination = data_node.get("pagination")
        
        if not pagination:
            # Still no pagination found?
            return 0

        total = pagination.get("totalCount") or pagination.get("total_count") or 0
        try:
            return int(total)
        except (TypeError, ValueError):
            logger.warning("Unexpected totalCount value from HEMIS: %r", total)
            return 0
