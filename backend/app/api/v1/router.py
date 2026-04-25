from fastapi import APIRouter
from .endpoints import forecast, drivers, segments, overview, explainability

api_router = APIRouter()

api_router.include_router(overview.router, prefix="/overview", tags=["Overview"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Driver Analysis"])
api_router.include_router(segments.router, prefix="/segments", tags=["Store Segmentation"])
api_router.include_router(explainability.router, prefix="/explainability", tags=["Explainability"])
