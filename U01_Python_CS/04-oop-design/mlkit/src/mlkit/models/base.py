from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import pickle

class Point:
  dimension = 2  
  def __init__(self, x:float, y:float) -> None:
    self.x = x
    self.y = y

class Circle:
  def __init__(self, radius: float) -> None:
        self._radius = radius

  
  @property
  def radis(self) -> float:
    return self.radis

  @radis.setter
  def radius(self, value: float) -> None:
    if value <= 0:
        raise ValueError("radius must be positive")
    self._radius = value 


class BaseModel(ABC):
  def __init__(self) -> None:
    self._is_fitted: bool = False

  @abstractmethod
  def fit(self, x: np.ndarray, y: np.ndarray) -> None:
    ...
  
  @abstractmethod
  def predict(self, X: np.ndarray) -> np.ndarray:
    ...
    
  def save(self, path: str) -> None:
    """Shared implementation — subclasses do not override this."""
    with open(path, "wb") as f:
        pickle.dump(self, f)

  @classmethod
  def load(cls, path: str) -> BaseModel:
    with open(path, "rb") as f:
        model = pickle.load(f)
    if not isinstance(model, cls):
        raise TypeError(f"Loaded object is not a {cls.__name__}")
    return model

  @property
  def is_fitted(self):
    return self._is_fitted
  
if __name__ == "__main__":
  mixin = BaseModel()
  print(mixin.is_fitted)   # False

  try:
      mixin.is_fitted = True   # AttributeError: property 'is_fitted' has no setter
  except AttributeError as e:
      print("Error:", e)


