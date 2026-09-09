# U01-04 — OOP và Thiết kế Lớp trong Python

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 2 · **Giờ dự kiến:** 7 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.11-14 · Stanford CS106B (OOP concepts) · Refactoring Guru — Design Patterns
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.
> **Cách dùng file này:** Đọc lý thuyết từng phần → làm ngay bài tập của phần đó (tick ☐ → ☑) → cuối bài có 1 dự án tổng hợp dùng lại mọi thứ đã làm.

---

## 1. Mục tiêu bài học

- [ ] Viết `class` đúng chuẩn, phân biệt instance vs class attribute, dùng `@property`.
- [ ] Hiểu kế thừa, MRO, `super()`, ưu tiên composition khi phù hợp.
- [ ] Cài đặt magic method: `__repr__`, `__eq__`, `__hash__`, `__len__`, `__call__`, `__getitem__`.
- [ ] Dùng `@dataclass` và `NamedTuple` đúng chỗ.
- [ ] Phân biệt ABC vs Protocol — kỹ năng thiết kế interface cho pipeline ML.
- [ ] Nhận diện Enum, Singleton, Factory, Strategy pattern.
- [ ] Xây `datasets.py`: Protocol + 2 implementation, đổi được mà không sửa code dùng nó.

---

## 2. Phần 2.1 — Class cơ bản: `__init__`, attribute, `@property`

### Lý thuyết

```python
class Point:
    dimension = 2                 # CLASS attribute — CHIA SẺ giữa mọi instance

    def __init__(self, x: float, y: float) -> None:
        self.x = x                # INSTANCE attribute — RIÊNG của từng object
        self.y = y
```

**Bẫy:** sửa class attribute qua instance sẽ tạo instance attribute mới, không sửa class attribute gốc:

```python
p1 = Point(0, 0)
p2 = Point(1, 1)
p1.dimension = 3          # tạo INSTANCE attribute mới cho p1
print(p1.dimension, p2.dimension, Point.dimension)   # 3 2 2
```

**`@property`** — kiểm soát đọc/ghi attribute như phương thức, gọi như attribute thường:

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def area(self) -> float:      # computed property — tính động
        return 3.14159 * self._radius ** 2
```

### Bài tập 2.1 — Class có validate qua `@property`

- [ ] **BT 2.1.1** — Tạo 2 instance `Point`, chứng minh sửa `dimension` qua 1 instance không ảnh hưởng instance kia hay class gốc (đúng như ví dụ trên).
- [ ] **BT 2.1.2** — Viết class `BankAccount` với `@property balance` chỉ đọc (không có setter), và phương thức `deposit(amount)`/`withdraw(amount)` validate `amount > 0` và không cho rút quá số dư.

<details>
<summary><strong>Lời giải chi tiết BT 2.1</strong></summary>

```python
class Point:
    dimension = 2
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

p1 = Point(0, 0)
p2 = Point(1, 1)
p1.dimension = 3
print(p1.dimension, p2.dimension, Point.dimension)   # 3 2 2


