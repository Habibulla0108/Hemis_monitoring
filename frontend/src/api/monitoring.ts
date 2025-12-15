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

export async function getStudentContingentSummary(): Promise<any> {
  const resp = await http.get("/monitoring/student-contingent/");
  return resp.data;
}

/** ---------------- NEW: ATTENDANCE ---------------- **/

export type SelectOption = { id: number | string; name: string };

export interface AttendanceOptionsResponse {
  faculties: SelectOption[];
  education_forms: SelectOption[];
  curricula: SelectOption[];
  groups: SelectOption[];
  semesters: SelectOption[];
}

export interface AttendanceRow {
  entity: string;
  date: string;
  timestamp: string;
  university: string;
  department: string;
  group: string;
  students: number;
  lessons: number;
  absent_on: number;
  absent_off: number;
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
  education_form_id?: number;
  curriculum_id?: number;
}): Promise<AttendanceOptionsResponse> {
  const resp = await http.get("/monitoring/attendance/options/", { params });
  return resp.data as AttendanceOptionsResponse;
}

export async function getAttendanceStat(params: {
  group_id: number;
  semester?: number;
  group_by?: "group" | "department" | "university";
  page?: number;
  limit?: number;
}): Promise<AttendanceStatResponse> {
  const resp = await http.get("/monitoring/attendance/stat/", { params });
  return resp.data as AttendanceStatResponse;
}