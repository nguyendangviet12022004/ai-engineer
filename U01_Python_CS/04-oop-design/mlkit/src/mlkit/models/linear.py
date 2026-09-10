from __future__ import annotations
from .base import BaseModel
import numpy as np

class LinearModel(BaseModel):
    def __init__(self) -> None:
        super().__init__()
        self._weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        self._weights = np.linalg.pinv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y
        self._is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Call fit() before predict()")
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        return X_with_bias @ self._weights