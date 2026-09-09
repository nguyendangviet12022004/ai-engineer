# U01-04 — OOP và Thiết kế Lớp trong Python

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 2 · **Giờ dự kiến:** 7 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.11-14 · Stanford CS106B (OOP concepts) · Refactoring Guru — Design Patterns
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.

---

## 1. Mục tiêu bài học

Sau bài này bạn phải:

1. Viết `class` đúng chuẩn: `__init__`, phân biệt instance attribute vs class attribute, dùng `@property` để kiểm soát truy cập.
2. Hiểu kế thừa, MRO (Method Resolution Order), `super()`, và biết khi nào nên ưu tiên **composition** thay vì inheritance.
3. Cài đặt các magic method quan trọng: `__repr__`, `__eq__`, `__hash__`, `__len__`, `__call__`, `__getitem__`.
4. Dùng `@dataclass` (kèm `frozen`, `field`, `default_factory`) và `NamedTuple` đúng chỗ.
5. Phân biệt **ABC** (nominal typing — kế thừa tường minh) vs **Protocol** (structural typing — "vịt kêu như vịt thì là vịt") — kỹ năng thiết kế interface quan trọng nhất cho pipeline ML.
6. Nhận diện và áp dụng đúng lúc: Enum, Singleton, Factory, Strategy pattern trong ngữ cảnh ML.
7. Xây `datasets.py` với `Protocol Dataset` + 2 cách cài đặt khác nhau — thay đổi implementation mà **không sửa 1 dòng nào** ở code dùng nó (Dependency Injection + nguyên lý Liskov Substitution).

---

## 2. Lý thuyết

### 2.1. Class cơ bản: `__init__`, instance vs class attribute, `@property`

```python
class Point:
    dimension = 2                 # CLASS attribute — CHIA SẺ giữa mọi instance

    def __init__(self, x: float, y: float) -> None:
        self.x = x                # INSTANCE attribute — RIÊNG của từng object
        self.y = y
```

**Bẫy kinh điển: sửa class attribute qua instance sẽ tạo ra instance attribute mới, không sửa class attribute gốc:**

```python
p1 = Point(0, 0)
p2 = Point(1, 1)
p1.dimension = 3          # tạo INSTANCE attribute mới tên "dimension" cho p1
print(p1.dimension)       # 3
print(p2.dimension)       # 2 — KHÔNG đổi, vì p2 vẫn đọc class attribute gốc
print(Point.dimension)    # 2 — class attribute gốc không hề bị ảnh hưởng
```

**`@property` — kiểm soát việc đọc/ghi attribute như 1 phương thức, nhưng gọi như attribute thường:**

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius     # dấu "_" đầu = quy ước "coi như private", không có enforcement thật

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def area(self) -> float:      # "computed property" — tính động, không lưu trạng thái riêng
        return 3.14159 * self._radius ** 2
```

```python
c = Circle(5)
c.area          # 78.53975 — gọi như attribute, không phải c.area()
c.radius = -1   # ValueError: radius must be positive — validate tự động khi gán
```

### 2.2. Kế thừa, MRO, `super()`, và "Composition over Inheritance"

```python
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "Woof"
```

**MRO (Method Resolution Order)** — thứ tự Python tìm phương thức khi có kế thừa đa cấp/đa lớp (multiple inheritance):

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
# (D, B, C, A, object) — Python dùng thuật toán C3 linearization
print(D().greet())   # "B" — tìm theo đúng thứ tự MRO, gặp B trước C
```

**`super()`** gọi phương thức của lớp cha theo đúng MRO (không phải "lớp cha trực tiếp" một cách ngây thơ — quan trọng khi kế thừa đa cấp):

```python
class Base:
    def __init__(self, name: str) -> None:
        self.name = name

class Derived(Base):
    def __init__(self, name: str, extra: int) -> None:
        super().__init__(name)    # gọi Base.__init__ đúng cách, tránh lặp code
        self.extra = extra
```

**"Composition over Inheritance" — nguyên tắc thiết kế quan trọng nhất của mục này:**