class BankAccount:
    """A bank account with a read-only balance and validated operations."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        if initial_balance < 0:
            raise ValueError("initial_balance cannot be negative")
        self._balance = initial_balance

    @property
    def balance(self) -> float:
        """Read-only — there is intentionally no setter for `balance`."""
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("withdraw amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

account = BankAccount(100)
account.deposit(50)
print(account.balance)   # 150
account.withdraw(30)
print(account.balance)   # 120

try:
    account.balance = 999   # AttributeError: property 'balance' has no setter
except AttributeError as e:
    print("Error:", e)
```
</details>

---

## 3. Phần 2.2 — Kế thừa, MRO, `super()`, Composition

### Lý thuyết

```python
class A:
    def greet(self): return "A"
class B(A):
    def greet(self): return "B"
class C(A):
    def greet(self): return "C"
class D(B, C):
    pass

print(D.__mro__)      # (D, B, C, A, object) — thuật toán C3 linearization
print(D().greet())    # "B" — tìm theo MRO, gặp B trước C
```

`super()` gọi phương thức lớp cha **theo đúng MRO**:

```python
class Base:
    def __init__(self, name: str) -> None:
        self.name = name

class Derived(Base):
    def __init__(self, name: str, extra: int) -> None:
        super().__init__(name)
        self.extra = extra
```

**"Composition over Inheritance"** — kế thừa tạo quan hệ "is-a" chặt chẽ, composition tạo quan hệ "has-a" linh hoạt hơn:

```python
class Trainer:
    def __init__(self, optimizer: "Optimizer") -> None:
        self.optimizer = optimizer   # Trainer "has-a" optimizer, không kế thừa nó
    def step(self) -> None:
        self.optimizer.update()
```

> **Quy tắc thực hành:** chỉ kế thừa khi "is-a" đúng ngữ nghĩa và cần tái sử dụng hành vi chung. Khi chỉ cần "dùng chức năng của object khác", ưu tiên composition.

### Bài tập 2.2 — MRO và Composition

- [ ] **BT 2.2.1** — Tạo lại ví dụ `A`/`B`/`C`/`D` trên, in `__mro__` và giải thích bằng lời vì sao thứ tự đó.
- [ ] **BT 2.2.2** — Viết 2 class `SGDOptimizer` và `AdamOptimizer` (mỗi class có method `update()` in ra tên chính nó), rồi viết `Trainer` (composition) nhận optimizer bất kỳ trong constructor và gọi `step()` — chứng minh đổi optimizer không cần sửa `Trainer`.

<details>
<summary><strong>Lời giải chi tiết BT 2.2</strong></summary>

```python
class A:
    def greet(self): return "A"
class B(A):
    def greet(self): return "B"
class C(A):
    def greet(self): return "C"
class D(B, C):
    pass

print(D.__mro__)
print(D().greet())
# MRO là (D, B, C, A, object): Python tìm greet() theo thứ tự D -> B -> C -> A,
# gặp B trước nên trả "B", dù D cũng kế thừa C (chỉ là C đứng sau B trong MRO).


class SGDOptimizer:
    def update(self) -> None:
        print("SGDOptimizer: updating weights with plain gradient descent")

class AdamOptimizer:
    def update(self) -> None:
        print("AdamOptimizer: updating weights with adaptive moments")

class Trainer:
    """Trainer HAS-A optimizer — it never inherits from any optimizer class."""
    def __init__(self, optimizer) -> None:
        self.optimizer = optimizer

    def step(self) -> None:
        self.optimizer.update()

trainer1 = Trainer(SGDOptimizer())
trainer1.step()   # SGDOptimizer: ...

trainer2 = Trainer(AdamOptimizer())   # swap optimizer, ZERO changes to Trainer
trainer2.step()   # AdamOptimizer: ...
```
</details>

---

## 4. Phần 2.3 — Magic Methods

### Lý thuyết

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __len__(self) -> int:
        return 2

    def __call__(self, scale: float) -> "Vector":
        return Vector(self.x * scale, self.y * scale)

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]
```

| Magic method | Được gọi khi | Ứng dụng thực tế |
|---|---|---|
| `__repr__` | `repr(obj)`, in REPL/debugger | Debug dễ dàng |
| `__eq__` | `obj1 == obj2` | So sánh 2 config/kết quả |
| `__hash__` | `hash(obj)`, dict key/set element | Cache theo config |
| `__len__` | `len(obj)` | `Dataset.__len__` → tổng số mẫu |
| `__call__` | `obj(...)` | Model gọi như hàm: `model(x)` |
| `__getitem__` | `obj[i]` | `Dataset.__getitem__` → lấy 1 mẫu |

### Bài tập 2.3 — Cài magic method cho 1 class thực tế

- [ ] **BT 2.3.1** — Tự cài lại `Vector` như trên, kiểm chứng: `repr()`, `==`, `hash()` giữa 2 vector bằng nhau, `len()`, gọi `v(2.0)`, và `v[0]`/`v[1]`.
- [ ] **BT 2.3.2** — Cho 2 `Vector` bằng nhau vào 1 `set()`, chứng minh chúng bị coi là trùng (chỉ còn 1 phần tử) — nhờ `__eq__` + `__hash__` nhất quán.

<details>
<summary><strong>Lời giải chi tiết BT 2.3</strong></summary>

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash((self.x, self.y))
    def __len__(self):
        return 2
    def __call__(self, scale):
        return Vector(self.x * scale, self.y * scale)
    def __getitem__(self, index):
        return (self.x, self.y)[index]

v1 = Vector(1, 2)
v2 = Vector(1, 2)
print(repr(v1))            # Vector(x=1, y=2)
print(v1 == v2)             # True
print(hash(v1) == hash(v2)) # True
print(len(v1))               # 2
print(v1(2.0))                 # Vector(x=2.0, y=4.0)
print(v1[0], v1[1])             # 1 2

unique_vectors = {v1, v2}
print(unique_vectors)   # {Vector(x=1, y=2)} — chỉ 1 phần tử, dù thêm 2 object khác nhau
```
</details>

---

## 5. Phần 2.4 — `@dataclass` và `NamedTuple`

### Lý thuyết

```python
from dataclasses import dataclass, field

@dataclass
class TrainConfig:
    learning_rate: float = 1e-3
    epochs: int = 10
    tags: list[str] = field(default_factory=list)   # KHÔNG viết tags: list = []

@dataclass(frozen=True)     # immutable + tự động hashable
class ImmutablePoint:
    x: float
    y: float
```

```python
from typing import NamedTuple

class EvalResult(NamedTuple):
    accuracy: float
    f1_score: float
```

| Tình huống | Lựa chọn |
|---|---|
| Chứa dữ liệu, ít logic (config, kết quả) | `@dataclass` |
| Cần immutable + hashable, nhẹ, giống tuple | `NamedTuple` |
| Logic nghiệp vụ phức tạp, kế thừa sâu | `class` thường |

### Bài tập 2.4 — `TrainConfig` có validate

- [ ] **BT 2.4.1** — Viết `TrainConfig` (dataclass) với `learning_rate`, `epochs`, validate `> 0` cho cả 2 bằng `__post_init__`, ném `ValueError` nếu vi phạm.
- [ ] **BT 2.4.2** — Chứng minh `field(default_factory=list)` tạo list **độc lập** cho mỗi instance (không như bẫy mutable default ở Bài 1.2).

<details>
<summary><strong>Lời giải chi tiết BT 2.4</strong></summary>

```python
from dataclasses import dataclass, field

@dataclass
class TrainConfig:
    learning_rate: float = 1e-3
    epochs: int = 10
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be > 0, got {self.learning_rate}")
        if self.epochs <= 0:
            raise ValueError(f"epochs must be > 0, got {self.epochs}")

TrainConfig(learning_rate=0.01, epochs=5)   # OK
try:
    TrainConfig(learning_rate=-1, epochs=5)
except ValueError as e:
    print("Error:", e)

c1, c2 = TrainConfig(), TrainConfig()
c1.tags.append("exp1")
print(c1.tags, c2.tags)   # ['exp1'] []  — độc lập, không chia sẻ
```
</details>

---

## 6. Phần 2.5 — ABC vs Protocol

### Lý thuyết

Phần **quan trọng nhất** bài học — quyết định cách thiết kế mọi pipeline trong lộ trình.

**ABC — "nominal typing"**: lớp con phải kế thừa tường minh.

```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def fit(self, X, y) -> None: ...
    @abstractmethod
    def predict(self, X): ...

class LinearModelWrapper(BaseModel):    # PHẢI kế thừa
    def fit(self, X, y) -> None: ...
    def predict(self, X): ...
```

Quên implement → `TypeError` ngay lúc khởi tạo object.

**Protocol — "structural typing"**: không cần kế thừa, chỉ cần đúng cấu trúc ("duck typing").

```python
from typing import Protocol

class Dataset(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, index: int): ...

class CSVDataset:            # KHÔNG kế thừa Dataset, vẫn hợp lệ!
    def __len__(self) -> int: ...
    def __getitem__(self, index: int): ...
```

| | ABC | Protocol |
|---|---|---|
| Đăng ký hợp lệ | Kế thừa tường minh | Đúng cấu trúc, không kế thừa |
| Kiểm tra | Runtime (lúc khởi tạo) | Static (mypy/pyright), hoặc `isinstance()` với `@runtime_checkable` |
| Chia sẻ code triển khai? | Có | Không (chỉ chữ ký) |
| Dùng khi | Bạn kiểm soát toàn bộ hierarchy | Cần tương thích class có sẵn, hoặc interface lỏng dễ mock |

> **Quyết định:** dùng ABC khi thiết kế 1 họ class từ đầu, muốn ép buộc cấu trúc chung. Dùng Protocol khi định nghĩa "hợp đồng" mà nhiều loại object — kể cả từ thư viện ngoài — có thể thoả mãn mà không cần sửa code chúng.

### Bài tập 2.5 — `BaseModel` (ABC)

- [ ] **BT 2.5.1** — Xây `BaseModel` (ABC) với 4 abstract method: `fit`, `predict`, `save`, `load`. `save`/`load` nên là concrete method (dùng chung `pickle`), không phải abstract.
- [ ] **BT 2.5.2** — Cài `DummyModel` (luôn dự đoán trung bình của `y`) và `LinearModelWrapper` (normal equation) kế thừa `BaseModel`.
- [ ] **BT 2.5.3** — Cố tình viết 1 lớp con thiếu implement `predict`, chứng minh Python ném `TypeError` ngay khi khởi tạo.

<details>
<summary><strong>Lời giải chi tiết BT 2.5</strong></summary>

```python
"""Abstract base class for ML models with a unified fit/predict/save/load API."""
from __future__ import annotations

import pickle
from abc import ABC, abstractmethod

import numpy as np


class BaseModel(ABC):
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model on features X and targets y."""

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predictions for features X."""

    def save(self, path: str) -> None:
        """Shared implementation — subclasses do not need to override this."""
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> "BaseModel":
        with open(path, "rb") as f:
            model = pickle.load(f)
        if not isinstance(model, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__}")
        return model


class DummyModel(BaseModel):
    def __init__(self) -> None:
        self._mean_value: float | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._mean_value = float(np.mean(y))

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._mean_value is None:
            raise RuntimeError("Call fit() before predict()")
        return np.full(shape=(len(X),), fill_value=self._mean_value)


class LinearModelWrapper(BaseModel):
    def __init__(self) -> None:
        self._weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        self._weights = np.linalg.pinv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._weights is None:
            raise RuntimeError("Call fit() before predict()")
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        return X_with_bias @ self._weights


# BT 2.5.3 — demonstrate TypeError on incomplete subclass
class Incomplete(BaseModel):
    def fit(self, X, y):
        pass
    # predict is missing on purpose

try:
    Incomplete()
except TypeError as e:
    print("Error:", e)
```
</details>

---

## 7. Phần 2.6 — Enum, Singleton, Factory, Strategy

### Lý thuyết

```python
from enum import Enum, auto

class ModelType(Enum):
    LINEAR = auto()
    RANDOM_FOREST = auto()
    NEURAL_NET = auto()
```

```python
def model_factory(model_type: ModelType) -> "BaseModel":
    """Factory pattern — tách 'tạo object nào' khỏi nơi sử dụng."""
    if model_type == ModelType.LINEAR:
        return LinearModelWrapper()
    if model_type == ModelType.RANDOM_FOREST:
        return DummyModel()   # placeholder demo
    raise ValueError(f"Unknown model type: {model_type}")
```

Strategy pattern đã minh hoạ ở Phần 2.2 (`Trainer` nhận `optimizer` bất kỳ). Singleton dùng khi cần trạng thái dùng chung toàn cục — cẩn thận, lạm dụng gây khó test.

### Bài tập 2.6 — `ModelType` Enum + Factory

- [ ] **BT 2.6.1** — Viết `ModelType` (Enum) và `model_factory(model_type)` như trên, gọi thử với cả 2 giá trị hợp lệ và 1 giá trị không tồn tại (bắt lỗi).

<details>
<summary><strong>Lời giải chi tiết BT 2.6</strong></summary>

```python
from enum import Enum, auto

class ModelType(Enum):
    LINEAR = auto()
    DUMMY = auto()

def model_factory(model_type: ModelType):
    if model_type == ModelType.LINEAR:
        return LinearModelWrapper()
    if model_type == ModelType.DUMMY:
        return DummyModel()
    raise ValueError(f"Unknown model type: {model_type}")

print(model_factory(ModelType.LINEAR))
print(model_factory(ModelType.DUMMY))
```
</details>

---

## 8. Dự án tổng hợp — Mini Training Pipeline

Dùng lại **toàn bộ** Phần 2.1-2.6: `BaseModel` (ABC), `TrainConfig` (dataclass), `Dataset` (Protocol), magic method, composition — ghép thành 1 pipeline huấn luyện tí hon nhưng hoạt động thật.

### Yêu cầu

- [ ] **DA.1** — `datasets.py`: định nghĩa `Protocol Dataset` (`__len__`, `__getitem__`) + 2 lớp cài đặt `CSVDataset` và `ImageFolderDataset` — **không kế thừa** Protocol.
- [ ] **DA.2** — Viết hàm `run_pipeline(dataset: Dataset, model: BaseModel, config: TrainConfig)` — chuyển dữ liệu từ `Dataset` sang numpy array, gọi `model.fit()`, in báo cáo dùng `config`.
- [ ] **DA.3** — Chạy `run_pipeline` với **cả 2** dataset (`CSVDataset`, `ImageFolderDataset` — dataset ảnh dùng dữ liệu giả để demo) và **cả 2** model (`DummyModel`, `LinearModelWrapper`) — tổng cộng ≥2 tổ hợp — **không sửa 1 dòng nào** trong `run_pipeline`.
- [ ] **DA.4** — `TrainConfig` dùng để cấu hình pipeline (ví dụ: số `epochs` in ra bao nhiêu dòng log) — chứng minh dataclass tích hợp thật vào luồng chạy, không chỉ là ví dụ độc lập.

<details>
<summary><strong>Lời giải chi tiết — Dự án tổng hợp</strong></summary>

**`datasets.py`** (Protocol, tái sử dụng Phần 2.5 style):

```python
"""Dataset abstraction using structural typing (Protocol)."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Dataset(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> tuple[list[float], float]: ...


