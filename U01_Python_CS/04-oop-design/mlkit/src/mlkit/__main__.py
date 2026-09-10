from mlkit.config import TrainConfig
from mlkit.data.datasets import CSVDataset
from mlkit.pipeline import run_pipeline

dataset = CSVDataset("sample_data.csv", target_column="target")

print("=== Training with model_type='linear' ===")
run_pipeline(dataset, TrainConfig(model_type="linear", tags=["demo-linear"]))

print("\n=== Training with model_type='dummy' ===")
run_pipeline(dataset, TrainConfig(model_type="dummy", tags=["demo-dummy"]))