Kế thừa tạo ra quan hệ **"is-a"** rất chặt chẽ — lớp con bị ràng buộc chặt vào cấu trúc nội bộ của lớp cha, khó thay đổi độc lập. Composition tạo ra quan hệ **"has-a"** — linh hoạt hơn nhiều, đặc biệt quan trọng khi thiết kế pipeline ML (1 `Trainer` "has-a" `Optimizer`, "has-a" `Dataset`, thay vì `Trainer` kế thừa từ `Optimizer`).

```python
# Kế thừa (is-a) — RÀNG BUỘC CHẶT, khó đổi Optimizer lúc runtime
class SGDTrainer:
    def step(self): ...   # logic SGD hardcode ngay trong Trainer

# Composition (has-a) — LINH HOẠT, đổi được optimizer bất kỳ lúc nào
class Trainer:
    def __init__(self, optimizer: "Optimizer") -> None:
        self.optimizer = optimizer   # Trainer KHÔNG cần biết chi tiết bên trong optimizer

    def step(self) -> None:
        self.optimizer.update()
```

> **Quy tắc thực hành cho AI Engineer:** chỉ dùng kế thừa khi quan hệ "is-a" thực sự đúng về mặt ngữ nghĩa VÀ bạn cần tái sử dụng hành vi chung (như `CSVDataset` "is-a" `Dataset`). Khi chỉ cần "dùng chức năng của 1 object khác", luôn ưu tiên composition — sẽ thấy rõ lợi ích này khi thiết kế `Trainer` ở Unit 05.

### 2.3. Magic Methods (Dunder Methods)

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        """Unambiguous representation — used by repr(), and shown in REPL/debugger."""
        return f"Vector(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        """Value equality — used by ==. Without this, == compares identity (is)."""
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Required if you want instances usable as dict keys / set elements
        AFTER defining __eq__ (Python removes the default __hash__ automatically
        once __eq__ is overridden, unless you redefine __hash__ explicitly)."""
        return hash((self.x, self.y))

    def __len__(self) -> int:
        """Called by len(). Here we (arbitrarily) define it as vector dimension."""
        return 2

    def __call__(self, scale: float) -> "Vector":
        """Makes an instance callable like a function: vector_instance(2.0)."""
        return Vector(self.x * scale, self.y * scale)

    def __getitem__(self, index: int) -> float:
        """Enables indexing: vector[0], and iteration via automatic __iter__ fallback."""
        return (self.x, self.y)[index]
```

**Bảng magic method thường dùng nhất trong code AI Engineer:**

| Magic method | Được gọi khi | Ứng dụng thực tế |
|---|---|---|
| `__repr__` | `repr(obj)`, in ra REPL/debugger | Debug dễ dàng — luôn nên implement |
| `__eq__` | `obj1 == obj2` | So sánh 2 config/kết quả huấn luyện |
| `__hash__` | `hash(obj)`, dùng làm dict key/set element | Cache kết quả theo config |
| `__len__` | `len(obj)` | `Dataset.__len__` → tổng số mẫu |
| `__call__` | `obj(...)` | Model/transform gọi được như hàm: `model(x)` |
| `__getitem__` | `obj[i]` | `Dataset.__getitem__` → lấy 1 mẫu theo index |

### 2.4. `@dataclass` và `NamedTuple`

```python
from dataclasses import dataclass, field

@dataclass
class TrainConfig:
    learning_rate: float = 1e-3
    epochs: int = 10
    tags: list[str] = field(default_factory=list)   # KHÔNG viết tags: list = [] — mutable default!

@dataclass(frozen=True)     # frozen=True: immutable sau khi tạo, tự động hashable
class ImmutablePoint:
    x: float
    y: float
```

`@dataclass` **tự động sinh** `__init__`, `__repr__`, `__eq__` dựa trên các field khai báo — tiết kiệm rất nhiều boilerplate so với viết class thường. Dùng `field(default_factory=...)` cho mọi default là mutable (`list`/`dict`/`set`) — lý do y hệt bẫy mutable default argument đã học ở Bài 1.2.

**`NamedTuple`** — khi bạn cần 1 cấu trúc dữ liệu **immutable, nhẹ, giống tuple** hơn là 1 object đầy đủ:

```python
from typing import NamedTuple

class EvalResult(NamedTuple):
    accuracy: float
    f1_score: float

