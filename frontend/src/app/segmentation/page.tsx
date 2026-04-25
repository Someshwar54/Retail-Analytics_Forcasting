"use client";

import { useState, useEffect, useCallback } from "react";
import ChartContainer from "@/components/ChartContainer";
import DataTable from "@/components/DataTable";
import LoadingSpinner from "@/components/LoadingSpinner";
import FilterBar from "@/components/FilterBar";
import { fetchSegments, type SegmentsData } from "@/lib/api";

const CLUSTER_COLORS: Record<string, string> = {
  "Premium Performer": "text-emerald-400",
  "Growth Potential": "text-cyan-400",
  "Stable Average": "text-amber-400",
  Underperformer: "text-rose-400",
};

export default function SegmentationPage() {
  const [data, setData] = useState<SegmentsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nClusters, setNClusters] = useState(4);
  
  // Filter states
  const [days, setDays] = useState(30);
  const [category, setCategory] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSegments(nClusters, days, category);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Segmentation failed");
    } finally {
      setLoading(false);
    }
  }, [nClusters, days, category]);

  useEffect(() => {
    load();
  }, [load]);

  const summaryRows = data?.cluster_summary?.map((c) => ({
    Segment: c.cluster_label,
    Stores: c.store_count,
    "Avg Revenue": Number(c.avg_revenue.toFixed(2)),
    "Avg Rating": Number(c.avg_rating.toFixed(2)),
  })) || [];

  const assignmentRows = data?.store_assignments?.map((s) => ({
    "Store ID": s.store_id,
    Location: s.store_location,
    Segment: s.cluster_label,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Store Segmentation</h1>
          <p className="text-sm text-slate-400 mt-1">K-Means clustering for store performance tiers</p>
        </div>
        
        <FilterBar
          days={days}
          onDaysChange={setDays}
          stores={[]} // No store filter for store clustering
          selectedStore=""
          onStoreChange={() => {}}
          categories={data?.filters?.categories || []}
          selectedCategory={category}
          onCategoryChange={setCategory}
          showStore={false}
        />
      </div>

      {/* Controls */}
      <div className="glass-card p-5 flex flex-wrap items-center gap-6 animate-fade-in-up">
        <div className="flex items-center gap-4">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Number of Clusters
          </label>
          <input
            id="cluster-slider"
            type="range"
            min={2}
            max={8}
            value={nClusters}
            onChange={(e) => setNClusters(Number(e.target.value))}
            className="w-40 h-2 bg-[#1a1d2e] rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-lg font-bold text-violet-400 w-8 text-center">{nClusters}</span>
        </div>

        <button
          id="segment-run-btn"
          onClick={load}
          disabled={loading}
          className="px-6 py-2.5 bg-gradient-to-r from-violet-500 to-rose-500 text-white text-sm font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/20 transition-all disabled:opacity-50"
        >
          {loading ? "Clustering..." : "Run Segmentation"}
        </button>

        <div className="text-xs text-slate-500 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          Strategy: K-Means++ (MinMaxScaler)
        </div>
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
          {/* Scatter Chart */}
          <ChartContainer
            chartJson={data?.segments_chart || null}
            title="Store Performance Clusters"
            loading={loading}
          />

          {/* Cluster Summary Cards */}
          {data?.cluster_summary && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3">🎯 Cluster Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
                {data.cluster_summary.map((c, i) => (
                  <div key={c.cluster_label} className="glass-card p-5 animate-fade-in-up" style={{ animationDelay: `${i * 80}ms` }}>
                    <p className={`text-sm font-bold ${CLUSTER_COLORS[c.cluster_label] || "text-slate-300"} mb-3`}>
                      {c.cluster_label}
                    </p>
                    <div className="space-y-2 text-xs text-slate-400">
                      <div className="flex justify-between">
                        <span>Stores</span>
                        <span className="text-white font-semibold">{c.store_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Revenue</span>
                        <span className="text-white font-semibold">${c.avg_revenue.toFixed(0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Rating</span>
                        <span className="text-white font-semibold">{c.avg_rating.toFixed(1)} ★</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Store Assignments Table */}
          {assignmentRows.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3">📋 Store Assignments</h3>
              <DataTable headers={["Store ID", "Location", "Segment"]} rows={assignmentRows} keyField="Store ID" />
            </div>
          )}
        </>
      )}
    </div>
  );
}
