from __future__ import annotations
import json
from typing import Literal, TypedDict, TypeVar, Generic, Callable
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
ModelName = Literal["linear", "dummy", "boosting"]
Status = Literal["queued", "running", "done", "failed"]
class RawRecord(TypedDict):
  name: str
  score: float

def process_record(record: RawRecord) -> str:
    return f"{record['name']}: {record['score']}"

def select_model(name: ModelName) -> str:
  return f"selected {name}"

T = TypeVar('T')

class Box(Generic[T]):
  
  def __init__(self, value: T):
    super().__init__()
    self._value = value
  
  @property
  def value(self) -> T:
    return self._value
  

  @value.setter
  def value(self, value: T) -> None:
    self._value = value
  

def apply_twice(fn: Callable[[int], int], x: int) -> int:
  return fn(fn(x))

def find_user(user_id: int) -> str | None:
  return "Alice" if user_id == 1 else None

class TrainConfig(BaseModel):
  train_ratio: float = Field(gt=0, le=1.0)
  val_ratio: float = Field(gt=0, le=1.0)
  test_ratio: float = Field(gt=0, le=1.0)

  @field_validator("train_ratio")
  @classmethod
  def check_range(cls, value: float) -> float:
    if not (0.0 <= value <= 1.0):
        raise ValueError("must be between 0 and 1")
    return value

  @model_validator(mode="after")
  def check_sum(self) -> TrainConfig:
      if abs(self.train_ratio + self.val_ratio + self.test_ratio - 1.0) > 1e-9:
          raise ValueError("ratios must sum to 1.0")
      return self

class TrainRequest(BaseModel):
  dataset_path: str 
  model_type: ModelName = "linear"
  epochs : int = Field(gt=0, default=10)

class TrainResponse(BaseModel):
  run_id: str
  status: Status

class EvalResult(BaseModel):
    """Metrics produced after evaluating a trained model."""

    accuracy: float = Field(ge=0.0, le=1.0)
    f1_score: float = Field(ge=0.0, le=1.0)

def parse_train_request(raw_json: str) -> TrainRequest | None:
    """Parse a raw JSON string into a TrainRequest, printing a friendly
    error message instead of crashing on malformed input."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON syntax: {e}")
        return None

    try:
        return TrainRequest.model_validate(data)
    except ValidationError as e:
        print("Request failed validation:")
        for err in e.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            print(f"  - {field}: {err['msg']}")
        return None

if __name__ == "__main__":
  req = TrainRequest(dataset_path="data.csv", model_type="linear", epochs=5)
  print(req)
  # dataset_path='data.csv' model_type='linear' epochs=5
  print(req.model_dump())
  # {'dataset_path': 'data.csv', 'model_type': 'linear', 'epochs': 5}
  print(req.model_dump_json())
  # {"dataset_path":"data.csv","model_type":"linear","epochs":5}

  config = TrainConfig(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
  print(config)
  # train_ratio=0.7 val_ratio=0.15 test_ratio=0.15

  try:
      TrainConfig(train_ratio=0.7, val_ratio=0.2, test_ratio=0.2)
  except ValidationError as e:
      print("Error:", e.errors()[0]["msg"])
      # Error: Value error, train_ratio + val_ratio + test_ratio must equal 1.0, got 1.0999999999999999

  try:
      TrainConfig(train_ratio=1.5, val_ratio=0.0, test_ratio=-0.5)
  except ValidationError as e:
      for err in e.errors():
          print("Error:", err["msg"])
      # Error: Value error, ratio must be between 0 and 1, got 1.5
      # Error: Value error, ratio must be between 0 and 1, got -0.5

  result = EvalResult(accuracy=0.92, f1_score=0.89)
  print(result)   # accuracy=0.92 f1_score=0.89

  try:
      EvalResult(accuracy=1.5, f1_score=0.5)
  except ValidationError as e:
      print("Error:", e.errors()[0]["msg"])
      # Error: Input should be less than or equal to 1
      
  print("=== Case 1: broken JSON syntax ===")
  parse_train_request('{"dataset_path": "data.csv", epochs: 5}')
  # Invalid JSON syntax: Expecting property name enclosed in double quotes: line 1 column 30 (char 29)

  print("=== Case 2: valid JSON, wrong field type ===")
  parse_train_request('{"dataset_path": "data.csv", "epochs": "not-a-number"}')
  # Request failed validation:
  #   - epochs: Input should be a valid integer, unable to parse string as an integer

  print("=== Case 3: valid JSON, unknown model_type ===")
  parse_train_request('{"dataset_path": "data.csv", "model_type": "random_forest"}')
  # Request failed validation:
  #   - model_type: Input should be 'linear', 'dummy' or 'boosting'

  print("=== Case 4: valid request ===")
  result = parse_train_request('{"dataset_path": "data.csv", "model_type": "linear", "epochs": 20}')
  print(result)
  # dataset_path='data.csv' model_type='linear' epochs=20
