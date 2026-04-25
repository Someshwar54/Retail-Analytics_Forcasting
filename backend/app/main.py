from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    ModelNotTrainedError,
    DataIngestionError,
    InsufficientDataError,
    model_not_trained_handler,
    data_ingestion_handler,
    insufficient_data_handler,
    generic_exception_handler,
)
import uvicorn

# Initialize centralized logging first so all imported modules inherit it
setup_logging(log_level="DEBUG" if settings.DEBUG else "INFO")

app = FastAPI(
    title=settings.APP_NAME,
    description="Monolithic Backend for Retail Analytics, Forecasting, and Segmentation",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Custom Exception Handlers ---
app.add_exception_handler(ModelNotTrainedError, model_not_trained_handler)
app.add_exception_handler(DataIngestionError, data_ingestion_handler)
app.add_exception_handler(InsufficientDataError, insufficient_data_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# --- Routers ---
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to the {settings.APP_NAME}", "version": settings.APP_VERSION}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

