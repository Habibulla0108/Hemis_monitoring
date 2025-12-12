import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.cache import cache
from hemis_client.services.hemis_api import HemisClient

logger = logging.getLogger(__name__)

def fetch_count_with_retry(client, **kwargs):
    """
    Helper to fetch student count with retries.
    """
    retries = 3
    for attempt in range(retries):
        try:
            return client.get_student_count(**kwargs)
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Failed to fetch count after {retries} attempts: {kwargs} - {e}")
                return 0

def get_faculty_table_data() -> dict:
    """
    Fetches and aggregates data for the Faculty x Education Form table.
    Implements Sparse Matrix strategy and 'Boshqa' column consistency check.
    Returns:
        dict: { 'columns': [...], 'rows': [...], 'totals': {...} }
    """
    cache_key = "faculty_table_data_optimized_v4"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    client = HemisClient()

    # 1. Get Faculties
    dept_data = client.get_department_list(limit=1000)
    items = dept_data.get('data', {}).get('items', []) if isinstance(dept_data, dict) else []
    all_faculties = [item for item in items if item.get('structureType', {}).get('code') == '11']

    # 2. Get Education Forms
    ed_forms_raw = client.get_education_forms()
    all_forms = {}
    for form in ed_forms_raw:
        try:
            f_id = int(form.get('id', 0))
            if f_id > 0:
                all_forms[f_id] = {
                    "name": form.get('name', "Noma'lum"),
                    "code": form.get('code')
                }
        except (ValueError, TypeError):
            continue

    standard_order_names = [
        'Kunduzgi', 'Sirtqi', 'Kechki', 'Masofaviy', 
        'Maxsus sirtqi', 'Ikkinchi oliy (sirtqi)', 
        'Ikkinchi oliy (kunduzgi)', 'Ikkinchi oliy (kechki)', 
        'Qo\'shma (kunduzgi)', 'Qo\'shma (sirtqi)'
    ]

    # 3. OPTIMIZATION: Filter Active Rows/Columns first
    active_faculties = [] 
    active_form_ids = []
    form_total_counts = {} 

    with ThreadPoolExecutor(max_workers=10) as executor:
        # A) Faculty Totals
        f_futures = {
            executor.submit(fetch_count_with_retry, client, department_id=f['id'], student_status_id=11): f 
            for f in all_faculties
        }
        # B) Form Totals
        form_futures = {
            executor.submit(fetch_count_with_retry, client, education_form_id=fid, student_status_id=11): fid 
            for fid in all_forms.keys()
        }

        for ft in as_completed(f_futures):
            fac = f_futures[ft]
            c = ft.result()
            if c > 0:
                active_faculties.append({'id': fac['id'], 'name': fac.get('name', ''), 'total': c})

        for ft in as_completed(form_futures):
            fid = form_futures[ft]
            c = ft.result()
            if c > 0:
                active_form_ids.append(fid)
                form_total_counts[fid] = c

    # 4. Fetch Intersection Cells (Sparse Matrix)
    matrix_data = {} # (fac_id, form_id) -> count

    with ThreadPoolExecutor(max_workers=10) as executor:
        cell_futures = {}
        for fac in active_faculties:
            for fid in active_form_ids:
                ft = executor.submit(
                    fetch_count_with_retry, 
                    client, 
                    department_id=fac['id'], 
                    education_form_id=fid, 
                    student_status_id=11
                )
                cell_futures[ft] = (fac['id'], fid)
        
        for ft in as_completed(cell_futures):
            fac_id, form_id = cell_futures[ft]
            val = ft.result()
            if val > 0:
                matrix_data[(fac_id, form_id)] = val

    # 5. Build Response
    final_rows = []
    grand_total = 0
    table_form_totals = {fid: 0 for fid in active_form_ids}
    table_form_totals['other'] = 0 
    has_other_data = False

    for fac in active_faculties:
        fid = fac['id']
        row_vals = {}
        row_sum_breakdown = 0
        
        for form_id in active_form_ids:
            val = matrix_data.get((fid, form_id), 0)
            if val > 0:
                row_vals[str(form_id)] = val
                row_sum_breakdown += val
                table_form_totals[form_id] += val
        
        # Consistency Check: Total - Sum(Forms) = Boshqa
        api_total = fac.get('total', 0)
        diff = api_total - row_sum_breakdown
        
        if diff > 0:
            row_vals['other'] = diff
            has_other_data = True
            table_form_totals['other'] += diff
            row_sum = api_total
        else:
            row_sum = max(api_total, row_sum_breakdown)
        
        if row_sum > 0:
            final_rows.append({
                'faculty_id': fid,
                'faculty_name': fac['name'],
                'values': row_vals,
                'total': row_sum
            })
            grand_total += row_sum

    final_rows.sort(key=lambda x: x['faculty_name'])

    # Columns Meta
    sorted_active_ids = sorted(active_form_ids, key=lambda x: (
        standard_order_names.index(all_forms[x]['name']) 
        if all_forms[x]['name'] in standard_order_names 
        else 999, x
    ))
    
    columns_meta = [
        {'id': form_id, 'name': all_forms[form_id]['name']}
        for form_id in sorted_active_ids
    ]
    
    if has_other_data:
        columns_meta.append({'id': 'other', 'name': 'Boshqa'})

    totals_by_form = {
        str(form_id): table_form_totals[form_id] 
        for form_id in sorted_active_ids
    }
    if has_other_data:
        totals_by_form['other'] = table_form_totals['other']

    response_data = {
        'columns': columns_meta,
        'rows': final_rows,
        'totals': {
            'by_form': totals_by_form,
            'grand_total': grand_total
        }
    }
    
    cache.set(cache_key, response_data, timeout=3600)
    return response_data

def get_dashboard_summary() -> dict:
    """
    Returns summary data for dashboard charts (Total, Faculty Bar, Form Pie).
    Tries to reuse valid cached table data for 100% consistency.
    """
    # 1. Try to derive from Table Data if cached
    cached_table = cache.get("faculty_table_data_optimized_v3")
    if cached_table:
        return _derive_summary_from_table(cached_table)
    
    # 2. Trigger fresh fetch (which caches)
    table_data = get_faculty_table_data()
    return _derive_summary_from_table(table_data)

def _derive_summary_from_table(table_data: dict) -> dict:
    """ Helper to transform Table structure to Summary structure """
    total_students = table_data['totals']['grand_total']
    
    faculty_counts = [
        {'name': r['faculty_name'], 'count': r['total']}
        for r in table_data['rows']
    ]
    
    form_counts = []
    cols_map = {c['id']: c['name'] for c in table_data['columns']}
    
    for fid_str, count in table_data['totals']['by_form'].items():
        # Handle 'other' key safely
        if fid_str == 'other':
            name = "Boshqa"
        elif fid_str.isdigit():
            name = cols_map.get(int(fid_str), "Noma'lum")
        else:
            name = cols_map.get(fid_str, "Noma'lum")
            
        form_counts.append({'name': name, 'count': count})
        
    return {
        "total_students": total_students,
        "faculty_counts": faculty_counts,
        "education_form_counts": form_counts
    }
