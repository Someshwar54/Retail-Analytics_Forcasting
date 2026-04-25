interface FilterBarProps {
  days: number;
  onDaysChange: (d: number) => void;
  stores: string[];
  selectedStore: string;
  onStoreChange: (s: string) => void;
  categories: string[];
  selectedCategory: string;
  onCategoryChange: (c: string) => void;
  /** Hide the Days dropdown (default: true) */
  showDays?: boolean;
  /** Hide the Store dropdown (default: true) */
  showStore?: boolean;
  /** Hide the Category dropdown (default: true) */
  showCategory?: boolean;
}

const DAY_OPTIONS = [
  { value: 0, label: "All Time" },
  { value: 7, label: "Last 7 days" },
  { value: 30, label: "Last 30 days" },
  { value: 90, label: "Last 90 days" },
  { value: 365, label: "Last 1 year" },
];

export default function FilterBar({
  days,
  onDaysChange,
  stores,
  selectedStore,
  onStoreChange,
  categories,
  selectedCategory,
  onCategoryChange,
  showDays = true,
  showStore = true,
  showCategory = true,
}: FilterBarProps) {
  const selectClasses =
    "bg-[#1a1d2e]/80 border border-white/10 text-slate-300 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:border-cyan-400/40 transition-colors cursor-pointer";

  return (
    <div className="flex flex-wrap items-center gap-3 animate-fade-in-up">
      <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Filters
      </label>

      {/* Days */}
      {showDays && (
        <select
          id="filter-days"
          value={days}
          onChange={(e) => onDaysChange(Number(e.target.value))}
          className={selectClasses}
        >
          {DAY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      )}

      {/* Store */}
      {showStore && (
        <select
          id="filter-store"
          value={selectedStore}
          onChange={(e) => onStoreChange(e.target.value)}
          className={selectClasses}
        >
          <option value="">All Stores</option>
          {stores.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      )}

      {/* Category */}
      {showCategory && (
        <select
          id="filter-category"
          value={selectedCategory}
          onChange={(e) => onCategoryChange(e.target.value)}
          className={selectClasses}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
