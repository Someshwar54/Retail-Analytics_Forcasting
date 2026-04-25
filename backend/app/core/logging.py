"""
Centralized logging configuration for the Retail Analytics application.
Call setup_logging() once at application startup.
"""
import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures the root logger with a consistent format across all modules.
    Should be called once during application startup in main.py.
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silence noisy third-party loggers
    logging.getLogger("prophet").setLevel(logging.WARNING)
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    logging.getLogger("lightgbm").setLevel(logging.WARNING)
    logging.getLogger("shap").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging initialized at level={log_level}"
    )
