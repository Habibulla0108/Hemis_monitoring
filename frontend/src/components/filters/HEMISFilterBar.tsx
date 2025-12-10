// src/components/filters/HEMISFilterBar.tsx
import { useMonitoringFilters } from "../../context/FilterContext";

const HEMISFilterBar: React.FC = () => {
  const { filters, setFilters } = useMonitoringFilters();

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl bg-white/80 p-3 shadow-sm">
      <select
        value={filters.year}
        onChange={(e) => setFilters({ year: Number(e.target.value) })}
        className="rounded-lg border px-2 py-1 text-sm"
      >
        <option value={2023}>2023/2024</option>
        <option value={2024}>2024/2025</option>
      </select>

      <select
        value={filters.semester}
        onChange={(e) =>
          setFilters({ semester: Number(e.target.value) as 1 | 2 })
        }
        className="rounded-lg border px-2 py-1 text-sm"
      >
        <option value={1}>1-semestr</option>
        <option value={2}>2-semestr</option>
      </select>

      {/* Keyin fakultet va guruh select’larini backenddan kelgan ro‘yxat bilan to‘ldiramiz */}
    </div>
  );
};

export default HEMISFilterBar;
