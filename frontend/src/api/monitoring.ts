// src/api/monitoring.ts
import { http } from "./http";

export interface FacultyCount {
  name: string;
  count: number;
}

export interface EducationFormCount {
  name: string;
  count: number;
}

export interface StudentContingentSummary {
  total_students: number;
  faculty_counts: FacultyCount[];
  education_form_counts: EducationFormCount[];
}

export async function getStudentContingentSummary(): Promise<StudentContingentSummary> {
  const res = await http.get<StudentContingentSummary>(
    "/monitoring/student-contingent/"
  );
  return res.data;
}

export interface FacultyTableRow {
  id: number;
  name: string;
  kunduzgi: number;
  sirtqi: number;
  ikkinchi_oliy_sirtqi: number;
  ikkinchi_oliy_kunduzgi: number;
  masofaviy: number;
  kechki: number;
  jami: number;
}

export interface FacultyTableResponse {
  rows: FacultyTableRow[];
  total: {
    kunduzgi: number;
    sirtqi: number;
    ikkinchi_oliy_sirtqi: number;
    ikkinchi_oliy_kunduzgi: number;
    masofaviy: number;
    kechki: number;
    jami: number;
  };
}

export async function getFacultyTableData(): Promise<FacultyTableResponse> {
  const res = await http.get<FacultyTableResponse>(
    "/monitoring/faculty-table/"
  );
  return res.data;
}
