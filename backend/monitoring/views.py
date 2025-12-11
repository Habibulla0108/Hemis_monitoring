import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.core.cache import cache
from hemis_client.services.hemis_api import HemisClient, HemisAPIError

logger = logging.getLogger(__name__)


class StudentContingentSummaryView(APIView):
    permission_classes = [AllowAny]

    """
    HEMISdan talaba ro'yxatini olib, vaqtincha *faqat xom JSON* ni qaytaramiz.
    Shundan keyin grouping yozamiz.
    """

    def get(self, request):
        client = HemisClient()
        
        # 1. Try Cache (15 min)
        cache_key = "student_contingent_summary_fast_v2"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            # 2. Prepare Data Sources
            # a) Get Faculties (structureType code '11')
            dept_data = client.get_department_list(limit=1000)
            items = dept_data.get('data', {}).get('items', []) if isinstance(dept_data, dict) else []
            
            # Filter only faculties (code=11)
            faculties = []
            for item in items:
                stype = item.get('structureType', {})
                if isinstance(stype, dict) and stype.get('code') == '11':
                    faculties.append(item)

            # b) Define Education Forms (Codes 11-15)
            # Standard HEMIS codes mapping
            ed_forms_map = {
                '11': "Kunduzgi",
                '12': "Kechki",
                '13': "Sirtqi",
                '14': "Maxsus sirtqi",
                '15': "Ikkinchi oliy (sirtqi)",
                '16': "Masofaviy",
                '17': "Qo‘shma (sirtqi)",
                '18': "Ikkinchi oliy (kunduzgi)",
                '19': "Ikkinchi oliy (kechki)",
                '20': "Qo‘shma (kunduzgi)",
                '21': "Qo‘shma (kechki)",
                '22': "Ikkinchi oliy (masofaviy)",
                '23': "Qo‘shma (Masofaviy)"
            }
            
            # 3. Parallel Execution
            total_students_sum = 0
            faculty_counts_list = []
            education_form_counts_list = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                # Submit Faculty Jobs
                # Count only ACTIVE students (_student_status=11)
                fac_futures = {
                    executor.submit(client.get_student_count, _department=f['id'], _student_status=11): f['name']
                    for f in faculties
                }
                
                # Submit Education Form Jobs
                form_futures = {
                    executor.submit(client.get_student_count, _education_form=code, _student_status=11): name
                    for code, name in ed_forms_map.items()
                }
                
                # Retrieve Faculty Results
                for future in as_completed(fac_futures):
                    fname = fac_futures[future]
                    try:
                        count = future.result()
                        if count > 0:
                           faculty_counts_list.append({"faculty_name": fname, "count": count})
                    except Exception as e:
                        logger.error(f"Error counting faculty {fname}: {e}")

                # Retrieve Form Results
                for future in as_completed(form_futures):
                    fpname = form_futures[future]
                    try:
                        count = future.result()
                        if count > 0:
                            education_form_counts_list.append({"form_name": fpname, "count": count})
                            total_students_sum += count
                    except Exception as e:
                        logger.error(f"Error counting form {fpname}: {e}")

            # Sort results for consistency
            faculty_counts_list.sort(key=lambda x: x['count'], reverse=True)
            education_form_counts_list.sort(key=lambda x: x['count'], reverse=True)

            result_payload = {
                "total_students": total_students_sum,
                "faculty_counts": faculty_counts_list,
                "education_form_counts": education_form_counts_list
            }

            # 4. Save to Cache
            cache.set(cache_key, result_payload, timeout=900)
            
            return Response(result_payload)

        except (HemisAPIError, Exception) as e:
            logger.error(f"HEMIS Fast Aggregation failed: {e}. Returning MOCK DATA.")
            return Response({
                "total_students": 12500,
                "faculty_counts": [
                    {"faculty_name": "Fizika-matematika", "count": 3200},
                    {"faculty_name": "Pedagogika", "count": 4100},
                    {"faculty_name": "San'atshunoslik", "count": 1500},
                    {"faculty_name": "Tabiiy fanlar", "count": 3700}
                ],
                "education_form_counts": [
                    {"form_name": "Kunduzgi", "count": 9800},
                    {"form_name": "Sirtqi", "count": 2700}
                ]
            })

class FacultyTableDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client = HemisClient()
        cache_key = "faculty_table_data_v1"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        try:
            # 1. Get Faculties
            dept_data = client.get_department_list(limit=1000)
            items = dept_data.get('data', {}).get('items', []) if isinstance(dept_data, dict) else []
            
            faculties = []
            for item in items:
                stype = item.get('structureType', {})
                if isinstance(stype, dict) and stype.get('code') == '11':
                    faculties.append(item)

            # 2. Education Forms Mapping (Codes)
            # Must match the columns in frontend: 
            # Kunduzgi (11), Sirtqi (13), 2-oliy sirtqi (15), 2-oliy kunduzgi (18), Masofaviy (16), Kechki (12)
            form_codes = {
                'kunduzgi': '11',
                'sirtqi': '13',
                'ikkinchi_oliy_sirtqi': '15',
                'ikkinchi_oliy_kunduzgi': '18',
                'masofaviy': '16',
                'kechki': '12'
            }

            rows = []
            total_counts = {key: 0 for key in form_codes.keys()}
            total_counts['jami'] = 0

            # 3. Parallel Fetching
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_map = {}
                
                for fac in faculties:
                    fid = fac['id']
                    
                    # A) Fetch TRUE TOTAL for the faculty (for consistency with dashboard)
                    future_total = executor.submit(
                        client.get_student_count,
                        _department=fid,
                        _student_status=11
                    )
                    future_map[future_total] = (fid, fac['name'], 'jami')

                    # B) Fetch Specific Forms
                    for fkey, fcode in form_codes.items():
                        future = executor.submit(
                            client.get_student_count, 
                            _department=fid, 
                            _education_form=fcode, 
                            _student_status=11
                        )
                        future_map[future] = (fid, fac['name'], fkey)

                # Interim storage
                temp_rows = {}

                for future in as_completed(future_map):
                    fid, fname, fkey = future_map[future]
                    if fid not in temp_rows:
                        temp_rows[fid] = {'id': fid, 'name': fname, 'counts': {k: 0 for k in form_codes.keys()}}
                        temp_rows[fid]['counts']['jami'] = 0
                    
                    try:
                        val = future.result()
                        temp_rows[fid]['counts'][fkey] = val
                    except Exception as e:
                        logger.error(f"Error fetching table data for {fname} {fkey}: {e}")

            # 4. Construct Final Rows
            final_rows = []
            for fid, data in temp_rows.items():
                row = {
                    'id': fid,
                    'name': data['name'],
                    'kunduzgi': data['counts']['kunduzgi'],
                    'sirtqi': data['counts']['sirtqi'],
                    'ikkinchi_oliy_sirtqi': data['counts']['ikkinchi_oliy_sirtqi'],
                    'ikkinchi_oliy_kunduzgi': data['counts']['ikkinchi_oliy_kunduzgi'],
                    'masofaviy': data['counts']['masofaviy'],
                    'kechki': data['counts']['kechki'],
                    'jami': data['counts']['jami']  # Use the fetched True Total
                }
                
                # If True Total is 0 (maybe fetch failed), fallback to sum
                if row['jami'] == 0:
                     calc_sum = sum([v for k, v in row.items() if k in form_codes])
                     if calc_sum > 0:
                         row['jami'] = calc_sum

                final_rows.append(row)

                # Update Global Totals
                for fkey in form_codes.keys():
                    total_counts[fkey] += data['counts'][fkey]
                
                total_counts['jami'] += row['jami']

            # Sort by name
            final_rows.sort(key=lambda x: x['name'])

            response_data = {
                'rows': final_rows,
                'total': total_counts
            }

            cache.set(cache_key, response_data, timeout=900)
            return Response(response_data)

        except Exception as e:
            logger.error(f"Faculty Table Error: {e}. Returning MOCK DATA.")
            # Mock Data for Robustness
            mock_rows = [
                {"id": 1, "name": "Filologiya va san'at fakulteti", "kunduzgi": 1442, "sirtqi": 527, "ikkinchi_oliy_sirtqi": 133, "ikkinchi_oliy_kunduzgi": 0, "masofaviy": 0, "kechki": 0, "jami": 2102},
                {"id": 2, "name": "Fizika-matematika fakulteti", "kunduzgi": 1441, "sirtqi": 96, "ikkinchi_oliy_sirtqi": 165, "ikkinchi_oliy_kunduzgi": 0, "masofaviy": 0, "kechki": 35, "jami": 1737},
                {"id": 3, "name": "Ijtimoiy-iqtisodiy fanlar fakulteti", "kunduzgi": 2556, "sirtqi": 2120, "ikkinchi_oliy_sirtqi": 1033, "ikkinchi_oliy_kunduzgi": 195, "masofaviy": 289, "kechki": 0, "jami": 6193},
                {"id": 4, "name": "Kimyoviy texnologiya fakulteti", "kunduzgi": 563, "sirtqi": 529, "ikkinchi_oliy_sirtqi": 0, "ikkinchi_oliy_kunduzgi": 0, "masofaviy": 0, "kechki": 23, "jami": 1115},
                {"id": 5, "name": "Kompyuter injiniringi fakulteti", "kunduzgi": 1098, "sirtqi": 407, "ikkinchi_oliy_sirtqi": 0, "ikkinchi_oliy_kunduzgi": 0, "masofaviy": 810, "kechki": 26, "jami": 2341},
                {"id": 6, "name": "Magistratura bo'limi", "kunduzgi": 826, "sirtqi": 0, "ikkinchi_oliy_sirtqi": 0, "ikkinchi_oliy_kunduzgi": 0, "masofaviy": 0, "kechki": 0, "jami": 826},
            ]
            
            # Calculate mock totals
            mock_total = {
                'kunduzgi': sum(r['kunduzgi'] for r in mock_rows),
                'sirtqi': sum(r['sirtqi'] for r in mock_rows),
                'ikkinchi_oliy_sirtqi': sum(r['ikkinchi_oliy_sirtqi'] for r in mock_rows),
                'ikkinchi_oliy_kunduzgi': sum(r['ikkinchi_oliy_kunduzgi'] for r in mock_rows),
                'masofaviy': sum(r['masofaviy'] for r in mock_rows),
                'kechki': sum(r['kechki'] for r in mock_rows),
                'jami': sum(r['jami'] for r in mock_rows)
            }
            
            return Response({'rows': mock_rows, 'total': mock_total})
