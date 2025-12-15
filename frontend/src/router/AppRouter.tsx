// frontend/src/router/AppRouter.tsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "../components/layout/AppLayout";
import OverviewDashboard from "../pages/dashboard/OverviewDashboard";
import AttendanceAnalyticsPage from "../pages/dashboard/AttendanceAnalyticsPage";

const AppRouter: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<OverviewDashboard />} />
        <Route path="/attendance" element={<AttendanceAnalyticsPage />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

export default AppRouter;
