import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  getStudentContingentSummary,
  StudentContingentSummary,
} from "../api/monitoring";

const HemisMonitoringTest: React.FC = () => {
  const [data, setData] = useState<StudentContingentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getStudentContingentSummary()
      .then((res) => {
        setData(res);
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

  if (loading) {
    return <p>Yuklanmoqda...</p>;
  }

  if (error) {
    return <p style={{ color: "red" }}>Xatolik: {error}</p>;
  }

  if (!data) {
    return <p>Ma'lumot topilmadi.</p>;
  }

  return (
    <div style={{ padding: "32px" }}>
      <h1>HEMIS Monitoring – test</h1>

      <p>Umumiy talabalar soni: {data.total_students}</p>
      <p>Fakultetlar soni: {data.faculty_counts.length}</p>
      <p>Ta'lim shakllari soni: {data.education_form_counts.length}</p>

      <h3>Fakultetlar kesimi:</h3>
      <ul>
        {data.faculty_counts.map((f) => (
          <li key={f.faculty_name}>
            {f.faculty_name}: <b>{f.count}</b>
          </li>
        ))}
      </ul>

      <h3>Ta'lim shakllari kesimi:</h3>
      <ul>
        {data.education_form_counts.map((e) => (
          <li key={e.form_name}>
            {e.form_name}: <b>{e.count}</b>
          </li>
        ))}
      </ul>

      <h3>Raw JSON:</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default HemisMonitoringTest;