result = EvalResult(accuracy=0.92, f1_score=0.89)
result.accuracy       # 0.92 — truy cập như attribute
a, f = result          # unpack như tuple thường
```

**Khi nào dùng dataclass, khi nào dùng class thường?**

| Tình huống | Lựa chọn |
|---|---|
| Chỉ chứa dữ liệu, ít/không có logic phức tạp (config, kết quả trả về) | `@dataclass` |
| Cần immutable + hashable, nhẹ, giống tuple | `NamedTuple` |
| Có logic nghiệp vụ phức tạp, nhiều phương thức, cần kế thừa sâu | `class` thường |

### 2.5. ABC vs Protocol — thiết kế interface cho pipeline ML

Đây là phần **quan trọng nhất** của bài học — quyết định cách bạn thiết kế mọi pipeline trong suốt lộ trình.

**ABC (Abstract Base Class) — "nominal typing"**: lớp con phải **kế thừa tường minh** từ ABC mới được coi là hợp lệ.

```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def fit(self, X, y) -> None: ...

    @abstractmethod
    def predict(self, X): ...

class LinearModelWrapper(BaseModel):    # PHẢI kế thừa BaseModel tường minh
    def fit(self, X, y) -> None: ...
    def predict(self, X): ...
```

Nếu quên implement 1 abstract method, Python ném lỗi **ngay lúc khởi tạo object** (`TypeError: Can't instantiate abstract class ... with abstract method predict`) — phát hiện lỗi sớm, rất hữu ích.

**Protocol — "structural typing"**: **không cần kế thừa**. Miễn object có đúng các phương thức/attribute yêu cầu (giống hệt "duck typing": *"nếu nó đi như vịt và kêu như vịt, thì nó là vịt"*), nó được coi là hợp lệ với Protocol đó.

```python
from typing import Protocol

class Dataset(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, index: int): ...

class CSVDataset:            # KHÔNG kế thừa Dataset, vẫn hợp lệ!
    def __len__(self) -> int: ...
    def __getitem__(self, index: int): ...

def train(dataset: Dataset) -> None:   # type checker (mypy/pyright) chấp nhận CSVDataset
    ...
```

**Bảng so sánh quyết định:**

| | ABC | Protocol |
|---|---|---|
| Cách "đăng ký" hợp lệ | Kế thừa tường minh | Chỉ cần đúng cấu trúc (không kế thừa) |
| Kiểm tra lúc nào | Runtime (lúc khởi tạo object) | Static (mypy/pyright lúc code, hoặc `isinstance()` với `@runtime_checkable`) |
| Có thể chia sẻ code triển khai (concrete method) không | Có | Không (chỉ khai báo chữ ký phương thức) |
| Phù hợp khi | Bạn kiểm soát toàn bộ class hierarchy, muốn ép buộc implement | Bạn cần tương thích với class **có sẵn** từ thư viện khác (không sửa được), hoặc muốn interface lỏng, dễ mock khi test |
| Ví dụ trong lộ trình | `BaseModel` (fit/predict/save/load) | `Dataset` (`__len__`/`__getitem__`) — để tương thích cả `torch.utils.data.Dataset` lẫn dataset tự viết |

> **Quyết định thực hành:** dùng **ABC** khi bạn thiết kế 1 họ class từ đầu và muốn ép buộc cấu trúc chung (như `BaseModel` trong BT1). Dùng **Protocol** khi bạn muốn định nghĩa "hợp đồng" (contract) mà nhiều loại object khác nhau — kể cả object từ thư viện ngoài bạn không kiểm soát được — có thể thoả mãn mà không cần sửa code của chúng.

### 2.6. Enum, Singleton, Factory, Strategy trong ngữ cảnh ML

```python
from enum import Enum, auto

class ModelType(Enum):
    """Enum thay cho string/int rời rạc — tránh lỗi gõ nhầm 'linaer' thay vì 'linear'."""
    LINEAR = auto()
    RANDOM_FOREST = auto()
    NEURAL_NET = auto()
```

```python
class ModelRegistry:
    """Singleton — đảm bảo chỉ có 1 instance trong toàn bộ ứng dụng.
    Dùng khi cần trạng thái dùng chung toàn cục (registry model đã load,
    connection pool...). Cẩn thận: lạm dụng Singleton gây khó test."""
    _instance: "ModelRegistry | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models = {}
        return cls._instance
```