class CSVDataset:
    """Loads (features, target) pairs from a CSV file. Does NOT inherit
    from Dataset — it satisfies the protocol purely structurally."""

    def __init__(self, file_path: str, target_column: str) -> None:
        self.target_column = target_column
        with open(file_path, newline="", encoding="utf-8") as f:
            self._rows = list(csv.DictReader(f))

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> tuple[list[float], float]:
        row = dict(self._rows[index])
        target = float(row.pop(self.target_column))
        features = [float(v) for v in row.values()]
        return features, target


@dataclass
class ImageSample:
    features: list[float]   # e.g. a tiny fake embedding, to keep this dependency-free
    label: float


class ImageFolderDataset:
    """Simulates an image dataset with precomputed numeric features,
    so this lesson stays free of image-decoding dependencies."""

    def __init__(self, samples: list[ImageSample]) -> None:
        self._samples = samples

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int) -> tuple[list[float], float]:
        sample = self._samples[index]
        return sample.features, sample.label
```

**`pipeline.py`** — hàm dùng chung cho mọi dataset/model (DA.2):

```python
"""Mini training pipeline combining Dataset (Protocol), BaseModel (ABC),
and TrainConfig (dataclass) — the Lesson 04 capstone project."""
from __future__ import annotations

import numpy as np

