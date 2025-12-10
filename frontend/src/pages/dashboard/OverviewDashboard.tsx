import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  getStudentContingentSummary,
} from "../../api/monitoring";
import type { StudentContingentSummary } from "../../api/monitoring";

const OverviewDashboard: React.FC = () => {
  // 👉 mana shu qatorda summary + setSummary e'lon qilinadi
  const [summary, setSummary] = useState<StudentContingentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getStudentContingentSummary()
      .then((res) => {
        setSummary(res);            // ✅ endi mavjud
      })
      .catch((err) => {
        console.error("Contingent load error:", err);
        if (axios.isAxiosError(err)) {
          setError(err.message);
        } else {
          setError("Noma'lum xatolik");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Yuklanmoqda...</p>;
  if (error) return <p style={{ color: "red" }}>Xatolik: {error}</p>;
  if (!summary) return <p>Ma'lumot topilmadi.</p>;

  return (
    <div style={{ padding: 32 }}>
      <h1>HEMIS Monitoring – test</h1>
      <p>Umumiy talabalar soni: {summary.total_students}</p>
      <p>Fakultetlar soni: {summary.faculty_counts.length}</p>
      <p>Ta'lim shakllari soni: {summary.education_form_counts.length}</p>

      <h3>Fakultetlar kesimi:</h3>
      <ul>
        {summary.faculty_counts.map((f) => (
          <li key={f.faculty_name}>
            {f.faculty_name}: <b>{f.count}</b>
          </li>
        ))}
      </ul>

      <h3>Ta'lim shakllari kesimi:</h3>
      <ul>
        {summary.education_form_counts.map((e) => (
          <li key={e.form_name}>
            {e.form_name}: <b>{e.count}</b>
          </li>
        ))}
      </ul>

      <h3>Raw JSON:</h3>
      <pre>{JSON.stringify(summary, null, 2)}</pre>
    </div>
  );
};

export default OverviewDashboard;
