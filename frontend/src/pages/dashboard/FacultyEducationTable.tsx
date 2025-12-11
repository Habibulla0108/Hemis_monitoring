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
                            <th>KUNDUZGI</th>
                            <th>SIRTQI</th>
                            <th>IKKINCHI OLIY (SIRTQI)</th>
                            <th>IKKINCHI OLIY (KUNDUZGI)</th>
                            <th>MASOFAVIY</th>
                            <th>KECHKI</th>
                            <th>JAMI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.rows.map((row, index) => (
                            <tr key={row.id}>
                                <td>{index + 1}</td>
                                <td className="text-left" style={{ fontWeight: 600 }}>{row.name}</td>
                                <td>{row.kunduzgi}</td>
                                <td>{row.sirtqi}</td>
                                <td>{row.ikkinchi_oliy_sirtqi}</td>
                                <td>{row.ikkinchi_oliy_kunduzgi}</td>
                                <td>{row.masofaviy}</td>
                                <td>{row.kechki}</td>
                                <td style={{ fontWeight: 800 }}>{row.jami}</td>
                            </tr>
                        ))}
                        {/* Total Row */}
                        <tr className="hm-table-footer">
                            <td colSpan={2} style={{ textAlign: "right", paddingRight: "20px" }}>JAMI</td>
                            <td>{data.total.kunduzgi}</td>
                            <td>{data.total.sirtqi}</td>
                            <td>{data.total.ikkinchi_oliy_sirtqi}</td>
                            <td>{data.total.ikkinchi_oliy_kunduzgi}</td>
                            <td>{data.total.masofaviy}</td>
                            <td>{data.total.kechki}</td>
                            <td>{data.total.jami}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FacultyEducationTable;
