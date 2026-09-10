from dataclasses import dataclass, field

@dataclass
class TrainConfig:
  learning_rate: float = 1e-3
  tags: list[str] = field(default_factory=list)
  model_type: str = "linear"
  precision: int = 4
  tags: list[str] = field(default_factory=list)
  
  def __post_init__(self) -> None:
    if self.precision <= 0:
      raise ValueError(f"precision must be > 0, got {self.precision}")
    


if __name__ == "__main__":
  TrainConfig(model_type="dummy", precision=2)   # OK
  try:
      TrainConfig(precision=0)
  except ValueError as e:
      print("Error:", e)

  c1, c2 = TrainConfig(), TrainConfig()
  c1.tags.append("run1")
  print(c1.tags, c2.tags) 
      
  