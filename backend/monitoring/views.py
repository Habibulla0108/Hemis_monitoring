import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.core.cache import cache
from hemis_client.services.hemis_api import HemisClient

logger = logging.getLogger(__name__)


# Helper for retries
def fetch_count_with_retry(client, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            val = client.get_student_count(**kwargs)
            return val
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Failed to fetch count after {retries} attempts: {kwargs} - {e}")
                return 0
            # small backoff could be added here if needed

class FacultyTableDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client = HemisClient()
        cache_key = "faculty_table_data_optimized_v3"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        try:
            # 1. Get Faculties
            dept_data = client.get_department_list(limit=1000)
            items = dept_data.get('data', {}).get('items', []) if isinstance(dept_data, dict) else []
            
            all_faculties = []
            for item in items:
                stype = item.get('structureType', {})
                if isinstance(stype, dict) and stype.get('code') == '11':
                    all_faculties.append(item)

            # 2. Get Education Forms
            ed_forms_raw = client.get_education_forms()
            all_forms = {}
            for form in ed_forms_raw:
                try:
                    f_id = int(form.get('id', 0))
                    if f_id > 0:
                        all_forms[f_id] = {
                            "name": form.get('name', 'Noma\'lum'),
                            "code": form.get('code')
                        }
                except (ValueError, TypeError):
                    continue

            # Standard Sort Order
            standard_order_names = [
                'Kunduzgi', 'Sirtqi', 'Kechki', 'Masofaviy', 
                'Maxsus sirtqi', 'Ikkinchi oliy (sirtqi)', 
                'Ikkinchi oliy (kunduzgi)', 'Ikkinchi oliy (kechki)', 
                'Qo\'shma (kunduzgi)', 'Qo\'shma (sirtqi)'
            ]

            # 3. OPTIMIZATION PHASE: Filter Active Rows/Columns first
            # We fetch totals for Faculties and Forms to exclude 0-count ones from the matrix query.
            
            # Let's rewrite the execution block to be cleaner for variable access
            active_faculties = []
            active_form_ids = []  # Just IDs
            
            # Use separate Map for Form Totals to track ID
            form_total_counts = {} # id -> count

            with ThreadPoolExecutor(max_workers=10) as executor:
                # A) Faculty Totals
                f_futures = {}
                for f in all_faculties:
                    ft = executor.submit(fetch_count_with_retry, client, department_id=f['id'], student_status_id=11)
                    f_futures[ft] = f

                # B) Form Totals
                form_futures = {}
                for fid in all_forms.keys():
                    ft = executor.submit(fetch_count_with_retry, client, education_form_id=fid, student_status_id=11)
                    form_futures[ft] = fid

                # Collect Faculty Totals
                for ft in as_completed(f_futures):
                    fac = f_futures[ft]
                    c = ft.result()
                    if c > 0:
                         active_faculties.append({'id': fac['id'], 'name': fac.get('name', ''), 'total': c})

                # Collect Form Totals
                for ft in as_completed(form_futures):
                    fid = form_futures[ft]
                    c = ft.result()
                    if c > 0:
                        active_form_ids.append(fid)
                        form_total_counts[fid] = c
            
            # 4. Fetch Intersection Cells (Sparse Matrix)
            # Only for Active Faculty * Active Form
            # Requests = len(active_faculties) * len(active_form_ids)
            # This is much smaller than All * All
            
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
            
            # Re-calculate form totals from matrix to be 100% consistent with table cells
            table_form_totals = {fid: 0 for fid in active_form_ids}
            table_form_totals['other'] = 0 # Track 'Boshqa' column total
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
                
                # Consistency Check: 
                # fac['total'] is the True Total from API.
                # row_sum_breakdown is Sum of Known Forms.
                # If True Total > Sum, we have missing forms (e.g. Master's forms not in our active list).
                
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

            # Columns
            sorted_active_ids = sorted(active_form_ids, key=lambda x: (
                standard_order_names.index(all_forms[x]['name']) 
                if all_forms[x]['name'] in standard_order_names 
                else 999, x
            ))
            
            columns_meta = [
                {'id': form_id, 'name': all_forms[form_id]['name']}
                for form_id in sorted_active_ids
            ]
            
            # Append "Boshqa" column if needed
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

            # Extended cache time for performance
            cache.set(cache_key, response_data, timeout=3600)
            return Response(response_data)

        except Exception as e:
            logger.error(f"Faculty Table Error: {e}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class StudentContingentSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # reuse the logic or cache from FacultyTableDataView for consistency
        cache_key = "faculty_table_data_optimized_v3"
        table_data = cache.get(cache_key)
        
        # If table data is cached, derive summary from it for SPEED and CONSISTENCY
        if table_data:
            return self._derive_response(table_data)
            
        # If not cached, we could trigger the heavy calculation or do a lightweight fallback.
        # But lightweight fallback might be "inconsistent". 
        # Best approach: Trigger the heavy calculation (it's optimized now).
        view = FacultyTableDataView()
        # We can't easily call view.get() directly without a request. 
        # But we can instantiate helper logic.
        # For now, let's just do a fresh 'Fast' fetch for Summary if Table is missing,
        # OR just wait for the user to load the table (which they do on dashboard).
        
        # Actually, SummaryView is usually called FIRST. 
        # Let's perform the "Total" and "Active Faculty/Form" checks here too.
        # It's the same "Phase 1" of the optimization.
        
        try:
            client = HemisClient()
            total_students = client.get_student_count(student_status_id=11)
            
            # We need counts by Faculty and by Form.
            # We can use the same "Active Filter" logic.
            
            # To save code duplication and ensure consistency, we should probably just
            # return the data for the Dashboard charts from the Table API? 
            # Frontend expects specific structure though.
            
            # Let's implement the "Totals Only" fetch here. It's fast (Phases 1-3 only).
            
            # 1. Faculties
            dept_data = client.get_department_list(limit=500)
            items = dept_data.get('data', {}).get('items', []) if isinstance(dept_data, dict) else []
            faculties = [i for i in items if str(i.get('structureType', {}).get('code')) == '11']
            
            # 2. Ed Forms
            ed_forms_raw = client.get_education_forms()
            ed_forms = [f for f in ed_forms_raw if int(f.get('id', 0)) > 0]
            
            faculty_counts = []
            form_counts = []

            with ThreadPoolExecutor(max_workers=10) as executor:
                # Faculty Totals
                future_fac = {
                    executor.submit(fetch_count_with_retry, client, department_id=f['id'], student_status_id=11): f 
                    for f in faculties
                }
                # Form Totals
                future_form = {
                    executor.submit(fetch_count_with_retry, client, education_form_id=f['id'], student_status_id=11): f 
                    for f in ed_forms
                }
                
                for future in as_completed(future_fac):
                    fac = future_fac[future]
                    c = future.result()
                    if c > 0:
                        faculty_counts.append({'name': fac.get('name', ''), 'count': c})
                
                for future in as_completed(future_form):
                    form = future_form[future]
                    c = future.result()
                    if c > 0:
                        form_counts.append({'name': form.get('name', ''), 'count': c})
            
            data = {
                "total_students": total_students,
                "faculty_counts": faculty_counts,
                "education_form_counts": form_counts
            }
            return Response(data)

        except Exception as e:
             return Response({"error": str(e)}, status=500)
    
    def _derive_response(self, table_data):
        # Convert Table Data to Summary Format
        # totals.grand_total -> total_students
        # rows -> faculty_counts
        # totals.by_form -> education_form_counts
        
        try:
            total_students = table_data['totals']['grand_total']
            
            faculty_counts = [
                {'name': r['faculty_name'], 'count': r['total']}
                for r in table_data['rows']
            ]
            
            form_counts = []
            cols_map = {c['id']: c['name'] for c in table_data['columns']}
            for fid_str, count in table_data['totals']['by_form'].items():
                # fid_str is string ID (could be '11' or 'other')
                col_key = int(fid_str) if fid_str.isdigit() else fid_str
                name = cols_map.get(col_key, "Noma'lum")
                form_counts.append({'name': name, 'count': count})
                
            return Response({
                "total_students": total_students,
                "faculty_counts": faculty_counts,
                "education_form_counts": form_counts
            })
        except Exception:
            # If derivation fails, return empty or retry fetching
            pass
            
        return Response({"error": "Data derivation failed"}, status=500)
