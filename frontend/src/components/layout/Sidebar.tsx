// frontend/src/components/layout/Sidebar.tsx
import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC = () => {
  return (
    <aside
      style={{
        width: "240px",
        borderRight: "1px solid #e5e7eb",
        height: "calc(100vh - 60px)",
        backgroundColor: "#fff",
        padding: "20px 10px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <nav>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          <li>
            <NavLink
              to="/"
              style={({ isActive }) => ({
                display: "block",
                padding: "10px 14px",
                borderRadius: "8px",
                color: isActive ? "#3b82f6" : "#6b7280",
                fontWeight: isActive ? "600" : "500",
                textDecoration: "none",
                backgroundColor: isActive ? "#eff6ff" : "transparent",
                transition: "all 0.2s",
              })}
            >
              Bosh sahifa
            </NavLink>
          </li>

          <li style={{ marginTop: 6 }}>
            <NavLink
              to="/attendance"
              style={({ isActive }) => ({
                display: "block",
                padding: "10px 14px",
                borderRadius: "8px",
                color: isActive ? "#3b82f6" : "#6b7280",
                fontWeight: isActive ? "600" : "500",
                textDecoration: "none",
                backgroundColor: isActive ? "#eff6ff" : "transparent",
                transition: "all 0.2s",
              })}
            >
              Davomat
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
