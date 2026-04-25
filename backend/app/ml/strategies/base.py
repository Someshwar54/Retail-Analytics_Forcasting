from abc import ABC, abstractmethod
from typing import Optional, Any
import pandas as pd

class BaseForecaster(ABC):
    """
    Strategy Pattern interface for Time-Series Revenue Forecasting models.
    Implementations may include ProphetForecaster or LSTMForecaster.
    """
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> None:
        """
        Trains the forecasting model on historical data.
        """
        pass

    @abstractmethod
    def predict(self, steps: int, exogenous_features: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Generates forecasts for the given number of steps into the future.
        """
        pass

    @abstractmethod
    def save_model(self, path: str) -> None:
        """Saves the trained model to disk."""
        pass
        
    @abstractmethod
    def load_model(self, path: str) -> None:
        """Loads a trained model from disk."""
        pass


class BaseClusterer(ABC):
    """
    Strategy Pattern interface for Store Segmentation models.
    Implementations may include KMeansClusterer.
    """
    
    @abstractmethod
    def fit(self, X: pd.DataFrame) -> None:
        """
        Identifies clusters from the store data.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Assigns cluster labels to new or existing store data.
        """
        pass

    @abstractmethod
    def save_model(self, path: str) -> None:
        """Saves the trained model to disk."""
        pass
        
    @abstractmethod
    def load_model(self, path: str) -> None:
        """Loads a trained model from disk."""
        pass


class BaseDriverAnalyzer(ABC):
    """
    Strategy Pattern interface for Sales Driver Analysis models.
    Implementations may include LightGBMDriverAnalyzer or XGBoostDriverAnalyzer.
    """
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Trains the gradient boosting model.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Predicts outcomes based on the driver features.
        """
        pass
        
    @abstractmethod
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Returns the intrinsic feature importance from the model.
        Used as a baseline prior to SHAP analysis.
        """
        pass

    @abstractmethod
    def save_model(self, path: str) -> None:
        """Saves the trained model to disk."""
        pass
        
    @abstractmethod
    def load_model(self, path: str) -> None:
        """Loads a trained model from disk."""
        pass
