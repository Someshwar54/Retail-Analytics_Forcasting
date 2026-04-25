"use client";

import { useState, useEffect, useCallback } from "react";
import KpiCard from "@/components/KpiCard";
import FilterBar from "@/components/FilterBar";
import ChartContainer from "@/components/ChartContainer";
import DataTable from "@/components/DataTable";
import LoadingSpinner from "@/components/LoadingSpinner";
import { fetchOverview, type OverviewData } from "@/lib/api";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [days, setDays] = useState(0);
  const [store, setStore] = useState("");
  const [category, setCategory] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchOverview(days, store || undefined, category || undefined);
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load overview data");
    } finally {
      setLoading(false);
    }
  }, [days, store, category]);

  useEffect(() => {
    load();
  }, [load]);

  // Build a simple Plotly chart JSON for the revenue trend
  const trendChartJson = data
    ? JSON.stringify({
        data: [
          {
            x: data.revenue_trend.map((r) => r.date),
            y: data.revenue_trend.map((r) => r.revenue),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            fillcolor: "rgba(6,182,212,0.1)",
            line: { color: "#06b6d4", width: 2.5 },
            name: "Daily Revenue",
          },
        ],
        layout: {
          title: "",
          xaxis: { title: "Date" },
          yaxis: { title: "Revenue ($)" },
          hovermode: "x unified",
        },
      })
    : null;

  if (loading && !data) return <LoadingSpinner />;
  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="glass-card p-8 text-center max-w-md">
          <p className="text-rose-400 text-lg font-semibold mb-2">Error</p>
          <p className="text-slate-400 text-sm">{error}</p>
          <button
            onClick={load}
            className="mt-4 px-5 py-2 bg-cyan-500/20 text-cyan-400 rounded-xl text-sm hover:bg-cyan-500/30 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard Overview</h1>
          <p className="text-sm text-slate-400 mt-1">Real-time retail analytics at a glance</p>
        </div>
        <div className="text-xs text-slate-500 bg-[#1a1d2e]/60 px-4 py-2 rounded-xl border border-white/[0.06]">
          {loading ? "Updating..." : `Showing last ${days} days`}
        </div>
      </div>

      {/* Filters */}
      <FilterBar
        days={days}
        onDaysChange={setDays}
        stores={data.filters.stores}
        selectedStore={store}
        onStoreChange={setStore}
        categories={data.filters.categories}
        selectedCategory={category}
        onCategoryChange={setCategory}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4 stagger-children">
        <KpiCard label="Total Revenue" value={Math.round(data.kpis.total_revenue)} prefix="$" icon="💰" color="cyan" delay={0} />
        <KpiCard label="Transactions" value={data.kpis.transaction_count} icon="🧾" color="violet" delay={80} />
        <KpiCard label="Avg Order Value" value={Math.round(data.kpis.avg_order_value)} prefix="$" icon="📦" color="emerald" delay={160} />
        <KpiCard label="Stores" value={data.kpis.store_count} icon="🏪" color="amber" delay={240} />
        <KpiCard label="Products" value={data.kpis.product_count} icon="🏷️" color="rose" delay={320} />
      </div>

      {/* Revenue Trend Chart */}
      <ChartContainer chartJson={trendChartJson} title="Revenue Trend" loading={loading} />

      {/* Top Stores & Categories Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">🏆 Top Stores by Revenue</h3>
          <DataTable
            headers={["store_location", "revenue"]}
            rows={data.top_stores}
            keyField="store_location"
          />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">📂 Top Categories by Revenue</h3>
          <DataTable
            headers={["category", "revenue"]}
            rows={data.top_categories}
            keyField="category"
          />
        </div>
      </div>
    </div>
  );
}
