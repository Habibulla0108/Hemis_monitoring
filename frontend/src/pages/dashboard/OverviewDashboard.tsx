import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { getStudentContingentSummary } from "../../api/monitoring";
import FacultyEducationTable from "./FacultyEducationTable";
import "./OverviewDashboard.css";

// --- Types ---
type FacultyStat = { name: string; count: number };
type EdFormStat = { name: string; count: number };

interface MonitoringData {
  total_students: number;
  faculty_counts: FacultyStat[];
  education_form_counts: EdFormStat[];
}

// --- Colors & Helpers ---
// --- Colors & Helpers ---
const COLORS = [
  "#4361EE", // Bright Blue
  "#F72585", // Pink
  "#3A0CA3", // Deep Purple
  "#4CC9F0", // Cyan
  "#06D6A0", // Green
  "#FFD166", // Yellow-Orange
  "#EF476F", // Red-Pink
  "#7209B7", // Purple
  "#118AB2", // Teal
  "#073B4C", // Dark Blue
  "#FF9F1C", // Orange
  "#2EC4B6", // Turquoise
];

const getEduFormColor = (_name: string, index: number): string => {
  return COLORS[index % COLORS.length];
};

const formatNumber = (num: number) => num.toLocaleString("uz-UZ");

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: 'rgba(0,0,0,0.15) 0px 4px 12px',
        padding: '10px',
        fontSize: '14px',
        border: 'none',
        zIndex: 50
      }}>
        <p style={{ margin: 0, fontWeight: 600, color: '#333' }}>{label || data.name}</p>
        <p style={{ margin: 0, fontWeight: 700, color: '#000' }}>
          {data.value ? formatNumber(data.value) : 0}
        </p>
      </div>
    );
  }
  return null;
};

const OverviewDashboard: React.FC = () => {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res: any = await getStudentContingentSummary();

        // Runtime Data Mapping (Safety Fix)
        // Backend might send 'faculty_name' or 'form_name' instead of 'name'
        const safeData: MonitoringData = {
          total_students: res.total_students || 0,
          faculty_counts: (res.faculty_counts || []).map((item: any) => ({
            name: item.name || item.faculty_name || "Noma'lum",
            count: item.count || 0
          })),
          education_form_counts: (res.education_form_counts || []).map((item: any) => ({
            name: item.name || item.form_name || "Noma'lum",
            count: item.count || 0
          }))
        };

        setData(safeData);
      } catch (err: unknown) {
        console.error("Failed to load dashboard data:", err);
        if (axios.isAxiosError(err)) {
          setError(err.message);
        } else {
          setError("Noma'lum xatolik yuz berdi");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="hm-state-container">
        <div className="hm-spinner"></div>
        <p>Yuklanmoqda...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="hm-state-container">
        <div style={{ color: '#ef4444', fontWeight: 600 }}>Xatolik: {error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="hm-state-container">
        <p>Ma'lumot topilmadi.</p>
      </div>
    );
  }

  const totalFacultyStudents = data.faculty_counts.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <div className="hm-dashboard-container">
      {/* Header Card */}
      <div className="hm-header-card">
        <h1 className="hm-page-title">BOSH SAHIFA</h1>
        <p className="hm-page-desc">
          Bosh sahifada diagramma ko‘rinishida statistikalardan foydalanishingiz mumkin
        </p>
      </div>

      {/* Charts Grid */}
      <div className="hm-stats-grid">

        {/* Left Panel: Faculty Bar Chart */}
        <div className="hm-chart-panel">
          <div className="hm-panel-header">
            <h3 className="hm-panel-title">FAKULTETLAR KESIMIDA TALABALAR SONI</h3>
            <div className="hm-panel-total">
              {formatNumber(totalFacultyStudents)}
            </div>
          </div>
          <div className="hm-chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.faculty_counts}
                margin={{ top: 20, right: 30, left: 80, bottom: 120 }}
                barSize={40}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis
                  dataKey="name"
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={120}
                  tick={{ fontSize: 13, fill: '#333', fontWeight: 600 }}
                  tickMargin={10}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
                <Bar
                  dataKey="count"
                  fill="#2f6bff"
                  radius={[6, 6, 0, 0]}
                  name="Talabalar soni"
                  activeBar={{ fill: '#1d4ed8' }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Panel: Edu Form Pie Chart */}
        <div className="hm-chart-panel">
          <div className="hm-panel-header">
            <h3 className="hm-panel-title">TAʼLIM SHAKLI KESIMIDA TALABALAR SONI</h3>
          </div>

          {/* Custom Legend Above Chart */}
          <div className="hm-custom-legend">
            {data.education_form_counts.map((item, index) => (
              <div key={item.name} className="hm-legend-item">
                <span
                  className="hm-legend-dot"
                  style={{ backgroundColor: getEduFormColor(item.name, index) }}
                ></span>
                <span>{item.name}</span>
              </div>
            ))}
          </div>

          <div className="hm-chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                <Pie
                  data={data.education_form_counts}
                  cx="50%"
                  cy="50%"
                  innerRadius="55%"
                  outerRadius="80%"
                  paddingAngle={4}
                  dataKey="count"
                  nameKey="name"
                  stroke="none"
                >
                  {data.education_form_counts.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getEduFormColor(entry.name, index)} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>


      </div>

      {/* Integration of the new Faculty Table Component */}
      <FacultyEducationTable />
    </div>
  );
};

export default OverviewDashboard;
