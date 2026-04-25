const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

/* ── Overview ─────────────────────────────────────────────── */
export interface OverviewData {
  status: string;
  kpis: {
    total_revenue: number;
    transaction_count: number;
    avg_order_value: number;
    store_count: number;
    product_count: number;
  };
  revenue_trend: { date: string; revenue: number }[];
  top_stores: { store_location: string; revenue: number }[];
  top_categories: { category: string; revenue: number }[];
  filters: { stores: string[]; categories: string[] };
}

export function fetchOverview(
  days = 30,
  store?: string,
  category?: string
): Promise<OverviewData> {
  const params = new URLSearchParams({ days: String(days) });
  if (store) params.set("store", store);
  if (category) params.set("category", category);
  return fetchJson(`${API_BASE}/overview/?${params}`);
}

/* ── Forecast ─────────────────────────────────────────────── */
export interface ForecastData {
  status: string;
  summary?: string;
  forecast_chart: string;
  predictions_head: { ds: string; yhat: number; yhat_lower: number; yhat_upper: number }[];
  filters: { stores: string[]; categories: string[] };
}

export function fetchForecast(
  steps = 30,
  store?: string,
  category?: string
): Promise<ForecastData> {
  const params = new URLSearchParams({ steps: String(steps) });
  if (store) params.set("store", store);
  if (category) params.set("category", category);
  return fetchJson(`${API_BASE}/forecast/?${params}`);
}

/* ── Drivers ──────────────────────────────────────────────── */
export interface DriversData {
  status: string;
  drivers_chart: string;
  global_importance: { Feature: string; SHAP_Importance: number }[];
  filters: { stores: string[]; categories: string[] };
}

export function fetchDrivers(
  days = 30,
  store?: string,
  category?: string
): Promise<DriversData> {
  const params = new URLSearchParams({ days: String(days) });
  if (store) params.set("store", store);
  if (category) params.set("category", category);
  return fetchJson(`${API_BASE}/drivers/?${params}`);
}

/* ── Segments ─────────────────────────────────────────────── */
export interface SegmentsData {
  status: string;
  segments_chart: string;
  cluster_summary: {
    cluster_label: string;
    store_count: number;
    avg_revenue: number;
    avg_rating: number;
  }[];
  store_assignments: {
    store_id: number;
    store_location: string;
    cluster_id: number;
    cluster_label: string;
  }[];
  filters: { stores: string[]; categories: string[] };
}

export function fetchSegments(
  nClusters = 4,
  days = 30,
  category?: string
): Promise<SegmentsData> {
  const params = new URLSearchParams({ 
    n_clusters: String(nClusters),
    days: String(days)
  });
  if (category) params.set("category", category);
  return fetchJson(`${API_BASE}/segments/?${params}`);
}

/* ── Explainability ───────────────────────────────────────── */
export interface ShapEntry {
  feature: string;
  shap_value: number;
  abs_importance: number;
  pct_of_avg_revenue: number;
  interpretation: string;
}

export interface ExplainabilityData {
  status: string;
  chart: string;
  profit_boosters: ShapEntry[];
  profit_reducers: ShapEntry[];
  summary: string;
  filters: { stores: string[]; categories: string[] };
}

export function fetchExplainability(
  days = 30,
  store?: string,
  category?: string
): Promise<ExplainabilityData> {
  const params = new URLSearchParams({ days: String(days) });
  if (store) params.set("store", store);
  if (category) params.set("category", category);
  return fetchJson(`${API_BASE}/explainability/?${params}`);
}
