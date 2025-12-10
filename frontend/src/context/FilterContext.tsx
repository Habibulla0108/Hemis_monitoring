// src/context/FilterContext.tsx
import React, { createContext, useContext, useState } from "react";

export interface MonitoringFilters {
  year: number;
  semester: 1 | 2;
  facultyId?: number;
  groupId?: number;
}

interface FilterContextValue {
  filters: MonitoringFilters;
  setFilters: (next: Partial<MonitoringFilters>) => void;
}

const FilterContext = createContext<FilterContextValue | undefined>(undefined);

export const FilterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [filters, setFiltersState] = useState<MonitoringFilters>({
    year: 2024,
    semester: 1,
  });

  const setFilters = (next: Partial<MonitoringFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...next }));
  };

  return (
    <FilterContext.Provider value={{ filters, setFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useMonitoringFilters = () => {
  const ctx = useContext(FilterContext);
  if (!ctx) {
    throw new Error("useMonitoringFilters must be used within FilterProvider");
  }
  return ctx;
};
