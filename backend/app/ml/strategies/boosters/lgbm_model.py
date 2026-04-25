import lightgbm as lgb
import pandas as pd
from typing import Optional, Dict
import joblib
import logging
from ..base import BaseDriverAnalyzer

logger = logging.getLogger(__name__)

class LightGBMDriverAnalyzer(BaseDriverAnalyzer):
    """
    Concrete Strategy Implementation using LightGBM for identifying primary growth drivers.
    LightGBM is highly optimized for performance and memory efficiency.
    """
    def __init__(self, params: Optional[Dict] = None):
        self.model = None
        self.params = params or {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'num_leaves': 31,
            'feature_fraction': 0.8,
            'verbose': -1
        }
        self.feature_names = []

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Trains the LightGBM model on the provided dataset.
        """
        self.feature_names = X.columns.tolist()
        
        # Categorical features in LightGBM should be category dtype
        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in cat_cols:
            X[col] = X[col].astype('category')
            
        train_data = lgb.Dataset(X, label=y, categorical_feature=cat_cols, free_raw_data=False)
        
        logger.info("Starting LightGBM Driver Analysis Training...")
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=500
        )
        logger.info("LightGBM Training Completed.")

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Predicts outcomes based on driver features.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train() first.")
            
        # Ensure identical feature typing before inference
        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in cat_cols:
            X[col] = X[col].astype('category')
            
        predictions = self.model.predict(X)
        return pd.Series(predictions, index=X.index)

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Returns split-based intrinsic feature importance from the model.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train() first.")
            
        importance = self.model.feature_importance(importance_type='split')
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importance
        }).sort_values(by='Importance', ascending=False)
        
        return importance_df

    def save_model(self, path: str) -> None:
        if self.model is not None:
            joblib.dump({'model': self.model, 'features': self.feature_names}, path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: str) -> None:
        data = joblib.load(path)
        self.model = data['model']
        self.feature_names = data['features']
        logger.info(f"Model loaded from {path}")
