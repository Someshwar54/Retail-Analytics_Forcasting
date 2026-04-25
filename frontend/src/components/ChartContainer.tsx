"use client";

import { useEffect, useRef, useState } from "react";

interface ChartContainerProps {
  chartJson: string | null;
  title: string;
  loading?: boolean;
  className?: string;
}

const CHART_TYPES = [
  { value: "default", label: "Default" },
  { value: "bar", label: "Bar Graph" },
  { value: "column", label: "Column Chart" },
  { value: "scatter", label: "Scatter Plot" },
  { value: "clustered", label: "Clustered Column" },
  { value: "line", label: "Line Chart" },
  { value: "pie", label: "Pie Chart" },
];

export default function ChartContainer({ chartJson, title, loading = false, className = "" }: ChartContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartType, setChartType] = useState<string>("default");

  useEffect(() => {
    if (!chartJson || !containerRef.current) return;

    import("plotly.js-dist-min").then((Plotly) => {
      try {
        const parsed = JSON.parse(chartJson);
        let data = parsed.data || [];
        let layout = {
          ...(parsed.layout || {}),
          template: "plotly_dark",
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(26,29,46,0.3)",
          font: { color: "#94a3b8", family: "Inter, sans-serif", size: 12 },
          margin: { l: 60, r: 30, t: 40, b: 50 },
          autosize: true,
          xaxis: { ...parsed.layout?.xaxis, gridcolor: "rgba(255,255,255,0.05)" },
          yaxis: { ...parsed.layout?.yaxis, gridcolor: "rgba(255,255,255,0.05)" },
        };

        // Mutate traces based on selected chart type
        if (chartType !== "default") {
          data = data.map((trace: any) => {
            const newTrace = { ...trace };
            
            // Handle specific overrides
            if (chartType === "bar") {
              newTrace.type = "bar";
              newTrace.orientation = "h";
              // Swap x and y if it was a vertical chart originally to keep it horizontal
              if (!trace.orientation || trace.orientation === 'v') {
                newTrace.x = trace.y;
                newTrace.y = trace.x;
              }
            } else if (chartType === "column" || chartType === "clustered") {
              newTrace.type = "bar";
              newTrace.orientation = "v";
              // Swap back if it was horizontal
              if (trace.orientation === 'h') {
                newTrace.x = trace.y;
                newTrace.y = trace.x;
              }
            } else if (chartType === "scatter") {
              newTrace.type = "scatter";
              newTrace.mode = "markers";
            } else if (chartType === "line") {
              newTrace.type = "scatter";
              newTrace.mode = "lines";
            } else if (chartType === "pie") {
              newTrace.type = "pie";
              newTrace.labels = trace.x || trace.labels;
              newTrace.values = trace.y || trace.values;
              delete newTrace.x;
              delete newTrace.y;
            }
            return newTrace;
          });

          if (chartType === "clustered") {
            layout.barmode = "group";
          } else {
            delete layout.barmode;
          }
        }

        const config = { responsive: true, displayModeBar: true, displaylogo: false };
        Plotly.newPlot(containerRef.current!, data, layout, config);
      } catch (e) {
        console.error("Chart render error:", e);
      }
    });

    return () => {
      if (containerRef.current) {
        import("plotly.js-dist-min").then((Plotly) => {
          Plotly.purge(containerRef.current!);
        });
      }
    };
  }, [chartJson, chartType]); // Re-run effect when chartType changes

  if (loading) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <h3 className="text-sm font-semibold text-slate-300 mb-4">{title}</h3>
        <div className="h-[380px] rounded-xl animate-shimmer" />
      </div>
    );
  }

  return (
    <div className={`glass-card p-6 animate-fade-in-up ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300">{title}</h3>
        <select
          value={chartType}
          onChange={(e) => setChartType(e.target.value)}
          className="bg-[#1a1d2e] border border-white/10 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:border-cyan-400/40"
        >
          {CHART_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>
      <div ref={containerRef} className="w-full h-[380px]" />
    </div>
  );
}
