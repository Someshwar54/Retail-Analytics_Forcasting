from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ....services.analytics import AnalyticsService

router = APIRouter()

@router.get("/")
def get_revenue_forecast(
    steps: int = 30, 
    store: str | None = None, 
    category: str | None = None, 
    db: Session = Depends(get_db)
):
    """
    Retrieves the time-series revenue forecast for the given number of steps (days).
    Returns an interactive Plotly chart JSON and top-level predictions.
    """
    try:
        service = AnalyticsService(db)
        result = service.generate_revenue_forecast(steps=steps, store=store, category=category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
