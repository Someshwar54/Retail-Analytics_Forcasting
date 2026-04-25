"""
Explainability endpoint — SHAP as a decoupled, independent service.
Returns Profit Boosters, Profit Reducers, and plain English interpretations.
GET /api/v1/explainability/
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ....services.analytics import AnalyticsService

router = APIRouter()


@router.get("/")
def get_explainability(
    days: int = 0,
    store: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Computes SHAP values via LightGBM, classifies features into
    Profit Boosters and Profit Reducers, and generates plain-English
    interpretations for each factor.
    """
    try:
        service = AnalyticsService(db)
        result = service.get_shap_explainability(days=days, store=store, category=category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