```python
def model_factory(model_type: ModelType) -> "BaseModel":
    """Factory pattern — tách logic 'tạo object nào' ra khỏi nơi sử dụng.
    Thêm model mới chỉ cần sửa factory, không cần sửa code gọi nó."""
    if model_type == ModelType.LINEAR:
        return LinearModelWrapper()
    if model_type == ModelType.RANDOM_FOREST:
        return RandomForestWrapper()
    raise ValueError(f"Unknown model type: {model_type}")
```

```python
class TrainingStrategy(Protocol):
    """Strategy pattern — đóng gói 1 thuật toán/hành vi thành object hoán đổi được.
    Ví dụ: chiến lược chia train/val khác nhau (random split, time-based split,
    group-based split) mà không cần if/else rải rác khắp code."""
    def split(self, dataset, ratio: float): ...
```

Cả 4 pattern này sẽ xuất hiện lặp lại xuyên suốt lộ trình — đặc biệt Factory + Strategy là 2 pattern dùng nhiều nhất khi thiết kế pipeline huấn luyện linh hoạt (Unit 04, 05, 11).

---

## 3. Bài tập thực hành

### BT1 — `BaseModel` (ABC) + 2 lớp kế thừa

Xây `BaseModel` (ABC) với 4 abstract method: `fit`, `predict`, `save`, `load`. Cài 2 lớp kế thừa: `LinearModelWrapper` (bọc `sklearn.linear_model.LinearRegression` hoặc tự cài đơn giản) và `DummyModel` (luôn dự đoán giá trị trung bình của `y` lúc `fit`).

### BT2 — `@dataclass TrainConfig` có validate

Viết `TrainConfig` (dataclass) với các field `learning_rate`, `epochs`, và validate: `learning_rate > 0`, `epochs > 0` — ném `ValueError` nếu vi phạm, kiểm tra ngay sau khi khởi tạo (dùng `__post_init__`).

### Sản phẩm chính — `datasets.py`

Định nghĩa `Protocol Dataset` (`__len__`, `__getitem__`) + 2 lớp cài đặt: `CSVDataset` (đọc dữ liệu từ file CSV) và `ImageFolderDataset` (giả lập đọc ảnh từ thư mục, chỉ cần trả về đường dẫn file + nhãn, không cần đọc ảnh thật). Viết 1 hàm `train(dataset: Dataset)` in ra vài mẫu — chứng minh hàm này chạy được với **cả 2** implementation mà không sửa gì.

### Tiêu chí hoàn thành (DoD)

- [ ] `BaseModel` ném lỗi ngay khi khởi tạo 1 lớp con thiếu implement method.
- [ ] `TrainConfig()` với `learning_rate=-1` ném `ValueError` ngay lập tức.
- [ ] Hàm `train(dataset)` chạy đúng với cả `CSVDataset` và `ImageFolderDataset` — **không sửa 1 dòng nào** trong `train()` khi đổi dataset (đúng nguyên lý Liskov Substitution).
- [ ] Trả lời đúng 3 câu quiz bằng lời của bạn.

---

## 4. Lời giải chi tiết

### 4.1. Lời giải BT1 — `BaseModel` (ABC)

```python
"""Abstract base class for ML models with a unified fit/predict/save/load API."""
from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np


class BaseModel(ABC):
    """Every concrete model in this codebase must implement this contract,
    so training/evaluation code can work with any model interchangeably."""

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model on features X and targets y."""

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predictions for features X."""

    def save(self, path: str) -> None:
        """Persist the model to disk. Shared implementation via pickle;
        override only if a model needs a custom serialization format."""
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> "BaseModel":
        """Load a previously saved model from disk."""
        with open(path, "rb") as f:
            model = pickle.load(f)
        if not isinstance(model, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__}")
        return model


class DummyModel(BaseModel):
    """Baseline model: always predicts the mean of y seen during fit().
    Useful as a sanity-check floor that any real model must beat."""

    def __init__(self) -> None:
        self._mean_value: float | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._mean_value = float(np.mean(y))

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._mean_value is None:
            raise RuntimeError("Call fit() before predict()")
        return np.full(shape=(len(X),), fill_value=self._mean_value)


class LinearModelWrapper(BaseModel):
    """Simple linear regression wrapper implemented via the closed-form
    normal equation, with no external ML library dependency."""

    def __init__(self) -> None:
        self._weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # Add a bias column of ones so the model can learn an intercept.
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        # Normal equation: w = (X^T X)^-1 X^T y
        self._weights = np.linalg.pinv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._weights is None:
            raise RuntimeError("Call fit() before predict()")
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        return X_with_bias @ self._weights
```

