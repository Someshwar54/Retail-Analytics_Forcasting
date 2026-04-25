"use client";

import { useState, useEffect, useCallback } from "react";
import ChartContainer from "@/components/ChartContainer";
import DataTable from "@/components/DataTable";
import LoadingSpinner from "@/components/LoadingSpinner";
import FilterBar from "@/components/FilterBar";
import { fetchForecast, type ForecastData } from "@/lib/api";

export default function ForecastPage() {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState(30);
  
  // Filter states
  const [days, setDays] = useState(0); // 0 = all time
  const [store, setStore] = useState("");
  const [category, setCategory] = useState("");

  const runForecast = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // In the backend, we don't have a 'days' param for forecast yet, 
      // but let's assume we want to filter the training data.
      // For now, API only takes steps, store, category.
      const result = await fetchForecast(steps, store, category);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Forecast failed");
    } finally {
      setLoading(false);
    }
  }, [steps, store, category]);

  // Run forecast on initial mount and when filters change
  useEffect(() => {
    runForecast();
  }, [runForecast]);

  const predictions = data?.predictions_head?.map((p) => ({
    Date: new Date(p.ds).toLocaleDateString(),
    Predicted: Math.round(p.yhat),
    Lower: Math.round(p.yhat_lower),
    Upper: Math.round(p.yhat_upper),
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Time-Series Forecasting</h1>
          <p className="text-sm text-slate-400 mt-1">Prophet-based revenue prediction with confidence intervals</p>
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
          showDays={false}
        />
      </div>

      {/* Forecast Controls */}
      <div className="glass-card p-5 flex flex-wrap items-center gap-6 animate-fade-in-up">
        <div className="flex items-center gap-4">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Forecast Horizon
          </label>
          <input
            id="forecast-slider"
            type="range"
            min={7}
            max={90}
            value={steps}
            onChange={(e) => setSteps(Number(e.target.value))}
            className="w-48 h-2 bg-[#1a1d2e] rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-lg font-bold text-cyan-400 w-16 text-center">{steps}d</span>
        </div>

        <button
          id="forecast-run-btn"
          onClick={runForecast}
          disabled={loading}
          className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-violet-500 text-white text-sm font-semibold rounded-xl hover:shadow-lg hover:shadow-cyan-500/20 transition-all disabled:opacity-50 disabled:cursor-wait"
        >
          {loading ? "Training Model..." : "Update Forecast"}
        </button>

        <div className="text-xs text-slate-500 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Strategy: Prophet (Additive)
        </div>
      </div>

      {/* Results */}
      {loading && !data ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="glass-card p-8 text-center">
          <p className="text-rose-400 mb-2">Error: {error}</p>
          <button onClick={runForecast} className="text-cyan-400 text-sm underline">
            Retry
          </button>
        </div>
      ) : (
        <>
          {data?.summary && (
            <div className="glass-card p-6 border-l-4 border-l-cyan-400 bg-gradient-to-r from-cyan-950/20 to-transparent">
              <h3 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
                <span>🤖</span> AI Forecast Insight
              </h3>
              <p className="text-slate-200 leading-relaxed text-sm">
                {data.summary}
              </p>
            </div>
          )}

          <ChartContainer
            chartJson={data?.forecast_chart || null}
            title="Revenue Forecast with Confidence Bands"
            loading={loading}
          />

          {/* Predictions Table */}
          {predictions.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3">📋 Latest Predictions</h3>
              <DataTable headers={["Date", "Predicted", "Lower", "Upper"]} rows={predictions} keyField="Date" />
            </div>
          )}
        </>
      )}
    </div>
  );
}
