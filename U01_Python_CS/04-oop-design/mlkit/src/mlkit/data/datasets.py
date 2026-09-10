from __future__ import annotations
import csv
from typing import Protocol, runtime_checkable


@runtime_checkable
class Dataset(Protocol):
  def __len__(self) -> int: ...
  def __getitem__(self, index: int) -> tuple[list[float], float]: ...

class CSVDataset:
    def __init__(self, file_path: str, target_column: str) -> None:
        self.file_path = file_path
        self.target_column = target_column
        with open(file_path, newline="", encoding="utf-8") as f:
            self._rows = list(csv.DictReader(f))

    def __repr__(self) -> str:
        return f"CSVDataset(file_path={self.file_path!r}, n_samples={len(self)})"

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> tuple[list[float], float]:
        row = dict(self._rows[index])
        target = float(row.pop(self.target_column))
        features = [float(v) for v in row.values()]
        return features, target
      

if __name__ == "__main__":
  with open("sample_data.csv", "w", newline="", encoding="utf-8") as f:
    f.write("x1,x2,target\n1,2,5\n2,3,8\n3,4,11\n")

  dataset = CSVDataset("sample_data.csv", target_column="target")
  print(dataset)               # CSVDataset(file_path='sample_data.csv', n_samples=3)
  print(len(dataset))          # 3
  print(dataset[0])            # ([1.0, 2.0], 5.0)

  for i in range(len(dataset)):
      features, target = dataset[i]
      print(features, "->", target)
  
  print(isinstance(dataset, Dataset))
  print(CSVDataset.__bases__) 
  