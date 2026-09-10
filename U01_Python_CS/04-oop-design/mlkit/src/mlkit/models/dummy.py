from __future__ import annotations
from .base import BaseModel
import numpy as np

class DummyModel(BaseModel):
  def __init__(self):
    super().__init__()
    self._mean_value : float | None = None
    
  def fit(self, x: np.ndarray, y: np.ndarray) -> None:
    self._mean_value = float(np.mean(y))
    self._is_fitted = True
  
  def predict(self, x: np.ndarray) -> np.ndarray:
    if not self.is_fitted:
      raise RuntimeError("Call fit() before predict()")
    return np.full(shape=(len(x),), fill_value=self._mean_value)
  
  