from base_model import BaseModel
from datasets import Dataset
from train_config import TrainConfig


def run_pipeline(dataset: Dataset, model: BaseModel, config: TrainConfig) -> None:
    """Train `model` on `dataset` using settings from `config`.

    This function references ONLY the Dataset protocol and the BaseModel
    abstract interface — never a concrete class — so any combination of
    dataset/model implementation can be swapped in with zero changes here.
    """
    X = np.array([dataset[i][0] for i in range(len(dataset))])
    y = np.array([dataset[i][1] for i in range(len(dataset))])

    print(f"[{config.tags}] Training on {len(dataset)} samples "
          f"(lr={config.learning_rate}, epochs={config.epochs})")

    model.fit(X, y)
    predictions = model.predict(X)
    mse = float(np.mean((predictions - y) ** 2))
    print(f"  -> {model.__class__.__name__} training MSE: {mse:.4f}")
```

**Demo — chạy 4 tổ hợp khác nhau, `run_pipeline` không đổi 1 dòng nào:**

```python
"""Demonstrates run_pipeline() working unchanged across dataset x model
combinations — proving the Protocol/ABC-based design from Sections 2.5-2.6."""
from base_model import DummyModel, LinearModelWrapper
from datasets import CSVDataset, ImageFolderDataset, ImageSample
from pipeline import run_pipeline
from train_config import TrainConfig

