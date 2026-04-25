from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ....services.analytics import AnalyticsService

router = APIRouter()

@router.get("/")
def get_sales_drivers(
    days: int = 0,
    store: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Executes LightGBM driver analysis and calculates global SHAP feature importance.
    Returns an interactive Plotly chart JSON showing the most significant revenue drivers.
    """
    try:
        service = AnalyticsService(db)
        result = service.analyze_sales_drivers(days=days, store=store, category=category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
