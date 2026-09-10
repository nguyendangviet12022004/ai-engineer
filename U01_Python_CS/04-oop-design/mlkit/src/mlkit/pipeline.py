from __future__ import annotations
import numpy as np
from mlkit.config import TrainConfig
from mlkit.data.datasets import Dataset
from mlkit.models.registry import create_model_from_name


class Trainer:
    """HAS-A model (composition) — works with ANY BaseModel subclass."""

    def __init__(self, model) -> None:
        self.model = model

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)


def run_pipeline(dataset: Dataset, config: TrainConfig) -> Trainer:
    """Train a model (chosen via config.model_type) on `dataset`.

    References ONLY the Dataset protocol, BaseModel abstract interface,
    and the model registry — never a concrete model class by name.
    """
    X = np.array([dataset[i][0] for i in range(len(dataset))])
    y = np.array([dataset[i][1] for i in range(len(dataset))])

    model = create_model_from_name(config.model_type)
    trainer = Trainer(model)
    trainer.train(X, y)

    predictions = model.predict(X)
    mse = float(np.mean((predictions - y) ** 2))
    print(f"[{config.tags}] Trained {config.model_type} on {len(dataset)} samples "
          f"-> MSE: {round(mse, config.precision)}")
    return trainer


if __name__ == "__main__":
  import numpy as np
  from mlkit.models.dummy import DummyModel
  from mlkit.models.linear import LinearModel
  from mlkit.pipeline import Trainer

  X = np.array([[1], [2], [3], [4]])
  y = np.array([3.0, 5.0, 7.0, 9.0])   # y = 2x + 1

  trainer1 = Trainer(DummyModel())
  trainer1.train(X, y)
  print(trainer1.model.predict(X))   

  trainer2 = Trainer(LinearModel())   
  trainer2.train(X, y)
  print(trainer2.model.predict(X))   
