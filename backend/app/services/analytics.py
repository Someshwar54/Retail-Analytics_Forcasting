import logging
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ..db.models.retail import Transaction, Product, Store
from ..ml.data_processor import DataProcessor
from ..ml.strategies.forecasters.prophet_model import ProphetForecaster
from ..ml.strategies.boosters.lgbm_model import LightGBMDriverAnalyzer
from ..ml.strategies.clusterers.kmeans_model import KMeansClusterer
from ..ml.explainability.shap_engine import ShapExplainer
from ..visualization.charts import InteractiveCharts

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Orchestration Layer for high-end retail analytics.
    This service connects Database queries with ML Strategies and Visualizations.
    Includes an in-memory cache to maintain dashboard responsiveness.
    """
    _cache: Dict[str, Dict[str, Any]] = {}
    CACHE_DURATION = timedelta(minutes=10)

    def __init__(self, db: Session):
        self.db = db

    def _get_cached_result(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() - entry['timestamp'] < self.CACHE_DURATION:
                logger.info(f"Returning cached result for: {key}")
                return entry['data']
        return None

    def _set_cached_result(self, key: str, data: Any):
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }

    def _get_available_filters(self) -> dict:
        """Helper to fetch all unique stores and categories for frontend dropdowns."""
        all_stores = [r[0] for r in self.db.query(Store.store_location).distinct().all()]
        all_categories = [r[0] for r in self.db.query(Product.category).distinct().all()]
        return {
            "stores": sorted(all_stores),
            "categories": sorted(all_categories),
        }

    def generate_revenue_forecast(self, steps: int = 30, store: str | None = None, category: str | None = None) -> dict:
        """
        Orchestrates extracting historical revenue, training Prophet, and visualizing the forecast.
        Now supports store and category level filtering.
        """
        cache_key = f"forecast_{steps}_{store}_{category}"
        cached = self._get_cached_result(cache_key)
        if cached: return cached
        
        # Fetch historical data with filters
        query = self.db.query(
            Transaction.timestamp, 
            Transaction.revenue, 
            Transaction.holiday_flag
        ).join(Store).join(Product).order_by(Transaction.timestamp)
        
        if store:
            query = query.filter(Store.store_location == store)
        if category:
            query = query.filter(Product.category == category)
        
        # Load into pandas
        df = pd.read_sql(query.statement, self.db.bind)
        
        if df.empty:
            return {"status": "error", "message": "No historical data found for the selected filters."}

        # We need daily revenue for forecasting
        df['ds'] = pd.to_datetime(df['timestamp']).dt.date
        daily_revenue = df.groupby('ds').agg({'revenue': 'sum', 'holiday_flag': 'max'}).reset_index()
        
        # Strategy Implementation
        forecaster = ProphetForecaster()
        forecaster.train(daily_revenue[['ds']], daily_revenue['revenue'], exogenous_features=['holiday_flag'])
        
        logger.info("Predicting future.")
        future_dates = forecaster.model.make_future_dataframe(periods=steps)
        future_dates['holiday_flag'] = False
        
        forecast_df = forecaster.predict(steps, exogenous_features=future_dates[['ds', 'holiday_flag']])
        
        # Generate NLP Summary with Comparison
        future_forecast = forecast_df.tail(steps)
        total_revenue = future_forecast['yhat'].sum()
        start_val = future_forecast['yhat'].iloc[0]
        end_val = future_forecast['yhat'].iloc[-1]
        
        trend = "upward" if end_val > start_val else "downward" if end_val < start_val else "stable"
        max_day_row = future_forecast.loc[future_forecast['yhat'].idxmax()]
        max_day = max_day_row['ds'].strftime('%b %d, %Y')
        
        # Comparative Logic: Compare filter to overall average
        from sqlalchemy import func
        global_avg_q = self.db.query(func.avg(Transaction.revenue)).scalar() or 1
        filter_avg = total_revenue / steps if steps > 0 else 0
        diff_pct = ((filter_avg - global_avg_q) / global_avg_q) * 100
        
        comp_str = ""
        if store or category:
            cat_name = f"'{category}'" if category else "all"
            prefix = f"In the {cat_name} category"
            loc = f" at {store}" if store else " across all stores"
            relation = "higher" if diff_pct > 0 else "lower"
            comp_str = f" {prefix}{loc}, predicted performance is {abs(diff_pct):.1f}% {relation} than the global store average."

        reasons = []
        if 'weekly' in future_forecast.columns:
            weekly_max = future_forecast['weekly'].max()
            weekly_min = future_forecast['weekly'].min()
            if weekly_max - weekly_min > (total_revenue / steps) * 0.05:
                 reasons.append("strong weekly seasonality patterns")
        if 'extra_regressors_additive' in future_forecast.columns and future_forecast['extra_regressors_additive'].sum() > 0:
            reasons.append("upcoming holidays")
            
        reason_str = f" This {trend} trend is primarily driven by {', '.join(reasons)}." if reasons else ""
        
        summary_text = (
            f"Over the next {steps} days, revenue is expected to show an {trend} trend, "
            f"generating an estimated total of ${total_revenue:,.0f}. {comp_str}"
            f" The highest daily revenue is predicted to occur on {max_day}.{reason_str}"
        )
        
        # Generate Interactive Chart
        chart_json = InteractiveCharts.plot_forecast(
            historical_data=daily_revenue,
            forecast_data=forecast_df,
            date_col='ds',
            value_col='revenue'
        )
        
        res = {
            "status": "success",
            "summary": summary_text,
            "forecast_chart": chart_json,
            "predictions_head": forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail().to_dict(orient='records'),
            "filters": self._get_available_filters()
        }
        self._set_cached_result(cache_key, res)
        return res

    def analyze_sales_drivers(self, days: int = 0, store: str | None = None, category: str | None = None) -> dict:
        """
        Orchestrates extracting transaction data, training LightGBM, and generating SHAP importance charts.
        Now supports time, store, and category filters.
        """
        cache_key = f"drivers_{days}_{store}_{category}"
        cached = self._get_cached_result(cache_key)
        if cached: return cached
        
        from sqlalchemy import func
        cutoff = (self.db.query(func.max(Transaction.timestamp)).scalar() - timedelta(days=days)) if (days > 0) else None

        query = self.db.query(
            Transaction.discount_percentage,
            Transaction.customer_type,
            Transaction.payment_mode,
            Transaction.promotion_applied,
            Transaction.holiday_flag,
            Transaction.revenue,
            Store.store_rating,
            Product.category
        ).join(Store).join(Product)

        if cutoff:
            query = query.filter(Transaction.timestamp >= cutoff)
        if store:
            query = query.filter(Store.store_location == store)
        if category:
            query = query.filter(Product.category == category)

        df = pd.read_sql(query.statement, self.db.bind)

        if df.empty:
            return {"status": "error", "message": "No data found for the selected filters."}

        # Use the memory-efficient DataProcessor
        processor = DataProcessor(df)
        processed_df = processor.data

        # One-hot encode categoricals
        cat_cols = processed_df.select_dtypes(include=['object', 'category']).columns.tolist()
        processed_df = pd.get_dummies(processed_df, columns=cat_cols, drop_first=True)

        # Convert bool columns to int
        bool_cols = processed_df.select_dtypes(include=['bool']).columns
        processed_df[bool_cols] = processed_df[bool_cols].astype(int)

        X = processed_df.drop(columns=['revenue'])
        y = processed_df['revenue']

        # Train LightGBM Booster
        booster = LightGBMDriverAnalyzer()
        booster.train(X, y)

        # Integrate SHAP Explainability Engine
        explainer = ShapExplainer(booster.model)
        importance_df = explainer.get_global_importance(X)

        # Generate Interactive Chart
        chart_json = InteractiveCharts.plot_feature_importance(
            importance_df=importance_df,
            feature_col='Feature',
            importance_val_col='SHAP_Importance'
        )

        res = {
            "status": "success",
            "drivers_chart": chart_json,
            "global_importance": importance_df.head(10).to_dict(orient='records'),
            "filters": self._get_available_filters()
        }
        self._set_cached_result(cache_key, res)
        return res

    def segment_stores(self, n_clusters: int = 4, days: int = 0, category: str | None = None) -> dict:
        """
        Aggregates per-store metrics, clusters them with KMeans.
        Now supports time window and category filtering.
        """
        cache_key = f"segmentation_{n_clusters}_{days}_{category}"
        cached = self._get_cached_result(cache_key)
        if cached: return cached
        
        from sqlalchemy import func
        cutoff = (self.db.query(func.max(Transaction.timestamp)).scalar() - timedelta(days=days)) if (days > 0) else None

        query = self.db.query(
            Store.id.label("store_id"),
            Store.store_location,
            Store.store_rating,
            Transaction.revenue,
            Transaction.discount_percentage,
        ).join(Transaction).join(Product)

        if cutoff:
            query = query.filter(Transaction.timestamp >= cutoff)
        if category:
            query = query.filter(Product.category == category)

        df = pd.read_sql(query.statement, self.db.bind)

        if df.empty:
            return {"status": "error", "message": "No data found for segmentation"}

        # Aggregate to one row per store
        agg_df = (
            df.groupby(["store_id", "store_location"])
            .agg(
                avg_revenue=("revenue", "mean"),
                total_revenue=("revenue", "sum"),
                store_rating=("store_rating", "mean"),
                avg_discount=("discount_percentage", "mean"),
                transaction_count=("revenue", "count"),
            )
            .reset_index()
        )

        feature_cols = ["avg_revenue", "store_rating", "avg_discount", "transaction_count"]
        X_cluster = agg_df[feature_cols].fillna(0)

        # Fit KMeans
        clusterer = KMeansClusterer(n_clusters=n_clusters)
        clusterer.fit(X_cluster)
        result_df = clusterer.predict_with_labels(X_cluster)

        agg_df["cluster_id"] = result_df["cluster_id"]
        agg_df["cluster_label"] = result_df["cluster_label"]

        # Build interactive scatter chart
        chart_json = InteractiveCharts.plot_clusters(
            df=agg_df,
            x_col="avg_revenue",
            y_col="store_rating",
            cluster_col="cluster_label",
        )

        # Cluster-level statistics summary
        cluster_summary = (
            agg_df.groupby("cluster_label")
            .agg(
                store_count=("store_id", "count"),
                avg_revenue=("avg_revenue", "mean"),
                avg_rating=("store_rating", "mean"),
            )
            .reset_index()
            .to_dict(orient="records")
        )

        res = {
            "status": "success",
            "segments_chart": chart_json,
            "cluster_summary": cluster_summary,
            "store_assignments": agg_df[
                ["store_id", "store_location", "cluster_id", "cluster_label"]
            ].to_dict(orient="records"),
            "filters": self._get_available_filters()
        }
        self._set_cached_result(cache_key, res)
        return res


    # ------------------------------------------------------------------
    # Overview KPI Stats (with multi-filter support)
    # ------------------------------------------------------------------

    def get_overview_stats(
        self,
        days: int = 30,
        store: str | None = None,
        category: str | None = None,
    ) -> dict:
        """
        Computes KPI summary statistics with optional filters for time window,
        store location, and product category.
        """
        cache_key = f"overview_{days}_{store}_{category}"
        cached = self._get_cached_result(cache_key)
        if cached: return cached
        from sqlalchemy import func
        from datetime import datetime, timedelta

        # days=0 means "all time" — no cutoff
        max_date = self.db.query(func.max(Transaction.timestamp)).scalar()
        cutoff = (max_date - timedelta(days=days)) if (days > 0 and max_date) else None

        # Base query for filtered transactions
        base_q = (
            self.db.query(Transaction)
            .join(Store)
            .join(Product)
        )
        if cutoff:
            base_q = base_q.filter(Transaction.timestamp >= cutoff)
        if store:
            base_q = base_q.filter(Store.store_location == store)
        if category:
            base_q = base_q.filter(Product.category == category)

        # KPI aggregation
        kpi_q = self.db.query(
            func.sum(Transaction.revenue).label("total_revenue"),
            func.count(Transaction.id).label("transaction_count"),
            func.avg(Transaction.revenue).label("avg_order_value"),
        ).join(Store).join(Product)
        if cutoff:
            kpi_q = kpi_q.filter(Transaction.timestamp >= cutoff)

        if store:
            kpi_q = kpi_q.filter(Store.store_location == store)
        if category:
            kpi_q = kpi_q.filter(Product.category == category)

        kpi = kpi_q.first()

        total_revenue = float(kpi.total_revenue or 0)
        transaction_count = int(kpi.transaction_count or 0)
        avg_order_value = round(float(kpi.avg_order_value or 0), 2)

        # Store & product counts (unfiltered for context)
        store_count = self.db.query(Store).count()
        product_count = self.db.query(Product).count()

        # Daily revenue trend (for chart)
        trend_q = (
            self.db.query(
                func.date(Transaction.timestamp).label("date"),
                func.sum(Transaction.revenue).label("daily_revenue"),
            )
            .join(Store)
            .join(Product)
        )
        if cutoff:
            trend_q = trend_q.filter(Transaction.timestamp >= cutoff)
        if store:
            trend_q = trend_q.filter(Store.store_location == store)
        if category:
            trend_q = trend_q.filter(Product.category == category)

        trend_rows = trend_q.group_by("date").order_by("date").all()
        revenue_trend = [
            {"date": str(r.date), "revenue": float(r.daily_revenue)}
            for r in trend_rows
        ]

        # Top 5 stores by revenue
        top_stores_q = (
            self.db.query(
                Store.store_location,
                func.sum(Transaction.revenue).label("revenue"),
            )
            .join(Transaction)
            .join(Product)
        )
        if cutoff:
            top_stores_q = top_stores_q.filter(Transaction.timestamp >= cutoff)
        if category:
            top_stores_q = top_stores_q.filter(Product.category == category)
        top_stores = (
            top_stores_q.group_by(Store.store_location)
            .order_by(func.sum(Transaction.revenue).desc())
            .limit(5)
            .all()
        )

        # Top 5 categories by revenue
        top_cats_q = (
            self.db.query(
                Product.category,
                func.sum(Transaction.revenue).label("revenue"),
            )
            .join(Transaction)
            .join(Store)
        )
        if cutoff:
            top_cats_q = top_cats_q.filter(Transaction.timestamp >= cutoff)
        if store:
            top_cats_q = top_cats_q.filter(Store.store_location == store)
        top_categories = (
            top_cats_q.group_by(Product.category)
            .order_by(func.sum(Transaction.revenue).desc())
            .limit(5)
            .all()
        )

        # Available filter options (for frontend dropdowns)
        all_stores = [
            r[0] for r in self.db.query(Store.store_location).distinct().all()
        ]
        all_categories = [
            r[0] for r in self.db.query(Product.category).distinct().all()
        ]

        res = {
            "status": "success",
            "kpis": {
                "total_revenue": total_revenue,
                "transaction_count": transaction_count,
                "avg_order_value": avg_order_value,
                "store_count": store_count,
                "product_count": product_count,
            },
            "revenue_trend": revenue_trend,
            "top_stores": [
                {"store_location": s.store_location, "revenue": float(s.revenue)}
                for s in top_stores
            ],
            "top_categories": [
                {"category": c.category, "revenue": float(c.revenue)}
                for c in top_categories
            ],
            "filters": self._get_available_filters(),
        }
        self._set_cached_result(cache_key, res)
        return res

    # ------------------------------------------------------------------
    # SHAP Explainability — Profit Boosters & Reducers with Plain English
    # ------------------------------------------------------------------

    def get_shap_explainability(self, days: int = 0, store: str | None = None, category: str | None = None) -> dict:
        """
        Trains LightGBM, computes SHAP values, and generates plain-English
        interpretations. Now supports global filters.
        """
        cache_key = f"explainability_{days}_{store}_{category}"
        cached = self._get_cached_result(cache_key)
        if cached: return cached
        import numpy as np
        from sqlalchemy import func

        cutoff = (self.db.query(func.max(Transaction.timestamp)).scalar() - timedelta(days=days)) if (days > 0) else None

        query = self.db.query(
            Transaction.discount_percentage,
            Transaction.customer_type,
            Transaction.payment_mode,
            Transaction.promotion_applied,
            Transaction.holiday_flag,
            Transaction.revenue,
            Store.store_rating,
            Product.category,
        ).join(Store).join(Product)

        if cutoff:
            query = query.filter(Transaction.timestamp >= cutoff)
        if store:
            query = query.filter(Store.store_location == store)
        if category:
            query = query.filter(Product.category == category)

        df = pd.read_sql(query.statement, self.db.bind)

        if df.empty:
            return {"status": "error", "message": "No data found for explainability filters"}

        processor = DataProcessor(df)
        processed_df = processor.data

        cat_cols = processed_df.select_dtypes(include=["object", "category"]).columns.tolist()
        processed_df = pd.get_dummies(processed_df, columns=cat_cols, drop_first=True)

        bool_cols = processed_df.select_dtypes(include=["bool"]).columns
        processed_df[bool_cols] = processed_df[bool_cols].astype(int)

        X = processed_df.drop(columns=["revenue"])
        y = processed_df["revenue"]

        # Train LightGBM
        booster = LightGBMDriverAnalyzer()
        booster.train(X, y)

        # Compute SHAP values with sampling for performance
        explainer = ShapExplainer(booster.model)
        
        # Sample X for SHAP calculation if large
        sample_size = 2000
        if len(X) > sample_size:
            X_sample = X.sample(n=sample_size, random_state=42)
        else:
            X_sample = X
            
        shap_values = explainer.explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        # Mean SHAP value (signed) per feature — direction matters
        mean_shap_signed = np.mean(shap_values, axis=0)
        mean_shap_abs = np.abs(shap_values).mean(axis=0)
        features = X.columns.tolist()

        # Build importance chart
        importance_df = pd.DataFrame({
            "Feature": features,
            "SHAP_Importance": mean_shap_abs,
        }).sort_values(by="SHAP_Importance", ascending=False)

        chart_json = InteractiveCharts.plot_feature_importance(
            importance_df=importance_df,
            feature_col="Feature",
            importance_val_col="SHAP_Importance",
        )

        # Classify into Boosters and Reducers with plain English
        avg_revenue = float(y.mean())
        boosters = []
        reducers = []

        for i, feat in enumerate(features):
            signed_val = float(mean_shap_signed[i])
            abs_val = float(mean_shap_abs[i])
            pct_impact = round((abs_val / avg_revenue) * 100, 1) if avg_revenue else 0

            # Generate plain English interpretation
            interpretation = self._generate_shap_interpretation(
                feat, signed_val, abs_val, pct_impact
            )

            entry = {
                "feature": feat,
                "shap_value": round(signed_val, 4),
                "abs_importance": round(abs_val, 4),
                "pct_of_avg_revenue": pct_impact,
                "interpretation": interpretation,
            }

            if signed_val >= 0:
                boosters.append(entry)
            else:
                reducers.append(entry)

        # Sort each group by absolute importance (strongest first)
        boosters.sort(key=lambda x: x["abs_importance"], reverse=True)
        reducers.sort(key=lambda x: x["abs_importance"], reverse=True)

        res = {
            "status": "success",
            "chart": chart_json,
            "profit_boosters": boosters,
            "profit_reducers": reducers,
            "summary": (
                f"Analysis identified {len(boosters)} factors that boost revenue "
                f"and {len(reducers)} factors that reduce it. "
                f"The top booster is '{boosters[0]['feature']}' and the "
                f"top reducer is '{reducers[0]['feature']}'."
                if boosters and reducers
                else "Insufficient data for classification."
            ),
            "filters": self._get_available_filters()
        }
        self._set_cached_result(cache_key, res)
        return res

    @staticmethod
    def _generate_shap_interpretation(
        feature: str, signed_val: float, abs_val: float, pct_impact: float
    ) -> str:
        """
        Generates a plain-English sentence describing a feature's SHAP impact.
        """
        direction = "increases" if signed_val >= 0 else "decreases"
        strength = (
            "strongly" if pct_impact > 5
            else "moderately" if pct_impact > 2
            else "slightly"
        )

        # Clean up one-hot encoded feature names for readability
        display_name = feature.replace("_", " ").title()
        if "_" in feature and feature.count("_") > 1:
            parts = feature.rsplit("_", 1)
            display_name = f"{parts[0].replace('_', ' ').title()} = {parts[1].title()}"

        abs_str = f"${abs_val:,.2f}"

        if signed_val >= 0:
            return (
                f"{display_name} {strength} boosts revenue, contributing "
                f"an average of +{abs_str} per transaction "
                f"({pct_impact}% of average order value)."
            )
        else:
            return (
                f"{display_name} {strength} reduces revenue, associated "
                f"with a -{abs_str} decrease per transaction "
                f"({pct_impact}% of average order value)."
            )
