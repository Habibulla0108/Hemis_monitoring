import React, { useEffect, useState } from "react";
import {
  getDepartmentList,
  getEmployeeList,
  type DepartmentItem,
  type EmployeeItem,
} from "../../api/monitoring";
import "./attendance.css";

const SearchableSelect = ({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: number | string | null;
  onChange: (val: number | string | "") => void;
  options: { id: number | string; name: string }[];
  placeholder: string;
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const wrapperRef = React.useRef<HTMLDivElement>(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Handle ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    if (isOpen) window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen]);

  // Filter options
  const q = search.trim().toLowerCase();
  const filtered = options.filter((o) => o.name.toLowerCase().includes(q));

  // Find selected label
  const selectedOption = options.find((o) => String(o.id) === String(value));
  const displayLabel = selectedOption ? selectedOption.name : placeholder;

  return (
    <div className="att-select-wrap" ref={wrapperRef} style={{ position: "relative" }}>
      <div
        className="att-select-trigger"
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) setSearch(""); // Reset search on open
        }}
        style={{
          height: "44px",
          borderRadius: "12px",
          border: "1px solid #dbe6f5",
          padding: "0 12px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          cursor: "pointer",
          background: "#fff",
          fontSize: "14px",
        }}
      >
        <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {value ? displayLabel : placeholder}
        </span>
        <span style={{ color: "#64748b", fontSize: "10px" }}>▼</span>
      </div>

      {isOpen && (
        <div
          className="att-select-dropdown"
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            background: "#fff",
            border: "1px solid #dbe6f5",
            borderRadius: "12px",
            marginTop: "4px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            zIndex: 100,
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "8px" }}>
            <input
              autoFocus
              type="text"
              placeholder="Qidirish..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "8px",
                border: "1px solid #dbe6f5",
                outline: "none",
                fontSize: "14px",
                boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ maxHeight: "250px", overflowY: "auto" }}>
            <div
              onClick={() => {
                onChange("");
                setIsOpen(false);
              }}
              style={{
                padding: "8px 12px",
                cursor: "pointer",
                fontSize: "14px",
                borderBottom: "1px solid #f1f5f9",
                color: "#64748b",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f8fafc")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              Barchasi
            </div>
            {filtered.length === 0 ? (
              <div style={{ padding: "12px", textAlign: "center", color: "#94a3b8", fontSize: "13px" }}>
                Topilmadi
              </div>
            ) : (
              filtered.map((opt) => (
                <div
                  key={opt.id}
                  onClick={() => {
                    onChange(opt.id);
                    setIsOpen(false);
                  }}
                  style={{
                    padding: "8px 12px",
                    cursor: "pointer",
                    fontSize: "14px",
                    background: String(value) === String(opt.id) ? "#eff6ff" : "transparent",
                    color: String(value) === String(opt.id) ? "#2563eb" : "#0f172a",
                  }}
                  onMouseEnter={(e) => {
                    if (String(value) !== String(opt.id)) e.currentTarget.style.background = "#f8fafc";
                  }}
                  onMouseLeave={(e) => {
                    if (String(value) !== String(opt.id)) e.currentTarget.style.background = "transparent";
                  }}
                >
                  {opt.name}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const AttendanceAnalyticsPage: React.FC = () => {
  // --------- FILTERS STATE ---------
  const [deptId, setDeptId] = useState<number | "">("");
  const [formCode, setFormCode] = useState<string>("");
  const [statusCode, setStatusCode] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  // --------- OPTIONS STATE ---------
  const [depts, setDepts] = useState<DepartmentItem[]>([]);
  const [forms, setForms] = useState<{ code: string; name: string }[]>([]);
  const [statuses, setStatuses] = useState<{ code: string; name: string }[]>([]);

  // --------- DATA STATE ---------
  const [rawItems, setRawItems] = useState<EmployeeItem[]>([]); // NEW: Store unfiltered data
  const [rows, setRows] = useState<EmployeeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // --------- PAGINATION (Client-side) ---------
  const [page, setPage] = useState(1);
  const limit = 50;

  // 1. Load Departments
  useEffect(() => {
    // 12 = Kafedra structure type code (usually)
    // Check parameters support on server, fallback on client
    getDepartmentList({ active: true, _structure_type: 12, limit: 1000 })
      .then((res) => {
        let items = res.data?.items || [];
        // Client-side fallback filter
        items = items.filter((d: any) => {
          // ensure active
          const isActive = d.active !== false; // assume true if undefined, or check property existence
          // ensure structure type is 12 (Kafedra)
          // Some APIs return structureType object, others _structure_type field
          const sCode = d.structureType?.code || d._structure_type;
          const isKafedra = sCode == 12 || sCode === "12";
          return isActive && isKafedra;
        });
        setDepts(items);
      })
      .catch((err) => console.error("Failed to load departments", err));
  }, []);

  // ========== CRITICAL: RESET DEPENDENT FILTERS ON KAFEDRA CHANGE ==========
  useEffect(() => {
    // When Kafedra changes:
    // 1. Reset filters
    setFormCode("");
    setStatusCode("");
    setSearch("");
    // 2. Reset UI state
    setIsSubmitted(false);
    setPage(1);

    // 3. IMMEDIATELY fetch options/data for the new department
    // This ensures options are fresh even before "Ko'rsatish" is clicked
    if (deptId) {
      fetchAllPages();
    } else {
      // If "Barchasi" selected, also fetch immediately
      fetchAllPages();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deptId]);

  // 1. Normalize Helper
  const normalize = (str: any) => {
    return String(str || "")
      .toLowerCase()
      .trim()
      .replace(/\s+/g, " ");
  };

  // 2. Filter Logic (Strict & Robust) - SINGLE SOURCE OF TRUTH
  const applyFilters = (items: EmployeeItem[]) => {
    let res = items;

    // A) Department Filter (double-check, server should handle this)
    if (deptId) {
      res = res.filter((x) => String(x.department?.id) === String(deptId));
    }

    // B) Employment Form Filter (Mehnat shakli)
    // ONLY check employmentForm.code
    if (formCode) {
      res = res.filter((x) => {
        const fCode = x.employmentForm?.code;
        return fCode && String(fCode) === String(formCode);
      });
    }

    // C) Status Filter
    // Checks "active" boolean if present, else employeeStatus.code
    if (statusCode) {
      res = res.filter((x: any) => {
        // 1. If filtering for "true" (Ishlamoqda) or "false" (Bo'shagan)
        if (statusCode === "true") return x.active === true;
        if (statusCode === "false") return x.active === false;

        // 2. Fallback to normal code match
        const code = x.employeeStatus?.code;
        return code && String(code) === String(statusCode);
      });
    }

    // D) Search Filter (Normalized)
    const q = normalize(search);
    if (q) {
      res = res.filter((x) => {
        const fields = [
          x.full_name,
          x.short_name,
          x.employee_id_number,
        ];
        return fields.some(f => normalize(f).includes(q));
      });
    }

    return res;
  };

  // 3. Fetch ALL Pages for Complete Dataset
  const fetchAllPages = async () => {
    setLoading(true);
    // setOptionsLoading(true);
    setError("");
    setRawItems([]);
    setRows([]);

    try {
      const baseParams: any = {
        type: "teacher",
        limit: 200, // Maximize per page
        page: 1,
      };

      if (deptId) baseParams["_department"] = deptId;
      // Note: We don't send search/form/status to API - we filter client-side
      // This ensures we get complete dataset for building options

      // Fetch first page
      const res1 = await getEmployeeList(baseParams);
      let allItems = res1.data?.items || [];
      const totalCount = res1.data?.pagination?.totalCount || 0;
      const totalPages = Math.ceil(totalCount / 200);

      // Fetch remaining pages in parallel
      if (totalPages > 1) {
        const promises = [];
        for (let p = 2; p <= totalPages; p++) {
          promises.push(getEmployeeList({ ...baseParams, page: p }));
        }
        const results = await Promise.all(promises);
        results.forEach(r => {
          const pageItems = r.data?.items || [];
          allItems = allItems.concat(pageItems);
        });
      }

      // Store raw items
      setRawItems(allItems);

      // Build COMPLETE options from ALL items

      // 1. MEHNAT SHAKLI: Use ONLY employmentForm (Asosiy, O'rindoshlik, etc.)
      const formMap = new Map<string, { code: string; name: string }>();
      allItems.forEach((item: any) => {
        if (item.employmentForm?.code) {
          formMap.set(item.employmentForm.code, {
            code: item.employmentForm.code,
            name: item.employmentForm.name,
          });
        }
      });
      setForms(Array.from(formMap.values()));



      // 2. STATUS: Deduplicate by favoring employmentStatus, fallback to active
      const statusMap = new Map<string, { code: string; name: string }>();
      allItems.forEach((item: any) => {
        // If real status object exists, use it (Granular: "Mehnat ta'tilida", "Ishlamoqda")
        if (item.employeeStatus?.code) {
          statusMap.set(item.employeeStatus.code, {
            code: item.employeeStatus.code,
            name: item.employeeStatus.name,
          });
        }
        // Fallback: If no status object, but has 'active' boolean -> Map to "true"/"false"
        else if (typeof item.active === 'boolean') {
          const code = item.active ? "true" : "false";
          const name = item.active ? "Ishlamoqda" : "Bo‘shagan";
          statusMap.set(code, { code, name });
        }
      });
      setStatuses(Array.from(statusMap.values()));

      // Apply filters to get displayed rows
      const filteredItems = applyFilters(allItems);
      setRows(filteredItems);

    } catch (e: any) {
      console.error(e);
      setError("Ma'lumotlarni yuklashda xatolik yuz berdi.");
    } finally {
      setLoading(false);
      // setOptionsLoading(false);
    }
  };

  // 4. Re-apply filters when filter values change or when submitted
  useEffect(() => {
    // Only update rows if we have data
    if (rawItems.length > 0) {
      const filtered = applyFilters(rawItems);
      setRows(filtered);
      setPage(1);
    }
  }, [formCode, statusCode, search, isSubmitted]); // Add isSubmitted to ensure sync

  // 5. Submit Handler
  const onSubmit = () => {
    setIsSubmitted(true);
    // Data is likely already loaded by dept change, but ensure
    if (rawItems.length === 0) {
      fetchAllPages();
    }
  };

  const [exportLoading, setExportLoading] = useState(false);

  // 5. Export Handler (ALL PAGES)
  const handleExport = async () => {
    if (!isSubmitted || exportLoading) return;

    try {
      setExportLoading(true);

      // 1. Prepare Params for iteration
      const baseParams: any = {
        type: "teacher",
        limit: 200, // Maximize per page
        page: 1,
      };
      if (deptId) baseParams["_department"] = deptId;
      // Note: We don't send search to API to ensure we get broader set and filter locally strictly
      // But if 'search' reduces result set significantly on server, it's good. 
      // User policy: "UI must match HEMIS". We used strict client filter. 
      // Safest: Fetch without search if we trust client filter 100%, OR fetch WITH search and filter again.
      // Let's pass search if present to respect server filtering first.
      if (search) baseParams["search"] = search;

      // 2. Initial Fetch
      const res1 = await getEmployeeList(baseParams);
      let allItems = res1.data?.items || [];
      const totalCount = res1.data?.pagination?.totalCount || 0;
      const totalPages = Math.ceil(totalCount / 200);

      // 3. Fetch Remaining Pages
      if (totalPages > 1) {
        const promises = [];
        for (let p = 2; p <= totalPages; p++) {
          promises.push(getEmployeeList({ ...baseParams, page: p }));
        }
        const results = await Promise.all(promises);
        results.forEach(r => {
          const pageItems = r.data?.items || [];
          allItems = allItems.concat(pageItems);
        });
      }

      // 4. Apply Strict Filters on ALL items
      const finalRows = applyFilters(allItems);

      if (finalRows.length === 0) {
        alert("Eksport qilish uchun ma'lumot topilmadi.");
        return;
      }

      // 5. Generate Excel
      const date = new Date().toISOString().slice(0, 10);
      const deptName = depts.find((d) => d.id == deptId)?.name || "Barchasi";
      const esc = (s: string) => s.replace(/[^a-z0-9а-яqv_ -]/gi, "_");
      const filename = `Kafedra_${esc(deptName)}_Status_${statusCode || "All"}_${date}.xls`;

      const tableHtml = `
        <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
        <head>
          <meta charset="UTF-8">
          <!--[if gte mso 9]>
          <xml>
            <x:ExcelWorkbook>
              <x:ExcelWorksheets>
                <x:ExcelWorksheet>
                  <x:Name>Sheet1</x:Name>
                  <x:WorksheetOptions>
                    <x:DisplayGridlines/>
                  </x:WorksheetOptions>
                </x:ExcelWorksheet>
              </x:ExcelWorksheets>
            </x:ExcelWorkbook>
          </xml>
          <![endif]-->
          <style>
            br { mso-data-placement:same-cell; }
            td, th { border: 1px solid #ddd; padding: 5px; vertical-align: top; }
          </style>
        </head>
        <body>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Status</th>
                <th>Xodim</th>
                <th>Kafedra</th>
                <th>Lavozim</th>
                <th>Stavka</th>
                <th>Buyruq raqami</th>
              </tr>
            </thead>
            <tbody>
              ${finalRows
          .map(
            (r, i) => `
                <tr>
                  <td>${i + 1}</td>
                  <td>${r.employeeStatus?.name || "-"}</td>
                  <td>${r.full_name || ""}</td>
                  <td>${r.department?.name || ""}</td>
                  <td>${r.staffPosition?.name || ""}</td>
                  <td>${r.employmentStaff?.name || r.employmentForm?.name || "-"}</td>
                  <td>${r.decree_number || "-"}</td>
                </tr>`
          )
          .join("")}
            </tbody>
          </table>
        </body>
        </html>
      `;

      // Create Blob and Download
      const blob = new Blob([tableHtml], { type: "application/vnd.ms-excel" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

    } catch (e) {
      console.error("Export failed", e);
      alert("Eksport jarayonida xatolik yuz berdi. Iltimos qayta urinib ko'ring.");
    } finally {
      setExportLoading(false);
    }
  };

  // CLIENT-SIDE PAGINATION SLICE
  const displayedRows = rows.slice((page - 1) * limit, page * limit);

  return (
    <div className="att-page">
      <div className="att-hero">
        <div>
          <h1>Kafedra O‘qituvchilar ro‘yxati</h1>
          <p>
            Kerakli filtrlarni tanlang va <b>Ko‘rsatish</b> tugmasini bosing.
          </p>
        </div>
      </div>

      <div className="att-card">
        <div className="att-form-row">
          <div className="att-field">
            <label>KAFEDRA</label>
            <SearchableSelect
              value={deptId}
              onChange={(val) => setDeptId(val ? Number(val) : "")}
              options={depts.map((d) => ({ id: d.id, name: d.name }))}
              placeholder="Barchasi"
            />
          </div>

          <div className="att-field">
            <label>MEHNAT SHAKLI</label>
            <select
              value={formCode}
              onChange={(e) => setFormCode(e.target.value)}
            >
              <option value="">Barchasi</option>
              {forms.map((f) => (
                <option key={f.code} value={f.code}>
                  {f.name}
                </option>
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>STATUS</label>
            <select
              value={statusCode}
              onChange={(e) => setStatusCode(e.target.value)}
            >
              <option value="">Barchasi</option>
              {statuses.map((s) => (
                <option key={s.code} value={s.code}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="att-field">
            <label>QIDIRISH</label>
            <input
              type="text"
              placeholder="Ism yoki ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="att-input"
              style={{
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                width: "100%",
                boxSizing: "border-box"
              }}
            />
          </div>

          <button className="att-btn" onClick={onSubmit} disabled={loading}>
            {loading ? "Yuklanmoqda..." : "Ko‘rsatish"}
          </button>
        </div>
      </div>

      <div className="att-result">
        <div className="att-result-head">
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <h2>Natija</h2>
            {isSubmitted && rows.length > 0 && (
              <button
                className="att-btn"
                onClick={handleExport}
                disabled={exportLoading}
                style={{
                  height: "32px",
                  fontSize: "13px",
                  background: exportLoading ? "#9ca3af" : "#10b981", // Gray if loading, Green if ready
                  padding: "0 12px",
                  cursor: exportLoading ? "not-allowed" : "pointer",
                }}
              >
                {exportLoading ? "Yuklanmoqda..." : "Excel yuklab olish"}
              </button>
            )}
          </div>
          {isSubmitted && (
            <div className="att-muted">
              Jami yuklangan: {rawItems.length} ta | Ko‘rsatilmoqda: {rows.length} ta
            </div>
          )}
        </div>

        {error && <div className="att-error">{error}</div>}

        <div className="att-table-wrap">
          <table className="att-table">
            <thead>
              <tr>
                <th style={{ width: 40 }}>#</th>
                <th>Status</th>
                <th>Xodim</th>
                <th>Kafedra</th>
                <th>Lavozim</th>
                <th>Stavka</th>
                <th>Buyruq raqami</th>
              </tr>
            </thead>
            <tbody>
              {!isSubmitted ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: 20 }}>
                    Ko‘rsatish tugmasini bosing
                  </td>
                </tr>
              ) : !loading && rows.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: 20 }}>
                    Ma'lumot topilmadi.
                  </td>
                </tr>
              ) : (
                displayedRows.map((r, idx) => (
                  <tr key={r.id || idx}>
                    <td>{(page - 1) * limit + idx + 1}</td>
                    <td>{r.employeeStatus?.name || "-"}</td>
                    <td>{r.full_name}</td>
                    <td>{r.department?.name}</td>
                    <td>{r.staffPosition?.name}</td>
                    <td>{r.employmentStaff?.name || r.employmentForm?.name || "-"}</td>
                    <td>{r.decree_number || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {isSubmitted && rows.length > 0 && (
          <div
            className="att-pagination"
            style={{ marginTop: 20, display: "flex", gap: 10, alignItems: "center" }}
          >
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="att-btn"
              style={{ padding: "5px 10px", fontSize: 14 }}
            >
              Ortga
            </button>
            <span>
              Sahifa {page} / {Math.ceil(rows.length / limit)}
            </span>
            <button
              disabled={page * limit >= rows.length}
              onClick={() => setPage((p) => p + 1)}
              className="att-btn"
              style={{ padding: "5px 10px", fontSize: 14 }}
            >
              Oldinga
            </button>
            <span style={{ marginLeft: "auto", fontWeight: "bold" }}>
              Jami: {rawItems.length} | Filtr: {rows.length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AttendanceAnalyticsPage;
