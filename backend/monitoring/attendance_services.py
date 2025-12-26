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
    faculties, education_types, education_forms, education_years, semester_types
    """
    client = HemisClient()

    # 1) Faculties (Active Only)
    dept_payload = client.get_department_list(limit=500)
    dept_items = _safe_items(dept_payload)
    faculties: list[dict] = []
    
    for it in dept_items:
        st = (it.get("structureType") or {}).get("code")
        # Active check: Hemis usually returns active but explicit check is good
        is_active = it.get("active", True)
        if str(st) == "11" and is_active is not False:
            faculties.append(_opt(it.get("id"), it.get("name", "Noma'lum")))
    faculties.sort(key=lambda x: x["name"])

    # 2) Education Types & Forms
    education_types: list[dict] = []
    education_forms: list[dict] = []
    
    if faculty_id:
        # Fetch active curricula for this faculty to extract types/forms
        c_params = {
            "limit": 500, 
            "_department": faculty_id
        }
        curr_payload = client.get_curriculum_list(params=c_params)
        curr_items = _safe_items(curr_payload)

        seen_types = set()
        seen_forms = set()

        for c in curr_items:
            # Education Type
            spec = c.get("specialty") or {}
            etype = spec.get("educationType") or {}
            et_id = etype.get("id")
            et_name = etype.get("name")
            if et_id and et_name and et_id not in seen_types:
                seen_types.add(et_id)
                education_types.append(_opt(et_id, et_name))

            # Education Form
            eform = c.get("educationForm") or {}
            ef_id = eform.get("id") or eform.get("code")
            ef_name = eform.get("name")
            if ef_id and ef_name:
                try: 
                    ef_id_int = int(ef_id)
                    if ef_id_int not in seen_forms:
                        seen_forms.add(ef_id_int)
                        education_forms.append(_opt(ef_id_int, ef_name))
                except: pass
        
        education_types.sort(key=lambda x: x["name"])
        # Custom sort for forms
        order = [11, 13, 15, 14, 12, 16]
        education_forms.sort(key=lambda x: order.index(x["id"]) if x["id"] in order else 99)

    # 3) Semesters (Fixed 1-8)
    semesters = [{"id": i, "name": f"{i}-semestr"} for i in range(1, 9)]

    return {
        "faculties": faculties,
        "education_types": education_types,
        "education_forms": education_forms,
        "semesters": semesters,
    }


def get_attendance_stat(
    *,
    faculty_id: int,
    education_type_id: int | None = None,
    education_form_id: int | None = None,
    semester_id: int | None = None,
    page: int = 1,
    limit: int = 50,
) -> dict:
    """
    Faculty-Level Report:
    1. Find groups matching Faculty + EduType + EduForm.
    2. Parallel fetch attendance for these groups (and optional semester).
    3. Aggregate & Filter.
    """
    client = HemisClient()
    
    # 1. Find Curricula first (to get relevant groups)
    c_params = {
        "limit": 500, 
        "_department": faculty_id
    }
    
    curricula_payload = client.get_curriculum_list(params=c_params)
    all_curricula = _safe_items(curricula_payload)
    
    # Filter Curricula by Type & Form
    valid_c_ids = set()
    c_map = {} # id -> {code, specialtyName, formName}
    
    for c in all_curricula:
        # Check Form
        sform = c.get("educationForm") or {}
        sform_id = sform.get("id") or sform.get("code")
        if education_form_id:
            try:
                if int(sform_id or 0) != education_form_id:
                    continue
            except: continue
        
        cid = c.get("id")
        valid_c_ids.add(cid)
        c_map[cid] = {
            "specialty": (c.get("specialty") or {}).get("name", ""),
            "form": sform.get("name", "")
        }

    if not valid_c_ids:
        return {"rows": [], "count": 0}

    # 3. Fetch Groups
    g_params = {
        "limit": 1000,
        "_department": faculty_id,
        "active": True
    }
    g_payload = client.get_group_list(params=g_params)
    all_groups = _safe_items(g_payload)
    
    target_groups = []
    for g in all_groups:
        gcid = g.get("_curriculum")
        if gcid in valid_c_ids:
            target_groups.append(g)

    if not target_groups:
        return {"rows": [], "count": 0}

    # 3. Parallel Fetch Attendance
    import concurrent.futures
    flattened_rows = []
    
    def fetch_group_stat(grp):
        gid = grp['id']
        gname = grp['name']
        cid = grp.get("_curriculum")
        meta = c_map.get(cid, {})
        
        p = {
            "limit": 200, 
            "group_by": "student",
            "_group": gid,
            "_student_status": 11
        }
        # NOTE: We do not pass _semester=semester_id because Hemis expects a specific ID, not '1', '2'.
        # Passing '1' causes empty results. We rely on Hemis returning current/active semester data.

        try:
            res = client.get_attendance_stat(params=p)
            items = _safe_items(res)
            g_rows = []
            for it in items:
                abs_on = int(it.get("absent_on") or it.get("ABSENT_ON") or 0)
                abs_off = int(it.get("absent_off") or it.get("ABSENT_OFF") or 0)
                if abs_on == 0 and abs_off == 0:
                    continue
                
                # Extract student name safely - ROBUST F.I.O
                student_obj = it.get("student") or it.get("_student") or {}
                student_name = None
                
                if isinstance(student_obj, dict):
                    student_name = student_obj.get("full_name") or student_obj.get("fullname") or student_obj.get("name") or student_obj.get("short_name")
                    if not student_name:
                         # Construct from parts
                         lname = student_obj.get("second_name") or student_obj.get("last_name") or student_obj.get("lastname") or ""
                         fname = student_obj.get("first_name") or student_obj.get("firstname") or ""
                         mname = student_obj.get("third_name") or student_obj.get("father_name") or ""
                         parts = [x for x in [lname, fname, mname] if x]
                         if parts:
                              student_name = " ".join(parts)

                # Fallback to current level keys
                if not student_name:
                    student_name = it.get("fullname") or it.get("short_name") or it.get("name")
                
                # Fallback to entity if everything fails
                if not student_name:
                     ent = it.get("_entityname") or it.get("entity") or it.get("_entityName")
                     student_name = _stringify(ent)

                g_rows.append({
                    "entity": student_name,
                    "specialty": meta.get("specialty"),
                    "education_form": meta.get("form"),
                    "group": gname,
                    "semester": str(semester_id) if semester_id else "-",
                    "subjects": int(it.get("subjects") or 0),
                    "lessons": int(it.get("lessons") or 0),
                    "absent_on": abs_on,
                    "absent_off": abs_off,
                    "total_absent": abs_on + abs_off,
                    "total_percent": float(it.get("total_percent") or 0)
                })
            return g_rows
        except:
            return []

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for g in target_groups:
            futures.append(executor.submit(fetch_group_stat, g))
                 
        for f in concurrent.futures.as_completed(futures):
            flattened_rows.extend(f.result())

    # 4. Pagination
    total_count = len(flattened_rows)
    start = (page - 1) * limit
    end = start + limit
    paged_rows = flattened_rows[start:end]

    return {
        "rows": paged_rows,
        "count": total_count,
    }
