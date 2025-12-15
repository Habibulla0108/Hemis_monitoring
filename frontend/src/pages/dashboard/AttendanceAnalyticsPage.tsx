import React, { useEffect, useMemo, useState } from "react";
import {
  getAttendanceOptions,
  getAttendanceStat,
  type AttendanceOptionsResponse,
  type AttendanceRow,
  type SelectOption,
} from "../../api/monitoring";
import "./attendance.css";

type Id = number | "";

const normalizeOptions = (x?: AttendanceOptionsResponse): AttendanceOptionsResponse => ({
  faculties: x?.faculties ?? [],
  education_forms: x?.education_forms ?? [],
  curricula: x?.curricula ?? [],
  groups: x?.groups ?? [],
  semesters: x?.semesters ?? [],
});

const Option = ({ opt }: { opt: SelectOption }) => (
  <option value={String(opt.id)}>{opt.name}</option>
);

const AttendanceAnalyticsPage: React.FC = () => {
  const [opts, setOpts] = useState<AttendanceOptionsResponse>(() => normalizeOptions(undefined));
  const [loadingOpts, setLoadingOpts] = useState(false);

  const [facultyId, setFacultyId] = useState<Id>("");
  const [formId, setFormId] = useState<Id>("");
  const [curriculumId, setCurriculumId] = useState<Id>("");
  const [groupId, setGroupId] = useState<Id>("");
  const [semester, setSemester] = useState<Id>("");

  const [rows, setRows] = useState<AttendanceRow[]>([]);
  const [count, setCount] = useState<number>(0);
  const [loadingStat, setLoadingStat] = useState(false);
  const [error, setError] = useState<string>("");

  const loadOptions = async (params?: {
    faculty_id?: number;
    education_form_id?: number;
    curriculum_id?: number;
  }) => {
    setLoadingOpts(true);
    setError("");
    try {
      const data = await getAttendanceOptions(params);
      setOpts(normalizeOptions(data));
    } catch (e: any) {
      setError(e?.response?.data?.error || e?.message || "Options yuklashda xatolik");
      setOpts(normalizeOptions(undefined));
    } finally {
      setLoadingOpts(false);
    }
  };

  // initial
  useEffect(() => {
    loadOptions();
  }, []);

  // cascade resets
  useEffect(() => {
    setCurriculumId("");
    setGroupId("");
    setSemester("");
    setRows([]);
    setCount(0);
  }, [facultyId, formId]);

  useEffect(() => {
    setGroupId("");
    setRows([]);
    setCount(0);
  }, [curriculumId]);

  // cascade fetch
  useEffect(() => {
    const params = {
      faculty_id: facultyId ? Number(facultyId) : undefined,
      education_form_id: formId ? Number(formId) : undefined,
      curriculum_id: curriculumId ? Number(curriculumId) : undefined,
    };
    loadOptions(params);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [facultyId, formId, curriculumId]);

  const canSubmit = useMemo(() => !!groupId, [groupId]);

  const onSubmit = async () => {
    setError("");
    setRows([]);
    setCount(0);

    if (!groupId) {
      setError("Davomat statistikasi uchun GURUH tanlash shart.");
      return;
    }

    try {
      setLoadingStat(true);
      const res = await getAttendanceStat({
        group_id: Number(groupId),
        semester: semester ? Number(semester) : undefined,
        group_by: "group",
        page: 1,
        limit: 200,
      });
      setRows(res.rows || []);
      setCount(res.count || 0);
    } catch (e: any) {
      setError(e?.response?.data?.error || e?.message || "Stat olishda xatolik");
    } finally {
      setLoadingStat(false);
    }
  };

  return (
    <div className="att-page">
      <div className="att-hero">
        <div>
          <h1>Davomat statistikasi</h1>
          <p>
            Filterlarni tanlang va <b>Ko‘rsatish</b> ni bosing.
          </p>
        </div>
      </div>

      <div className="att-card">
        <div className="att-form-row">
          <div className="att-field">
            <label>FAKULTET</label>
            <select value={String(facultyId)} onChange={(e) => setFacultyId((e.target.value || "") as any)} disabled={loadingOpts}>
              <option value="">Tanlang...</option>
              {opts.faculties.map((f) => (
                <Option key={String(f.id)} opt={f} />
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>TA’LIM SHAKLI</label>
            <select value={String(formId)} onChange={(e) => setFormId((e.target.value || "") as any)} disabled={loadingOpts}>
              <option value="">Tanlang...</option>
              {opts.education_forms.map((f) => (
                <Option key={String(f.id)} opt={f} />
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>O‘QUV REJA</label>
            <select value={String(curriculumId)} onChange={(e) => setCurriculumId((e.target.value || "") as any)} disabled={loadingOpts}>
              <option value="">Tanlang...</option>
              {opts.curricula.map((c) => (
                <Option key={String(c.id)} opt={c} />
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>GURUH</label>
            <select value={String(groupId)} onChange={(e) => setGroupId((e.target.value || "") as any)} disabled={loadingOpts}>
              <option value="">Tanlang...</option>
              {opts.groups.map((g) => (
                <Option key={String(g.id)} opt={g} />
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>SEMESTR</label>
            <select value={String(semester)} onChange={(e) => setSemester((e.target.value || "") as any)} disabled={loadingOpts}>
              <option value="">Tanlang...</option>
              {opts.semesters.map((s) => (
                <Option key={String(s.id)} opt={s} />
              ))}
            </select>
          </div>

          <button className="att-btn" onClick={onSubmit} disabled={!canSubmit || loadingStat} title={!canSubmit ? "Avval GURUH tanlang" : ""}>
            {loadingStat ? "Yuklanmoqda..." : "Ko‘rsatish"}
          </button>
        </div>

        <div className="att-help">
          Davomat statistikasi uchun <b>GURUH</b> tanlash shart (HEMIS attendance-stat shunday ishlaydi).
        </div>
      </div>

      <div className="att-result">
        <div className="att-result-head">
          <h2>Natija</h2>
          <div className="att-muted">Keldi: {count} ta satr</div>
        </div>

        {error ? (
          <div className="att-error">Xatolik: {error}</div>
        ) : rows.length === 0 ? (
          <div className="att-muted">
            Hozircha natija yo‘q. Filter tanlab <b>Ko‘rsatish</b> ni bosing.
          </div>
        ) : (
          <div className="att-table-wrap">
            <table className="att-table">
              <thead>
                <tr>
                  <th>Sana</th>
                  <th>Guruh</th>
                  <th>Talaba</th>
                  <th>Dars</th>
                  <th>ON</th>
                  <th>OFF</th>
                  <th>ON %</th>
                  <th>OFF %</th>
                  <th>Jami %</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r, idx) => (
                  <tr key={idx}>
                    <td>{r.date || "-"}</td>
                    <td>{r.group || "-"}</td>
                    <td>{r.students}</td>
                    <td>{r.lessons}</td>
                    <td>{r.absent_on}</td>
                    <td>{r.absent_off}</td>
                    <td>{Number(r.on_percent || 0).toFixed(1)}</td>
                    <td>{Number(r.off_percent || 0).toFixed(1)}</td>
                    <td>{Number(r.total_percent || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AttendanceAnalyticsPage;
