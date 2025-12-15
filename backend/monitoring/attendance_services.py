import logging
from typing import Any

from hemis_client.services.hemis_api import HemisClient

logger = logging.getLogger(__name__)


def _safe_items(payload: Any) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            return items
    if isinstance(data, list):
        return data
    return []


def _opt(item_id: Any, name: str) -> dict:
    return {"id": item_id, "name": name}


def _stringify(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    if isinstance(v, dict):
        for k in ("name", "title", "code"):
            if k in v and v[k]:
                return str(v[k])
        return str(v)
    return str(v)


def get_attendance_filter_options(
    *,
    faculty_id: int | None = None,
    education_form_id: int | None = None,
    curriculum_id: int | None = None,
) -> dict:
    """
    Frontend filter option’lari:
    faculties, education_forms, curricula, groups, semesters
    """
    client = HemisClient()

    # 1) Faculties
    dept_payload = client.get_department_list(limit=1000)
    dept_items = _safe_items(dept_payload)
    faculties: list[dict] = []
    for it in dept_items:
        st = (it.get("structureType") or {}).get("code")
        if str(st) == "11":
            faculties.append(_opt(it.get("id"), it.get("name", "Noma'lum")))
    faculties.sort(key=lambda x: x["name"])

    # 2) Education forms (siz bergan ro'yxatga mos filtr)
    forms_raw = client.get_education_forms()
    order = [11, 13, 15, 14, 12, 16, 20, 21, 19, 18, 17, 22, 23]
    allowed_ids = set(order)

    education_forms: list[dict] = []
    for f in forms_raw:
        try:
            fid = int(f.get("id"))
        except Exception:
            continue
        if fid in allowed_ids:
            education_forms.append(_opt(fid, f.get("name", "Noma'lum")))
    education_forms.sort(key=lambda x: order.index(x["id"]) if x["id"] in allowed_ids else 999)

    # 3) Curricula
    curricula: list[dict] = []
    try:
        cur_params: dict[str, Any] = {"limit": 200}
        if faculty_id is not None:
            cur_params["_department"] = faculty_id
        if education_form_id is not None:
            cur_params["_education_form"] = education_form_id

        cur_payload = client.get_curriculum_list(params=cur_params)
        for it in _safe_items(cur_payload):
            cid = it.get("id")
            name = it.get("name") or it.get("code") or f"Curriculum {cid}"
            curricula.append(_opt(cid, str(name)))
        curricula.sort(key=lambda x: x["name"])
    except Exception as e:
        logger.warning("curriculum-list fetch failed: %s", e)

    # 4) Groups
    groups: list[dict] = []
    try:
        g_params: dict[str, Any] = {"limit": 200}
        if curriculum_id is not None:
            g_params["_curriculum"] = curriculum_id
        if faculty_id is not None:
            g_params["_department"] = faculty_id
        if education_form_id is not None:
            g_params["_education_form"] = education_form_id

        g_payload = client.get_group_list(params=g_params)
        for it in _safe_items(g_payload):
            gid = it.get("id")
            name = it.get("name") or it.get("code") or f"Group {gid}"
            groups.append(_opt(gid, str(name)))
        groups.sort(key=lambda x: x["name"])
    except Exception as e:
        logger.warning("group-list fetch failed: %s", e)

    # 5) Semesters (fallback: 1..12)
    semesters: list[dict] = []
    try:
        sem_payload = client.get_semester_list(params={"limit": 50})
        for it in _safe_items(sem_payload):
            sid = it.get("id") or it.get("code")
            name = it.get("name") or str(sid)
            semesters.append(_opt(int(sid), str(name)))
        semesters.sort(key=lambda x: x["id"])
    except Exception:
        semesters = [{"id": i, "name": str(i)} for i in range(1, 13)]

    return {
        "faculties": faculties,
        "education_forms": education_forms,
        "curricula": curricula,
        "groups": groups,
        "semesters": semesters,
    }


def get_attendance_stat(
    *,
    group_id: int,
    semester: int | None = None,
    group_by: str = "group",
    page: int = 1,
    limit: int = 200,
) -> dict:
    """
    HEMIS: GET /v1/data/attendance-stat
    """
    client = HemisClient()

    params: dict[str, Any] = {
        "page": page,
        "limit": limit,
        "group_by": group_by,   # group / department / university
        "_group": group_id,     # HEMIS shuni talab qiladi
    }
    if semester is not None:
        params["_semester"] = semester

    payload = client.get_attendance_stat(params=params)
    items = _safe_items(payload)

    rows: list[dict] = []
    for it in items:
        rows.append({
            "entity": _stringify(it.get("_entityname") or it.get("entity") or it.get("_entityName")),
            "date": _stringify(it.get("date") or it.get("DATE")),
            "timestamp": _stringify(it.get("timestamp") or it.get("TIMESTAMP")),
            "university": _stringify(it.get("university") or it.get("UNIVERSITY")),
            "department": _stringify(it.get("department") or it.get("DEPARTMENT")),
            "group": _stringify(it.get("group") or it.get("GROUP")),

            # HEMIS raw fields:
            "students": int(it.get("students") or it.get("STUDENTS") or 0),
            "lessons": int(it.get("lessons") or it.get("LESSONS") or 0),

            # ⚠️ bu maydonlarni hozircha "ON/OFF" deb chiqaryapmiz (Kelgan/Kelmagan deb noto‘g‘ri bo‘lib qolmasin)
            "absent_on": int(it.get("absent_on") or it.get("ABSENT_ON") or 0),
            "absent_off": int(it.get("absent_off") or it.get("ABSENT_OFF") or 0),

            "on_percent": float(it.get("on_percent") or it.get("ON_PERCENT") or 0),
            "off_percent": float(it.get("off_percent") or it.get("OFF_PERCENT") or 0),
            "total_percent": float(it.get("total_percent") or it.get("TOTAL_PERCENT") or 0),
        })

    return {
        "rows": rows,
        "count": len(rows),
    }
