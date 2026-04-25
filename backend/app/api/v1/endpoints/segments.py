"""
Segments endpoint — exposes store clustering via KMeans.
GET /api/v1/segments/
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ....services.analytics import AnalyticsService

router = APIRouter()


@router.get("/")
def get_store_segments(
    n_clusters: int = 4, 
    days: int = 0, 
    category: str | None = None, 
    db: Session = Depends(get_db)
):
    """
    Clusters stores into performance segments using KMeans.
    Returns an interactive Plotly scatter chart and per-cluster statistics.

    Parameters
    ----------
    n_clusters : int
        Number of store segments to identify (default 4).
    days : int
        Time window in days for segmentation analysis.
    category : str
        Filter by product category.
    """
    try:
        service = AnalyticsService(db)
        result = service.segment_stores(n_clusters=n_clusters, days=days, category=category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