**Giải thích quyết định thiết kế:**
- `save`/`load` là **concrete method** (có sẵn implementation), không phải `abstractmethod` — vì logic lưu/nạp bằng pickle giống hệt nhau cho mọi model con, không cần lớp con tự viết lại. Đây là điểm khác biệt then chốt so với Protocol: ABC cho phép **chia sẻ code triển khai**.
- `LinearModelWrapper` dùng normal equation (đã học ở Bài 2.2 trong roadmap) thay vì phụ thuộc `sklearn` — giữ bài học độc lập, không cần cài thêm thư viện ngoài.

### 4.2. Lời giải BT2 — `TrainConfig` có validate

```python
"""Training configuration with validation on construction."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrainConfig:
    """Configuration for a training run. Validated immediately on creation
    so invalid configs fail fast, before any expensive training starts."""

    learning_rate: float = 1e-3
    epochs: int = 10
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Called automatically right after __init__ by @dataclass."""
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be > 0, got {self.learning_rate}")
        if self.epochs <= 0:
            raise ValueError(f"epochs must be > 0, got {self.epochs}")
```

```python
TrainConfig(learning_rate=0.01, epochs=5)          # OK
TrainConfig(learning_rate=-1, epochs=5)             # ValueError: learning_rate must be > 0, got -1
```

### 4.3. Lời giải chính — `datasets.py` (Protocol + 2 implementation)

```python
"""Dataset abstraction using structural typing (Protocol) so training code
can work with any dataset-like object without requiring inheritance."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Dataset(Protocol):
    """Structural contract: any object with __len__ and __getitem__
    satisfies this protocol, with no need to inherit from it."""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> tuple[dict, str]: ...


class CSVDataset:
    """Loads rows from a CSV file. Does NOT inherit from Dataset —
    it satisfies the protocol purely by having the right methods."""

    def __init__(self, file_path: str, label_column: str) -> None:
        self.label_column = label_column
        with open(file_path, newline="", encoding="utf-8") as f:
            self._rows = list(csv.DictReader(f))

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> tuple[dict, str]:
        row = dict(self._rows[index])
        label = row.pop(self.label_column)
        return row, label


@dataclass
class ImageSample:
    """One (image_path, label) pair for ImageFolderDataset."""

    image_path: str
    label: str


class ImageFolderDataset:
    """Simulates reading (image_path, label) pairs from a folder structure
    like root/<label>/<image>.jpg — without actually decoding image bytes,
    to keep this lesson dependency-free."""

    def __init__(self, samples: list[ImageSample]) -> None:
        self._samples = samples

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int) -> tuple[dict, str]:
        sample = self._samples[index]
        return {"image_path": sample.image_path}, sample.label


def train(dataset: Dataset) -> None:
    """Training loop stub that works with ANY object satisfying the
    Dataset protocol — it never needs to know the concrete class.
    This is the point of the exercise: swap CSVDataset <-> ImageFolderDataset
    below with zero changes to this function (Liskov Substitution Principle)."""
    print(f"Training on {len(dataset)} samples")
    for i in range(min(3, len(dataset))):
        features, label = dataset[i]
        print(f"  sample {i}: features={features}, label={label}")
```

### 4.4. Demo — chứng minh hàm `train()` không cần sửa khi đổi dataset

```python
"""Demonstrates that train() works unchanged with two different Dataset
implementations, proving the Protocol-based design achieves the DoD."""
from datasets import CSVDataset, ImageFolderDataset, ImageSample, train

# --- CSVDataset ---
with open("demo_data.csv", "w", newline="", encoding="utf-8") as f:
    f.write("age,income,churn\n30,50000,yes\n45,80000,no\n22,30000,yes\n")

csv_dataset = CSVDataset("demo_data.csv", label_column="churn")
train(csv_dataset)   # <-- exact same function

print()

# --- ImageFolderDataset ---
image_dataset = ImageFolderDataset(
    [
        ImageSample("root/cat/001.jpg", "cat"),
        ImageSample("root/dog/001.jpg", "dog"),
        ImageSample("root/cat/002.jpg", "cat"),
    ]
)
train(image_dataset)   # <-- exact same function, zero changes needed
```