# --- Prepare a small CSV dataset ---
with open("demo_train.csv", "w", newline="", encoding="utf-8") as f:
    f.write("x1,x2,target\n1,2,5\n2,3,8\n3,4,11\n4,5,14\n")

csv_dataset = CSVDataset("demo_train.csv", target_column="target")

# --- Prepare a fake image dataset ---
image_dataset = ImageFolderDataset(
    [
        ImageSample([0.1, 0.2], 1.0),
        ImageSample([0.4, 0.1], 2.0),
        ImageSample([0.3, 0.3], 3.0),
    ]
)

config = TrainConfig(learning_rate=0.01, epochs=5, tags=["capstone-demo"])

print("=== Combination 1: CSVDataset + DummyModel ===")
run_pipeline(csv_dataset, DummyModel(), config)

print("\n=== Combination 2: CSVDataset + LinearModelWrapper ===")
run_pipeline(csv_dataset, LinearModelWrapper(), config)

print("\n=== Combination 3: ImageFolderDataset + DummyModel ===")
run_pipeline(image_dataset, DummyModel(), config)

print("\n=== Combination 4: ImageFolderDataset + LinearModelWrapper ===")
run_pipeline(image_dataset, LinearModelWrapper(), config)
```

**Điều cần quan sát (DA.3):** `run_pipeline()` chỉ được viết **1 lần duy nhất** ở `pipeline.py`, không hề nhắc tới `CSVDataset`, `ImageFolderDataset`, `DummyModel`, hay `LinearModelWrapper` theo tên — nó chỉ dựa vào `Dataset` protocol và `BaseModel` ABC. Đây chính là điều Phần 2.5 dạy, áp dụng vào 1 tình huống thật có nhiều tổ hợp hơn ví dụ gốc.
</details>

---

## 9. Đáp án Quiz

- [ ] Đã trả lời cả 3 câu bằng lời của bạn trong `SUBMISSION.md` trước khi mở phần dưới.

<details>
<summary><strong>Đáp án tham khảo</strong></summary>

**Câu 1: Khác nhau ABC vs Protocol?**
> ABC dùng nominal typing: lớp con phải kế thừa tường minh, kiểm tra ngay lúc khởi tạo object (`TypeError` nếu thiếu abstract method). Protocol dùng structural typing: object chỉ cần đúng cấu trúc, không cần kế thừa, kiểm tra chủ yếu ở static type checker hoặc `isinstance()` với `@runtime_checkable`. ABC cho phép chia sẻ code triển khai chung (concrete method), Protocol chỉ khai báo chữ ký.

**Câu 2: Khi nào dùng dataclass thay class thường?**
> Khi lớp chủ yếu chứa dữ liệu (config, kết quả, DTO), ít logic phức tạp — `@dataclass` tự sinh `__init__`/`__repr__`/`__eq__`, tiết kiệm boilerplate. Khi có logic phức tạp, nhiều phương thức, kế thừa sâu — dùng class thường.

**Câu 3: `__eq__` mà không có `__hash__` gây lỗi gì?**
> Python tự đặt `__hash__ = None` khi override `__eq__` (vì 2 object bằng nhau theo giá trị nhưng hash theo id cũ sẽ khác nhau, vi phạm nguyên tắc hash). Hệ quả: object không dùng làm dict key/phần tử set được nữa — `TypeError: unhashable type`. Sửa bằng cách tự định nghĩa lại `__hash__` dựa trên đúng field dùng trong `__eq__`, hoặc dùng `@dataclass(frozen=True)`.
</details>

---

## 10. Tổng kết & bước tiếp theo

- ✅ Nắm vững OOP core, ưu tiên composition khi phù hợp.
- ✅ Kỹ năng thiết kế interface bằng ABC/Protocol — nền tảng cho mọi pipeline ML (Dataset, Model, Optimizer, Trainer đều dùng lại pattern này).
- ✅ Pipeline tổng hợp chứng minh Liskov Substitution bằng 4 tổ hợp dataset × model thật, không chỉ 1 ví dụ đơn giản.

**Bài tiếp theo:** U01-05 — Type hints, Pydantic v2 và cấu hình.

---

## 11. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Bài tập Phần 2.1-2.6 (mỗi phần có ít nhất 1 bài đúng) | 3 |
| `BaseModel`/`TrainConfig`/`datasets.py` đúng chuẩn, độc lập | 2 |
| Dự án tổng hợp: `run_pipeline` chạy đúng ≥4 tổ hợp, không sửa dòng nào khi đổi dataset/model | 3 |
| Trả lời đúng 3/3 câu quiz | 2 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
