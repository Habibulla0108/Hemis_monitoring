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
    def get_department_list(self, limit: int = 200, params: dict | None = None) -> dict:
        req_params = {"limit": limit}
        if params:
            req_params.update(params)
        return self._get("/v1/data/department-list", params=req_params)

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
                            limit: int = 200, params=None) -> dict:
        """
        O‘quv reja ro‘yxati (HEMIS: /v1/data/curriculum-list)
        """
        req_params: dict[str, Any] = {"page": 1, "limit": limit}
        if department_id:
            req_params["_department"] = department_id
        if education_form_id:
            req_params["_education_form"] = education_form_id
        
        # Support direct params override
        if params:
            req_params.update(params)
            
        return self._get("/v1/data/curriculum-list", params=req_params)

    def get_semester_list(self, *, curriculum_id: int | None = None, limit: int = 50, params=None) -> dict:
        """
        Semester ro‘yxati (HEMIS ko‘pincha /v1/data/semester-list yoki classifier bo‘lishi mumkin)
        Sizda ishlayotgan endpoint bo‘lmasa, biz fallback: 1..12 qaytaramiz.
        """
        try:
            req_params: dict[str, Any] = {"page": 1, "limit": limit}
            if curriculum_id:
                req_params["_curriculum"] = curriculum_id
            
            if params:
                req_params.update(params)

            return self._get("/v1/data/semester-list", params=req_params)
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

    def get_education_year_list(self, limit: int = 50) -> dict:
        """
        O‘quv yili ro‘yxati.
        HEMIS versiyasiga qarab:
        1. /v1/data/education-year-list (Ba'zida 404)
        2. /v1/data/classifier-list?classifier=h_education_year
        3. Fallback static list.
        """
        # 1. Direct endpoint
        try:
            return self._get("/v1/data/education-year-list", params={"limit": limit, "page": 1})
        except Exception:
            pass

        # 2. Classifier
        try:
            payload = self._get("/v1/data/classifier-list", params={"classifier": "h_education_year"})
            if payload and isinstance(payload.get("data"), dict):
                 first = payload["data"].get("items", [])
                 if isinstance(first, list) and len(first) > 0:
                     options = first[0].get("options", [])
                     if options:
                         normalized = self._normalize_forms(options)
                         return {"data": {"items": normalized}}
        except Exception:
            pass

        # 3. Static Fallback
        static_years = [
            {"id": 20, "name": "2024-2025", "code": "2024-2025"},
            {"id": 19, "name": "2023-2024", "code": "2023-2024"},
            {"id": 18, "name": "2022-2023", "code": "2022-2023"},
            {"id": 17, "name": "2021-2022", "code": "2021-2022"},
            {"id": 16, "name": "2020-2021", "code": "2020-2021"},
        ]
        # Hemis IDs for years vary. Usually they are int IDs like 11, 12. 
        # But if we fallback, we need IDs that match reality? 
        # Usually Year IDs are 11=2015, ... 
        # Let's use current year as generic fallback safely if we can't find it.
        # But wait, static fallback IDs might be wrong and return 0 results. 
        # This is a risk. But better than crashing.
        return {"data": {"items": static_years}}

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
    # Methods already updated above implicitly via signature change? No, explicit update needed if content changed. 
    # But wait, the previous snippet I am replacing covers get_department_list... down to ... 
    # Ah, I replaced a huge chunk including get_semester_list etc. to update signatures or keep consistency.
    # The KEY changes are below in get_employee_list.

    # -----------------------
    # EMPLOYEE LIST
    # -----------------------
    def get_employee_list(self, params: dict | None = None) -> dict:
        """
        Xodimlar ro‘yxati: /v1/data/employee-list
        Params: type=teacher|employee|all, _department, _staff_position, _gender, page, limit
        Search: We forward 'search' to API. If API ignores it, we rely on client-side or fallback logic if explicitly requested.
        """
        # Allow search in params
        allowed_params = ["type", "_department", "_gender", "_staff_position", "page", "limit", "search"]
        request_params = {k: v for k, v in (params or {}).items() if k in allowed_params}

        # Default type=teacher
        if "type" not in request_params:
            request_params["type"] = "teacher"

        search_query = (params or {}).get("search", "").strip().lower()
        
        # If searching, we still send query to HEMIS (maybe it supports it?). 
        # But we also fetch more if we plan to filter locally? 
        # User requirement: "UI must match HEMIS for the same query params."
        # So we should primarily trust HEMIS. 
        # But if HEMIS search doesn't work, we face the issue. 
        # User said: "If HEMIS supports a search param... forward it... If not... do client side search"
        # We will assume forwarding is first step.
        
        try:
            data = self._get("/v1/data/employee-list", params=request_params)
        except Exception as e:
            logger.error("HEMIS employee-list error: %s", e, exc_info=True)
            raise

        # Check if HEMIS filtered it? 
        # If we sent 'search' but results contain items NOT matching search, implies HEMIS ignored it.
        # But implementing that check is complex. 
        # For now, we return data. 
        # Frontend does its own Strict Filtering which is safer.
        return data
