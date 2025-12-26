// frontend/src/api/monitoring.ts
import { http } from "./http";

/** ---------------- EXISTING TYPES (o'zingizniki qoladi) ---------------- **/
export interface EducationFormDto {
  id: number;
  code?: string;
  name: string;
}

export interface StudentMatrixRow {
  faculty_id: number;
  faculty_name: string;
  by_form: Record<string, number>;
  total: number;
}

export interface StudentMatrixResponse {
  faculties: { id: number; name: string }[];
  education_forms: EducationFormDto[];
  rows: StudentMatrixRow[];
  totals: {
    by_form: Record<string, number>;
    grand_total: number;
  };
}

export async function getStudentContingentMatrix(): Promise<StudentMatrixResponse> {
  const resp = await http.get("/monitoring/student-contingent-matrix/");
  return resp.data as StudentMatrixResponse;
}

export interface FacultyTableResponse {
  columns: { id: number | string; name: string }[];
  rows: {
    faculty_id: number;
    faculty_name: string;
    values: Record<string, number>;
    total: number;
  }[];
  totals: {
    by_form: Record<string, number>;
    grand_total: number;
  };
}

export async function getFacultyTableData(): Promise<FacultyTableResponse> {
  const resp = await http.get("/monitoring/faculty-table-data/");
  return resp.data as FacultyTableResponse;
}

export interface StudentContingentSummary {
  total_students: number;
  faculty_counts: { faculty_name: string; count: number }[];
  education_form_counts: { form_name: string; count: number }[];
}

export async function getStudentContingentSummary(): Promise<StudentContingentSummary> {
  const resp = await http.get("/monitoring/student-contingent/");
  return resp.data as StudentContingentSummary;
}

/** ---------------- NEW: ATTENDANCE ---------------- **/

export type SelectOption = { id: number | string; name: string };

export interface AttendanceOptionsResponse {
  faculties: SelectOption[];
  education_types: SelectOption[];
  education_forms: SelectOption[];
  semesters: SelectOption[];
}

// Added Department List
export interface DepartmentItem {
  id: number;
  name: string;
  code?: string;
  parent?: number;
  structureType?: {
    code: string;
    name: string;
  };
}

export interface DepartmentListResponse {
  data: {
    items: DepartmentItem[];
    pagination: {
      totalCount: number;
    };
  };
}


export interface AttendanceRow {
  entity: string;
  specialty?: string;
  education_form?: string;
  date: string;
  timestamp: string;
  university: string;
  department: string;
  group: string;
  semester?: string;
  students: number;
  lessons: number;
  subjects?: number;
  absent_on: number;
  absent_off: number;
  total_absent?: number;
  on_percent: number;
  off_percent: number;
  total_percent: number;
}

export interface AttendanceStatResponse {
  rows: AttendanceRow[];
  count: number;
}

export async function getAttendanceOptions(params?: {
  faculty_id?: number;
}): Promise<AttendanceOptionsResponse> {
  const resp = await http.get("/monitoring/attendance/options/", { params });
  return resp.data as AttendanceOptionsResponse;
}

export async function getAttendanceStat(params: {
  faculty_id: number;
  education_type_id?: number;
  education_form_id?: number;
  semester_id?: number;
  page?: number;
  limit?: number;
}): Promise<AttendanceStatResponse> {
  const resp = await http.get("/monitoring/attendance/stat/", { params });
  return resp.data as AttendanceStatResponse;
}

// -----------------------
// EMPLOYEE LIST
// -----------------------

export interface EmployeeItem {
  id: number;
  full_name: string;
  short_name: string;
  image: string;
  department: {
    id: number;
    name: string;
    code: string;
  };
  staffPosition: {
    id: number;
    name: string;
    code: string;
  };
  employeeStatus: {
    id: number;
    name: string;
    code: string;
  };
  employmentForm: {
    id: number;
    name: string;
    code: string;
  };
  employmentStaff: {
    id: number;
    name: string;
    code: string;
  };
  employee_id_number: string;
  decree_number: string;
  contract_number: string;
  contract_date: number;
  gender: {
    code: string;
    name: string;
  };
  year_of_enter: number;
}

export interface EmployeeListResponse {
  data: {
    items: EmployeeItem[];
    pagination: {
      totalCount: number;
      currentPage: number;
      pageCount: number;
      perPage: number;
    };
  };
}

export async function getEmployeeList(params: {
  type?: "teacher" | "employee" | "all";
  page?: number;
  limit?: number;
  _department?: number;
  _staff_position?: number;
  _gender?: number;
  search?: string;
}): Promise<EmployeeListResponse> {
  const resp = await http.get("/monitoring/employee-list/", { params });
  return resp.data as EmployeeListResponse;
}

export async function getDepartmentList(params?: any): Promise<DepartmentListResponse> {
  const resp = await http.get("/monitoring/department-list/", { params });
  return resp.data as DepartmentListResponse;
}

