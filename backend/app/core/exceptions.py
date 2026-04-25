"""
Custom global exception handlers for the FastAPI application.
Register these handlers in main.py for consistent error responses.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class ModelNotTrainedError(Exception):
    """Raised when a prediction is attempted before a model is trained."""
    pass


class DataIngestionError(Exception):
    """Raised when data cannot be loaded or parsed correctly."""
    pass


class InsufficientDataError(Exception):
    """Raised when there is not enough data to train a model."""
    pass


async def model_not_trained_handler(request: Request, exc: ModelNotTrainedError):
    logger.error(f"ModelNotTrainedError on {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "ModelNotTrainedError"}
    )


async def data_ingestion_handler(request: Request, exc: DataIngestionError):
    logger.error(f"DataIngestionError on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": "DataIngestionError"}
    )


async def insufficient_data_handler(request: Request, exc: InsufficientDataError):
    logger.error(f"InsufficientDataError on {request.url}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "InsufficientDataError"}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "type": "InternalServerError"}
    )
