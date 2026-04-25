"use client";

import { useState, useEffect, useCallback } from "react";
import ChartContainer from "@/components/ChartContainer";
import InsightCard from "@/components/InsightCard";
import LoadingSpinner from "@/components/LoadingSpinner";
import FilterBar from "@/components/FilterBar";
import { fetchExplainability, type ExplainabilityData } from "@/lib/api";

export default function ExplainabilityPage() {
  const [data, setData] = useState<ExplainabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [days, setDays] = useState(30);
  const [store, setStore] = useState("");
  const [category, setCategory] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchExplainability(days, store, category);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Explainability analysis failed");
    } finally {
      setLoading(false);
    }
  }, [days, store, category]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">SHAP Explainability</h1>
          <p className="text-sm text-slate-400 mt-1">
            Model transparency — understand what drives and hurts your revenue
          </p>
        </div>
        
        <FilterBar
          days={days}
          onDaysChange={setDays}
          stores={data?.filters?.stores || []}
          selectedStore={store}
          onStoreChange={setStore}
          categories={data?.filters?.categories || []}
          selectedCategory={category}
          onCategoryChange={setCategory}
        />
      </div>

      {loading && !data ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="glass-card p-8 text-center">
          <p className="text-rose-400 mb-2">{error}</p>
          <button onClick={load} className="text-cyan-400 text-sm underline">Retry</button>
        </div>
      ) : !data ? null : (
        <>
          {/* Summary Banner */}
          <div className="glass-card p-5 bg-gradient-to-r from-cyan-400/5 to-violet-400/5 border-cyan-400/10 animate-fade-in-up">
            <div className="flex items-start gap-4">
              <span className="text-3xl">🧠</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-semibold text-white">AI-Powered Analysis Summary</p>
                  {loading && <div className="text-[10px] text-cyan-400 animate-pulse uppercase tracking-widest font-bold">Refreshing...</div>}
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{data.summary}</p>
              </div>
            </div>
          </div>

          {/* Chart */}
          <ChartContainer chartJson={data.chart} title="Global SHAP Feature Importance" loading={loading} />

          {/* Profit Boosters */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-bold text-emerald-400">📈 Profit Boosters</h2>
              <span className="text-xs text-slate-500 bg-emerald-400/10 px-3 py-1 rounded-full">
                {data.profit_boosters.length} factors
              </span>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              These factors have a positive impact on revenue — leveraging them can increase profitability.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.profit_boosters.map((entry, i) => (
                <InsightCard key={entry.feature} entry={entry} type="booster" rank={i} />
              ))}
            </div>
          </div>

          {/* Profit Reducers */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-bold text-rose-400">📉 Profit Reducers</h2>
              <span className="text-xs text-slate-500 bg-rose-400/10 px-3 py-1 rounded-full">
                {data.profit_reducers.length} factors
              </span>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              These factors negatively impact revenue — addressing them can reduce losses.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.profit_reducers.map((entry, i) => (
                <InsightCard key={entry.feature} entry={entry} type="reducer" rank={i} />
              ))}
            </div>
          </div>

          {/* Methodology Note */}
          <div className="glass-card p-5 text-xs text-slate-500 animate-fade-in-up">
            <p className="font-semibold text-slate-400 mb-2">Methodology</p>
            <p>
              SHAP (SHapley Additive exPlanations) values are computed using a TreeExplainer
              on a LightGBM model trained on transaction data filtered by your selection. Positive mean SHAP values
              indicate features that boost predicted revenue; negative values indicate features
              that reduce it. Interpretations are generated by analyzing the direction and
              magnitude of each feature&apos;s impact relative to the average order value.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
