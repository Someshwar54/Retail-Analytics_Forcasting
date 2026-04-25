import type { ShapEntry } from "@/lib/api";

interface InsightCardProps {
  entry: ShapEntry;
  type: "booster" | "reducer";
  rank: number;
}

export default function InsightCard({ entry, type, rank }: InsightCardProps) {
  const isBooster = type === "booster";
  const borderColor = isBooster ? "border-emerald-400/20" : "border-rose-400/20";
  const bgGradient = isBooster
    ? "from-emerald-400/10 to-emerald-400/0"
    : "from-rose-400/10 to-rose-400/0";
  const badge = isBooster ? "📈 Booster" : "📉 Reducer";
  const badgeColor = isBooster
    ? "bg-emerald-400/10 text-emerald-400"
    : "bg-rose-400/10 text-rose-400";

  return (
    <div
      className={`glass-card p-5 bg-gradient-to-br ${bgGradient} ${borderColor} animate-fade-in-up`}
      style={{ animationDelay: `${rank * 80}ms` }}
    >
      <div className="flex items-center justify-between mb-3">
        <span className={`text-[10px] font-semibold uppercase tracking-widest px-2.5 py-1 rounded-full ${badgeColor}`}>
          {badge}
        </span>
        <span className="text-xs text-slate-500">#{rank + 1}</span>
      </div>

      <h4 className="text-sm font-semibold text-white mb-2">
        {entry.feature.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
      </h4>

      <p className="text-sm text-slate-300 leading-relaxed mb-3">
        {entry.interpretation}
      </p>

      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span>SHAP: <strong className="text-slate-300">{entry.shap_value > 0 ? "+" : ""}{entry.shap_value.toFixed(4)}</strong></span>
        <span>Impact: <strong className="text-slate-300">{entry.pct_of_avg_revenue}%</strong></span>
      </div>
    </div>
  );
}
