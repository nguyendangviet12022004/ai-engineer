from __future__ import annotations
from .base import BaseModel
from .linear import LinearModel
from .dummy import DummyModel
from enum import Enum
class ModelType(Enum):
  LINEAR = "linear"
  DUMMY = "dummy"
  
def create_model(model_type: ModelType) -> BaseModel:
    """Factory pattern — calling code never imports DummyModel/LinearModel
    directly, only this function."""
    if model_type == ModelType.LINEAR:
        return LinearModel()
    if model_type == ModelType.DUMMY:
        return DummyModel()
    raise ValueError(f"Unknown model type: {model_type}") 

def create_model_from_name(name: str) -> BaseModel:
    """Convert a user-facing string (e.g. 'linear') into a concrete
    model instance."""
    try:
        model_type = ModelType(name)
    except ValueError:
        valid = [t.value for t in ModelType]
        raise ValueError(f"Unknown model '{name}'. Valid options: {valid}") from None
    return create_model(model_type)