# backend/hemis_client/services/hemis_api.py
import logging
import time
import random
import requests
from typing import Any
from django.conf import settings

logger = logging.getLogger(__name__)


class HemisClient:
    def __init__(self):
        self.api_url = settings.HEMIS_BASE_URL.rstrip("/")
        self.api_token = settings.HEMIS_TOKEN

        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.api_url}{endpoint}"

        # 429 uchun yumshoq retry (backoff)
        max_retries = 4
        base_sleep = 0.6

        for attempt in range(max_retries):
            try:
                resp = self.session.get(
                    url, headers=self.headers, params=params, timeout=15
                )

                # Rate limit bo‘lsa - kutib qayta uramiz
                if resp.status_code == 429:
                    sleep_s = base_sleep * (2 ** attempt) + random.uniform(0.1, 0.4)
                    logger.warning("HEMIS 429 Too Many Requests. Sleep %.2fs then retry. url=%s", sleep_s, url)
                    time.sleep(sleep_s)
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.RequestException as e:
                # oxirgi urinishda raise
                if attempt == max_retries - 1:
                    logger.error("HEMIS API Error (%s): %s", endpoint, e, exc_info=True)
                    raise
                sleep_s = base_sleep * (2 ** attempt) + random.uniform(0.1, 0.4)
                logger.warning("HEMIS request error. Sleep %.2fs then retry. endpoint=%s err=%s", sleep_s, endpoint, e)
                time.sleep(sleep_s)

        # amalda bu yerga kelmaydi
        raise RuntimeError("HEMIS request failed after retries")

    # -----------------------
    # BASIC LISTS
    # -----------------------
    def get_department_list(self, limit: int = 200) -> dict:
        return self._get("/v1/data/department-list", params={"limit": limit})

    def get_group_list(self, *, department_id: int | None = None, education_form_id: int | None = None,
                       curriculum_id: int | None = None, limit: int = 200) -> dict:
        """
        Guruhlar ro‘yxati (HEMIS: /v1/data/group-list)
        Paramlar HEMISga qarab ishlaydi: _department, _education_form, _curriculum
        """
        params: dict[str, Any] = {"page": 1, "limit": limit}
        if department_id:
            params["_department"] = department_id
        if education_form_id:
            params["_education_form"] = education_form_id
        if curriculum_id:
            params["_curriculum"] = curriculum_id
        return self._get("/v1/data/group-list", params=params)

    def get_curriculum_list(self, *, department_id: int | None = None, education_form_id: int | None = None,
                            limit: int = 200) -> dict:
        """
        O‘quv reja ro‘yxati (HEMIS: /v1/data/curriculum-list)
        """
        params: dict[str, Any] = {"page": 1, "limit": limit}
        if department_id:
            params["_department"] = department_id
        if education_form_id:
            params["_education_form"] = education_form_id
        return self._get("/v1/data/curriculum-list", params=params)

    def get_semester_list(self, *, curriculum_id: int | None = None, limit: int = 50) -> dict:
        """
        Semester ro‘yxati (HEMIS ko‘pincha /v1/data/semester-list yoki classifier bo‘lishi mumkin)
        Sizda ishlayotgan endpoint bo‘lmasa, biz fallback: 1..12 qaytaramiz.
        """
        try:
            params: dict[str, Any] = {"page": 1, "limit": limit}
            if curriculum_id:
                params["_curriculum"] = curriculum_id
            return self._get("/v1/data/semester-list", params=params)
        except Exception:
            return {"data": {"items": [{"id": i, "name": str(i)} for i in range(1, 13)]}}

    # -----------------------
    # EDUCATION FORMS (CLASSIFIER)
    # -----------------------
    def get_education_forms(self) -> list[dict]:
        """
        HEMIS dan 'Ta'lim shakllari' klassifikatorini oladi.
        Agar topilmasa, siz bergan REAL ro‘yxatga fallback qiladi.
        """
        endpoint = "/v1/data/classifier-list"

        # 1) API filter bilan urinish
        try:
            payload = self._get(endpoint, params={"classifier": "h_education_form"})
            items = payload.get("data", {}).get("items", [])
            if items:
                options = items[0].get("options", [])
                if options:
                    return self._normalize_forms(options)
        except Exception:
            pass

        # 2) hammasini olib ichidan topish
        try:
            payload = self._get(endpoint, params={"limit": 200})
            items = payload.get("data", {}).get("items", [])
            for item in items:
                if item.get("classifier") == "h_education_form":
                    return self._normalize_forms(item.get("options", []))
        except Exception as e:
            logger.error("Failed to fetch education forms: %s", e, exc_info=True)

        # 3) ✅ REAL STATIC FALLBACK (siz bergan ro‘yxat)
        return [
            {"id": 11, "name": "Kunduzgi", "code": "11"},
            {"id": 13, "name": "Sirtqi", "code": "13"},
            {"id": 15, "name": "Ikkinchi oliy (sirtqi)", "code": "15"},
            {"id": 14, "name": "Maxsus sirtqi", "code": "14"},
            {"id": 12, "name": "Kechki", "code": "12"},
            {"id": 16, "name": "Masofaviy", "code": "16"},
            {"id": 20, "name": "Qo‘shma (kunduzgi)", "code": "20"},
            {"id": 21, "name": "Qo‘shma (kechki)", "code": "21"},
            {"id": 19, "name": "Ikkinchi oliy (kechki)", "code": "19"},
            {"id": 18, "name": "Ikkinchi oliy (kunduzgi)", "code": "18"},
            {"id": 17, "name": "Qo‘shma (sirtqi)", "code": "17"},
            {"id": 22, "name": "Ikkinchi oliy (masofaviy)", "code": "22"},
            {"id": 23, "name": "Qo‘shma (Masofaviy)", "code": "23"},
        ]

    def _normalize_forms(self, options: list) -> list[dict]:
        result = []
        for opt in options:
            try:
                code = opt.get("code")
                name = opt.get("name")
                if code and name:
                    result.append({"id": int(code), "code": str(code), "name": name})
            except (ValueError, TypeError):
                continue
        return result

    # -----------------------
    # STUDENT COUNT
    # -----------------------
    def get_student_count(
        self,
        *,
        department_id: int | None = None,
        education_form_id: int | None = None,
        student_status_id: int | None = None,
    ) -> int:
        endpoint = "/v1/data/student-list"
        params: dict[str, Any] = {"page": 1, "limit": 1}

        if department_id is not None:
            params["_department"] = department_id
        if education_form_id is not None:
            params["_education_form"] = education_form_id
        if student_status_id is not None:
            params["_student_status"] = student_status_id

        try:
            payload = self._get(endpoint, params=params)
        except Exception as exc:
            logger.error("HEMIS student_count error: %s", exc, exc_info=True)
            return 0

        pagination = payload.get("pagination")
        if not pagination:
            data_node = payload.get("data")
            if isinstance(data_node, dict):
                pagination = data_node.get("pagination")

        if not pagination:
            return 0

        total = pagination.get("totalCount") or pagination.get("total_count") or 0
        try:
            return int(total)
        except (TypeError, ValueError):
            logger.warning("Unexpected totalCount value from HEMIS: %r", total)
            return 0

    # -----------------------
    # ATTENDANCE STAT
    # -----------------------
    def get_curriculum_list(self, params=None):
        return self._get("/v1/data/curriculum-list", params=params or {"limit": 200})

    def get_group_list(self, params=None):
        return self._get("/v1/data/group-list", params=params or {"limit": 200})

    def get_semester_list(self, params=None):
        return self._get("/v1/data/semester-list", params=params or {"limit": 50})

    def get_attendance_stat(self, params=None):
        return self._get("/v1/data/attendance-stat", params=params or {"page": 1, "limit": 200})



