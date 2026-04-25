import shap
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ShapExplainer:
    """
    Explainability Engine integrating SHAP (SHapley Additive exPlanations).
    This class wraps around trained Tree-based models (like LightGBM or XGBoost)
    to provide feature-level explanations and global interpretations.
    """
    
    def __init__(self, model: Any):
        """
        Initializes the SHAP explainer with a trained model.
        """
        try:
            self.explainer = shap.TreeExplainer(model)
            logger.info("SHAP TreeExplainer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            raise ValueError("Model provided is not supported by SHAP TreeExplainer.") from e

    def get_local_explanation(self, X_instance: pd.DataFrame) -> Dict[str, float]:
        """
        Returns feature contributions for a specific prediction instance.
        Shows management exactly *why* a specific prediction was made.
        """
        shap_values = self.explainer.shap_values(X_instance)
        
        # Handle binary classification vs regression shape differences in SHAP
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Get values for positive class
            
        feature_names = X_instance.columns.tolist()
        
        # Zip features with their respective SHAP values for this instance
        contributions = dict(zip(feature_names, shap_values[0]))
        
        # Calculate base value (expected value)
        expected_value = self.explainer.expected_value
        if isinstance(expected_value, (list, np.ndarray)):
            expected_value = expected_value[1]
            
        return {
            "base_value": float(expected_value),
            "feature_contributions": {k: float(v) for k, v in contributions.items()}
        }

    def get_global_importance(self, X: pd.DataFrame, sample_size: int = 2000) -> pd.DataFrame:
        """
        Calculates the mean absolute SHAP values across the dataset
        to determine global feature importance. Samples data if it's too large
        to maintain dashboard responsiveness.
        """
        # Sampling for performance on large datasets
        if len(X) > sample_size:
            logger.info(f"Sampling {sample_size} rows from {len(X)} for SHAP importance speedup.")
            X_sample = X.sample(n=sample_size, random_state=42)
        else:
            X_sample = X

        shap_values = self.explainer.shap_values(X_sample)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
            
        # Mean absolute SHAP value for each feature
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        importance_df = pd.DataFrame({
            'Feature': X_sample.columns,
            'SHAP_Importance': mean_abs_shap
        }).sort_values(by='SHAP_Importance', ascending=False)
        
        return importance_df
