// src/api/monitoring.ts
import { http } from "./http";

export interface FacultyCount {
  faculty_name: string;
  count: number;
}

export interface EducationFormCount {
  form_name: string;
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
