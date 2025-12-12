// frontend/src/api/monitoring.ts
import { http } from "./http";

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
  columns: { id: number; name: string }[];
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
