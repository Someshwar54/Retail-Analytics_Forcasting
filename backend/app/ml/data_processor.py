import pandas as pd
import numpy as np
from typing import Iterator
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Encapsulates DataFrame operations securely, including an automated downcasting
    method to drastically minimize memory footprint during data ingestion.
    """
    def __init__(self, data: pd.DataFrame):
        # We strictly encapsulate the dataframe to prevent unintended mutations
        self._data = self._downcast_dtypes(data)
        logger.info(f"DataProcessor initialized. Memory usage: {self.memory_usage_mb():.2f} MB")

    @classmethod
    def from_sql_generator(cls, sql_generator: Iterator[pd.DataFrame]) -> Iterator['DataProcessor']:
        """
        Yields DataProcessor instances from a SQL query generator stream to maintain O(1) space complexity.
        """
        for chunk in sql_generator:
            yield cls(chunk)

    def _downcast_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Downcasts integer and float columns to the smallest possible datatype.
        """
        # Deep copy to ensure we don't modify the original dataframe if passed by reference
        df_downcasted = df.copy()
        
        # Downcast floats
        float_cols = df_downcasted.select_dtypes(include=['float64']).columns
        for col in float_cols:
            df_downcasted[col] = pd.to_numeric(df_downcasted[col], downcast='float')
            
        # Downcast integers
        int_cols = df_downcasted.select_dtypes(include=['int64']).columns
        for col in int_cols:
            df_downcasted[col] = pd.to_numeric(df_downcasted[col], downcast='integer')
            
        return df_downcasted

    @property
    def data(self) -> pd.DataFrame:
        """
        Returns a copy of the dataframe to ensure encapsulation is strictly maintained.
        Modifications to this property will not affect the internal state.
        """
        return self._data.copy()

    def memory_usage_mb(self) -> float:
        """
        Calculates the current memory footprint of the encapsulated dataframe in MB.
        """
        return self._data.memory_usage(deep=True).sum() / (1024 ** 2)
