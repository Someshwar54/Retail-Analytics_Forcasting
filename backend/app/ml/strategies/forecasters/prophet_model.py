from prophet import Prophet
import pandas as pd
from typing import Optional
import joblib
import logging
from ..base import BaseForecaster

logger = logging.getLogger(__name__)

class ProphetForecaster(BaseForecaster):
    """
    Concrete Strategy Implementation using Meta's Prophet for Time-Series Revenue Forecasting.
    Prophet natively handles seasonality and exogenous features (e.g., Holiday_Flag).
    """
    def __init__(self, holidays: Optional[pd.DataFrame] = None):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            holidays=holidays
        )
        self.exogenous_columns = []

    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> None:
        """
        Trains the Prophet model.
        Prophet expects a dataframe with 'ds' (datestamp) and 'y' (target) columns.
        """
        df = X.copy()
        df['y'] = y.values
        
        # Add exogenous regressors (like Holiday_Flag, Discount_Percentage)
        exogenous_features = kwargs.get('exogenous_features', [])
        for feature in exogenous_features:
            if feature in df.columns:
                self.model.add_regressor(feature)
                self.exogenous_columns.append(feature)
                
        logger.info("Starting Prophet Time-Series Training...")
        self.model.fit(df)
        logger.info("Prophet Training Completed.")

    def predict(self, steps: int, exogenous_features: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Generates future forecasts.
        """
        if self.model.history is None:
            raise ValueError("Model is not trained. Call train() first.")
            
        future = self.model.make_future_dataframe(periods=steps, freq='D')
        
        if exogenous_features is not None and self.exogenous_columns:
            # Merge exogenous features into the future dataframe
            future = future.merge(exogenous_features, on='ds', how='left')
            # Handle missing exogenous values with backward fill as a simple default
            future[self.exogenous_columns] = future[self.exogenous_columns].bfill().fillna(0)
            
        forecast = self.model.predict(future)
        return forecast

    def save_model(self, path: str) -> None:
        """
        Saves the Prophet model.
        """
        if self.model.history is not None:
            joblib.dump({
                'model': self.model,
                'exog': self.exogenous_columns
            }, path)
            logger.info(f"Prophet model saved to {path}")

    def load_model(self, path: str) -> None:
        """
        Loads the Prophet model.
        """
        data = joblib.load(path)
        self.model = data['model']
        self.exogenous_columns = data['exog']
        logger.info(f"Prophet model loaded from {path}")