### 4.5. Đáp án Quiz

**Câu 1: Khác nhau ABC vs Protocol?**
> ABC dùng **nominal typing**: lớp con phải kế thừa tường minh (`class Foo(BaseModel)`) để được coi là hợp lệ, và Python kiểm tra ngay lúc **khởi tạo object** — nếu thiếu implement 1 abstract method, ném `TypeError` ngay lập tức. Protocol dùng **structural typing**: object chỉ cần có đúng các phương thức/attribute yêu cầu (không cần kế thừa) là được coi là hợp lệ, kiểm tra chủ yếu ở mức **static type checker** (mypy/pyright) khi viết code, hoặc runtime nếu đánh dấu `@runtime_checkable` và dùng `isinstance()`. ABC còn cho phép chia sẻ code triển khai chung (concrete method như `save`/`load`), Protocol thì không — Protocol chỉ khai báo "chữ ký" (signature), không có phần thân hàm thật.

**Câu 2: Khi nào dùng dataclass thay class thường?**
> Khi lớp đó chủ yếu **chứa dữ liệu** (config, kết quả, DTO — data transfer object) và không có nhiều logic nghiệp vụ phức tạp. `@dataclass` tự sinh `__init__`, `__repr__`, `__eq__` dựa trên field khai báo, tiết kiệm rất nhiều boilerplate. Khi lớp có logic phức tạp, nhiều phương thức tương tác với trạng thái nội bộ, hoặc cần kế thừa sâu nhiều tầng với hành vi ghi đè phức tạp — nên dùng `class` thường để kiểm soát rõ ràng hơn.

**Câu 3: `__eq__` mà không có `__hash__` gây lỗi gì?**
> Theo mặc định, mọi object Python đều hashable (dựa trên `id()`). Nhưng khi bạn **override `__eq__`** (định nghĩa lại so sánh bằng theo giá trị thay vì danh tính), Python **tự động đặt `__hash__` thành `None`** — vì nếu 2 object có `==` là `True` (theo giá trị) nhưng lại có hash khác nhau (theo id cũ), điều đó vi phạm nguyên tắc bắt buộc của hash: "2 object bằng nhau phải có cùng hash". Hệ quả: object đó **không còn dùng làm dict key hay phần tử set được nữa** — gọi `hash(obj)` sẽ ném `TypeError: unhashable type`. Muốn vừa có `__eq__` theo giá trị vừa hashable được, phải **tự định nghĩa lại `__hash__`** dựa trên đúng những field dùng để so sánh trong `__eq__` (như ví dụ `Vector` ở mục 2.3), hoặc dùng `@dataclass(frozen=True)` — tự động sinh cả `__eq__` lẫn `__hash__` nhất quán với nhau.

---

## 5. Tổng kết & bước tiếp theo

Bạn đã có:
- ✅ Nắm vững OOP core (class, kế thừa, MRO, magic method) và biết ưu tiên composition khi phù hợp.
- ✅ Kỹ năng thiết kế interface bằng ABC/Protocol — nền tảng cho **mọi** pipeline ML trong lộ trình (Dataset, Model, Optimizer, Trainer đều sẽ dùng lại pattern này).
- ✅ `datasets.py` chứng minh được nguyên lý Liskov Substitution bằng ví dụ cụ thể — kỹ năng sẽ dùng lại xuyên suốt Unit 04, 05, 09.

**Bài tiếp theo:** U01-05 — Type hints, Pydantic v2 và cấu hình.

---

## 6. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| `BaseModel` (ABC) đúng chuẩn, `DummyModel` + `LinearModelWrapper` hoạt động đúng | 3 |
| `TrainConfig` validate đúng, ném `ValueError` khi vi phạm | 2 |
| `datasets.py`: Protocol đúng, 2 implementation hoạt động, `train()` không cần sửa khi đổi dataset | 3 |
| Trả lời đúng 3/3 câu quiz bằng lời của bạn | 2 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
