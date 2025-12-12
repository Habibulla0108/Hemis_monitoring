import React, { useEffect, useState } from "react";
import axios from "axios";
import { getFacultyTableData, type FacultyTableResponse } from "../../api/monitoring";
import "./FacultyEducationTable.css";

const FacultyEducationTable: React.FC = () => {
    const [data, setData] = useState<FacultyTableResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const res = await getFacultyTableData();
                setData(res);
            } catch (err: unknown) {
                console.error("Failed to load table data:", err);
                if (axios.isAxiosError(err)) {
                    setError(err.message);
                } else {
                    setError("Ma'lumot yuklashda xatolik");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const formatNumber = (num: number) => num.toLocaleString("uz-UZ");

    if (loading) {
        return (
            <div className="hm-table-card">
                <h3 className="hm-table-title">FAKULTETLAR VA TA’LIM SHAKLI KESIMIDA TALABALAR SONI</h3>
                <div className="hm-table-loading">
                    <div className="hm-spinner"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="hm-table-card">
                <div style={{ color: "red", fontWeight: "bold" }}>Xatolik: {error}</div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="hm-table-card">
            <h3 className="hm-table-title">FAKULTETLAR VA TA’LIM SHAKLI KESIMIDA TALABALAR SONI</h3>
            <div className="hm-table-container">
                <table className="hm-faculty-table">
                    <thead>
                        <tr>
                            <th style={{ width: "40px" }}>№</th>
                            <th style={{ textAlign: "left" }}>FAKULTET</th>
                            {data.columns.map((col) => (
                                <th key={col.id}>{col.name.toUpperCase()}</th>
                            ))}
                            <th>JAMI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.rows.map((row, index) => (
                            <tr key={row.faculty_id}>
                                <td>{index + 1}</td>
                                <td className="text-left" style={{ fontWeight: 600 }}>{row.faculty_name}</td>
                                {data.columns.map((col) => (
                                    <td key={col.id}>
                                        {row.values[col.id] ? formatNumber(row.values[col.id]) : 0}
                                    </td>
                                ))}
                                <td style={{ fontWeight: 800 }}>{formatNumber(row.total)}</td>
                            </tr>
                        ))}
                        {/* Total Row */}
                        <tr className="hm-table-footer">
                            <td colSpan={2} style={{ textAlign: "right", paddingRight: "20px" }}>JAMI</td>
                            {data.columns.map((col) => (
                                <td key={col.id}>
                                    {data.totals.by_form[col.id] ? formatNumber(data.totals.by_form[col.id]) : 0}
                                </td>
                            ))}
                            <td>{formatNumber(data.totals.grand_total)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FacultyEducationTable;
