"use client";

import { useState, useEffect, useCallback } from "react";
import ChartContainer from "@/components/ChartContainer";
import DataTable from "@/components/DataTable";
import LoadingSpinner from "@/components/LoadingSpinner";
import FilterBar from "@/components/FilterBar";
import { fetchDrivers, type DriversData } from "@/lib/api";

export default function DriversPage() {
  const [data, setData] = useState<DriversData | null>(null);
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
      const result = await fetchDrivers(days, store, category);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Driver analysis failed");
    } finally {
      setLoading(false);
    }
  }, [days, store, category]);

  useEffect(() => {
    load();
  }, [load]);

  const importanceRows = data?.global_importance?.map((item, i) => ({
    Rank: i + 1,
    Feature: item.Feature.replace(/_/g, " "),
    "SHAP Importance": Number(item.SHAP_Importance.toFixed(4)),
    "% Contribution":
      data.global_importance.length > 0
        ? Number(
            (
              (item.SHAP_Importance /
                data.global_importance.reduce((s, x) => s + x.SHAP_Importance, 0)) *
              100
            ).toFixed(1)
          )
        : 0,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Sales Driver Analysis</h1>
          <p className="text-sm text-slate-400 mt-1">LightGBM + SHAP — identifying the strongest revenue drivers</p>
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

      {/* Strategy badge */}
      <div className="glass-card p-4 flex items-center gap-4 animate-fade-in-up">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400/20 to-amber-400/5 flex items-center justify-center text-lg">
          ⚡
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-white">Strategy: LightGBM Gradient Boosting</p>
          <p className="text-xs text-slate-400">500 boost rounds • RMSE objective • SHAP TreeExplainer</p>
        </div>
        {loading && <div className="text-xs text-cyan-400 animate-pulse">Analyzing...</div>}
      </div>

      {loading && !data ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="glass-card p-8 text-center">
          <p className="text-rose-400 mb-2">{error}</p>
          <button onClick={load} className="text-cyan-400 text-sm underline">Retry</button>
        </div>
      ) : (
        <>
          <ChartContainer
            chartJson={data?.drivers_chart || null}
            title="SHAP Feature Importance (Global)"
            loading={loading}
          />

          {importanceRows.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3">📊 Feature Ranking</h3>
              <DataTable
                headers={["Rank", "Feature", "SHAP Importance", "% Contribution"]}
                rows={importanceRows}
                keyField="Feature"
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
