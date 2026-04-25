"""
Overview endpoint — KPI dashboard stats with multi-filter support.
GET /api/v1/overview/?days=30&store=Downtown&category=Electronics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...dependencies import get_db
from ....services.analytics import AnalyticsService

router = APIRouter()


@router.get("/")
def get_overview(
    days: int = Query(30, ge=0, le=9999, description="Lookback window in days (0 = all time)"),
    store: Optional[str] = Query(None, description="Filter by store location"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: Session = Depends(get_db),
):
    """
    Returns KPI summary, revenue trend, top stores/categories,
    and available filter options for the dashboard overview.
    """
    try:
        service = AnalyticsService(db)
        result = service.get_overview_stats(days=days, store=store, category=category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
