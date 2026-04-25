"""
KMeans Store Segmentation Strategy — concrete implementation of BaseClusterer.

Segments stores into performance tiers based on aggregated metrics such as
average revenue, store rating, and discount behaviour. Uses Scikit-Learn's
MinMaxScaler before fitting to ensure features are on a comparable scale.
"""
import pandas as pd
import numpy as np
import joblib
import logging
from typing import Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from ..base import BaseClusterer

logger = logging.getLogger(__name__)

_CLUSTER_LABELS = {
    0: "Premium Performer",
    1: "Growth Potential",
    2: "Stable Average",
    3: "Underperformer",
}


class KMeansClusterer(BaseClusterer):
    """
    Strategy Pattern implementation of store segmentation using K-Means clustering.

    Feature columns passed in *X* are normalised before clustering to prevent
    high-magnitude columns (e.g. revenue) from dominating the distance metric.
    """

    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._model: Optional[KMeans] = None
        self._scaler: Optional[MinMaxScaler] = None
        self._feature_cols: list[str] = []

    # ------------------------------------------------------------------
    # BaseClusterer interface
    # ------------------------------------------------------------------

    def fit(self, X: pd.DataFrame) -> None:
        """
        Scales features and fits the KMeans model.

        Parameters
        ----------
        X : pd.DataFrame
            Numeric feature matrix. Typical columns: avg_revenue, store_rating,
            avg_discount, units_sold.
        """
        if X.empty:
            raise ValueError("Cannot fit KMeans on an empty DataFrame.")

        self._feature_cols = X.columns.tolist()
        self._scaler = MinMaxScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._model = KMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=self.random_state,
        )
        self._model.fit(X_scaled)
        logger.info(
            "KMeans clustering complete. "
            f"Inertia={self._model.inertia_:.2f}, k={self.n_clusters}"
        )

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Assigns cluster labels to the provided feature rows.

        Returns a Series of integer cluster IDs aligned with X's index.
        """
        self._assert_fitted()
        X_scaled = self._scaler.transform(X[self._feature_cols])
        labels = self._model.predict(X_scaled)
        return pd.Series(labels, index=X.index, name="cluster_id")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def predict_with_labels(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Convenience wrapper: returns X with two extra columns —
        ``cluster_id`` (int) and ``cluster_label`` (human-readable string).
        """
        result = X.copy()
        result["cluster_id"] = self.predict(X)
        result["cluster_label"] = result["cluster_id"].map(
            lambda cid: _CLUSTER_LABELS.get(cid, f"Cluster {cid}")
        )
        return result

    def get_cluster_centers(self) -> pd.DataFrame:
        """
        Returns the cluster centroids in the *original* (unscaled) feature space.
        """
        self._assert_fitted()
        centers_scaled = self._model.cluster_centers_
        centers = self._scaler.inverse_transform(centers_scaled)
        return pd.DataFrame(centers, columns=self._feature_cols)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_model(self, path: str) -> None:
        joblib.dump(
            {
                "model": self._model,
                "scaler": self._scaler,
                "feature_cols": self._feature_cols,
                "n_clusters": self.n_clusters,
            },
            path,
        )
        logger.info(f"KMeans model saved to {path}")

    def load_model(self, path: str) -> None:
        data = joblib.load(path)
        self._model = data["model"]
        self._scaler = data["scaler"]
        self._feature_cols = data["feature_cols"]
        self.n_clusters = data["n_clusters"]
        logger.info(f"KMeans model loaded from {path}")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _assert_fitted(self) -> None:
        if self._model is None or self._scaler is None:
            raise ValueError(
                "Clusterer is not fitted. Call fit() before predict()."
            )
