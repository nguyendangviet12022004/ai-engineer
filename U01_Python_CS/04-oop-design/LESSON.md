# U01-04 — OOP và Thiết kế Lớp trong Python

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 2 · **Giờ dự kiến:** 7 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.11-14 · Stanford CS106B (OOP concepts) · Refactoring Guru — Design Patterns
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.

## Dự án của bài học: package `mlkit`

Bài này xây **1 project mới, độc lập** — package `mlkit`, một bộ khung huấn luyện mô hình tí hon. **Không liên quan tới `mytools` của Bài 03** — không cài đặt CLI/`pyproject.toml` (đó là kỹ năng đã học riêng), chỉ cần Python thuần + `numpy`, chạy trực tiếp bằng `python demo_train.py`. Mọi bài tập trong bài học đều là 1 bước xây dựng package thật này.

```
mlkit-project/                    # thư mục mới, độc lập
├── demo_train.py                # -> Phần 2.7 (điểm hội tụ cuối bài)
├── sample_data.csv
└── mlkit/
    ├── __init__.py
    ├── config.py                 # -> Phần 2.4 (TrainConfig)
    ├── models/
    │   ├── __init__.py
    │   ├── base.py                 # -> Phần 2.1, 2.5 (BaseModel ABC)
    │   ├── dummy.py                  # -> Phần 2.2
    │   ├── linear.py                   # -> Phần 2.2
    │   └── registry.py                   # -> Phần 2.6 (ModelType + factory)
    ├── data/
    │   ├── __init__.py
    │   └── datasets.py                     # -> Phần 2.3, 2.5 (Dataset Protocol, CSVDataset)
    └── pipeline.py                            # -> Phần 2.2, 2.7 (Trainer, run_pipeline)
```

> **Cách dùng file này:** Đọc lý thuyết từng phần → tạo đúng file/class được chỉ định trong `mlkit/` → tick ☐ → ☑. Cuối bài, `python demo_train.py` chạy huấn luyện thật.

---

## 1. Mục tiêu bài học

- [ ] Viết `class` đúng chuẩn, phân biệt instance vs class attribute, dùng `@property`.
- [ ] Hiểu kế thừa, `super()`, ưu tiên composition khi phù hợp.
- [ ] Cài đặt magic method: `__repr__`, `__len__`, `__getitem__`.
- [ ] Dùng `@dataclass` đúng chỗ.
- [ ] Phân biệt ABC vs Protocol — kỹ năng thiết kế interface cho pipeline ML.
- [ ] Nhận diện Enum, Factory, Strategy pattern.
- [ ] **Sản phẩm:** `demo_train.py` huấn luyện được cả `LinearModel` và `DummyModel` trên cùng dữ liệu, chỉ đổi 1 tham số.

---

## 2. Phần 2.1 — Class, `@property`: bắt đầu `mlkit/models/base.py`

### Lý thuyết

```python
class Point:
    dimension = 2                 # CLASS attribute — CHIA SẺ giữa mọi instance
    def __init__(self, x: float, y: float) -> None:
        self.x = x                # INSTANCE attribute — RIÊNG của từng object
        self.y = y
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
```

Trong thư viện ML thật (giống scikit-learn/PyTorch), mọi model đều có 1 thuộc tính **`is_fitted`** — cho biết `fit()` đã được gọi hay chưa, để `predict()` báo lỗi rõ ràng thay vì lỗi mơ hồ. `mlkit.models.base.BaseModel` sẽ dùng `@property` này.

### Bài tập 2.1 — Bắt đầu `mlkit/models/base.py` với `is_fitted`

- [ ] **BT 2.1.1** — Tạo thư mục dự án `mlkit-project/` với package con `mlkit/models/` (có `__init__.py` rỗng tạm thời, sẽ điền ở Phần 2.6).
- [ ] **BT 2.1.2** — Tạo `mlkit/models/base.py`. Viết class tạm `_FittableMixin` với `self._is_fitted: bool = False` trong `__init__`, và `@property is_fitted` chỉ đọc trả về giá trị đó (chưa có `fit()`/`predict()` — sẽ hoàn thiện thành ABC ở Phần 2.5).

<details>
<summary><strong>Lời giải chi tiết Phần 2.1</strong></summary>

**`mlkit/models/base.py`** (phiên bản đầu, sẽ mở rộng thành ABC hoàn chỉnh ở Phần 2.5):

```python
"""Base building blocks for all mlkit models."""
from __future__ import annotations


class _FittableMixin:
    """Tracks whether a model has been fit yet, via a read-only property.

    This will become part of BaseModel once we add the ABC contract in
    Section 2.5 — kept separate here only to introduce @property first.
    """

    def __init__(self) -> None:
        self._is_fitted: bool = False

    @property
    def is_fitted(self) -> bool:
        """Read-only — there is intentionally no setter. Only fit() (added
        later) is allowed to flip this flag internally."""
        return self._is_fitted
```

```python
mixin = _FittableMixin()
print(mixin.is_fitted)   # False

try:
    mixin.is_fitted = True   # AttributeError: property 'is_fitted' has no setter
except AttributeError as e:
    print("Error:", e)
```
</details>

---

## 3. Phần 2.2 — Kế thừa, `super()`, Composition: `models/dummy.py`, `models/linear.py`, `pipeline.py`

### Lý thuyết

`super()` gọi phương thức lớp cha đúng chuẩn, tránh lặp code:

```python
class Base:
    def __init__(self, name: str) -> None:
        self.name = name

class Derived(Base):
    def __init__(self, name: str, extra: int) -> None:
        super().__init__(name)   # gọi Base.__init__
        self.extra = extra
```

**"Composition over Inheritance"** — kế thừa tạo quan hệ "is-a" chặt chẽ, composition tạo quan hệ "has-a" linh hoạt hơn. `mlkit.pipeline.Trainer` sẽ **"has-a" model** (composition), không kế thừa model:

```python
class Trainer:
    def __init__(self, model) -> None:
        self.model = model   # Trainer HAS-A model, không kế thừa nó
```

> **Quy tắc thực hành:** chỉ kế thừa khi "is-a" đúng ngữ nghĩa. `DummyModel`/`LinearModel` sẽ kế thừa `BaseModel` (đúng "is-a"); `Trainer` sẽ composition với model (không phải "is-a Model").

### Bài tập 2.2 — `DummyModel`, `LinearModel`, `Trainer`

- [ ] **BT 2.2.1** — Tạo `mlkit/models/dummy.py`: class `DummyModel(_FittableMixin)` — dùng `super().__init__()` gọi đúng constructor cha. `fit(self, X, y)` lưu `self._mean_value = mean(y)` và set `self._is_fitted = True`. `predict(self, X)` trả về mảng toàn giá trị `_mean_value`.
- [ ] **BT 2.2.2** — Tạo `mlkit/models/linear.py`: class `LinearModel(_FittableMixin)` tương tự, `fit()` giải bằng normal equation (`np.linalg.pinv`), `predict()` nhân ma trận.
- [ ] **BT 2.2.3** — Tạo `mlkit/pipeline.py`: class `Trainer` — **composition**, nhận `model` bất kỳ trong constructor, có `train(self, X, y)` gọi `self.model.fit(X, y)`. Chứng minh cùng 1 `Trainer` chạy được với cả `DummyModel()` và `LinearModel()` mà không cần sửa `Trainer`.

<details>
<summary><strong>Lời giải chi tiết Phần 2.2</strong></summary>

**`mlkit/models/dummy.py`:**

```python
"""Baseline model: always predicts the mean of y seen during fit()."""
from __future__ import annotations

import numpy as np

from mlkit.models.base import _FittableMixin


class DummyModel(_FittableMixin):
    """Predicts the mean of y. Useful as a sanity-check floor that any
    real model in mlkit must beat."""

    def __init__(self) -> None:
        super().__init__()   # sets self._is_fitted = False via the mixin
        self._mean_value: float | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._mean_value = float(np.mean(y))
        self._is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Call fit() before predict()")
        return np.full(shape=(len(X),), fill_value=self._mean_value)
```

**`mlkit/models/linear.py`:**

```python
"""Linear regression via the closed-form normal equation, no external
ML library dependency beyond numpy."""
from __future__ import annotations

import numpy as np

from mlkit.models.base import _FittableMixin


class LinearModel(_FittableMixin):
    def __init__(self) -> None:
        super().__init__()
        self._weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        self._weights = np.linalg.pinv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y
        self._is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Call fit() before predict()")
        X_with_bias = np.column_stack([np.ones(len(X)), X])
        return X_with_bias @ self._weights
```

**`mlkit/pipeline.py`** (phần `Trainer`, sẽ bổ sung `run_pipeline` ở Phần 2.7):

```python
"""Training orchestration for mlkit. Trainer uses composition, not
inheritance — it works with ANY model exposing fit()/predict()."""
from __future__ import annotations

import numpy as np


class Trainer:
    """HAS-A model (composition) — never inherits from any model class,
    so swapping DummyModel <-> LinearModel requires zero changes here."""

    def __init__(self, model) -> None:
        self.model = model

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
```

**Chứng minh cùng `Trainer` chạy với 2 model:**

```python
import numpy as np
from mlkit.models.dummy import DummyModel
from mlkit.models.linear import LinearModel
from mlkit.pipeline import Trainer

X = np.array([[1], [2], [3], [4]])
y = np.array([3.0, 5.0, 7.0, 9.0])   # y = 2x + 1

trainer1 = Trainer(DummyModel())
trainer1.train(X, y)
print(trainer1.model.predict(X))   # [6. 6. 6. 6.] — luôn dự đoán trung bình

trainer2 = Trainer(LinearModel())   # đổi model, KHÔNG sửa Trainer
trainer2.train(X, y)
print(trainer2.model.predict(X))   # [3. 5. 7. 9.] — khớp gần như tuyệt đối
```
</details>

---

## 4. Phần 2.3 — Magic Methods: `mlkit/data/datasets.py` (`CSVDataset`)

### Lý thuyết

```python
class Example:
    def __repr__(self) -> str: ...        # repr(obj) — debug
    def __len__(self) -> int: ...          # len(obj)
    def __getitem__(self, i): ...          # obj[i]
```

`mlkit.data.datasets.CSVDataset` cần **`__len__`** và **`__getitem__`** để tương thích chuẩn "dataset" (đúng cấu trúc mà `torch.utils.data.Dataset` dùng — sẽ gặp lại ở Unit 05). Thêm **`__repr__`** để debug dễ dàng khi in dataset ra console.

### Bài tập 2.3 — `CSVDataset` với magic methods

- [ ] **BT 2.3.1** — Tạo `mlkit/data/__init__.py` (rỗng) và `mlkit/data/datasets.py`. Viết class `CSVDataset` đọc `(features, target)` từ file CSV, cài `__len__` và `__getitem__`.
- [ ] **BT 2.3.2** — Thêm `__repr__` cho `CSVDataset` in ra dạng `CSVDataset(file_path='...', n_samples=N)`.
- [ ] **BT 2.3.3** — Chứng minh `CSVDataset` dùng được với `len(dataset)`, `dataset[0]`, và duyệt qua toàn bộ mẫu bằng vòng lặp.

<details>
<summary><strong>Lời giải chi tiết Phần 2.3</strong></summary>

**`mlkit/data/datasets.py`** (phần `CSVDataset`, `Dataset` Protocol thêm ở Phần 2.5):

```python
"""Dataset classes for mlkit, built around __len__/__getitem__."""
from __future__ import annotations

import csv


class CSVDataset:
    """Loads (features, target) pairs from a CSV file."""

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
```

```python
from mlkit.data.datasets import CSVDataset

with open("sample_data.csv", "w", newline="", encoding="utf-8") as f:
    f.write("x1,x2,target\n1,2,5\n2,3,8\n3,4,11\n")

dataset = CSVDataset("sample_data.csv", target_column="target")
print(dataset)               # CSVDataset(file_path='sample_data.csv', n_samples=3)
print(len(dataset))          # 3
print(dataset[0])            # ([1.0, 2.0], 5.0)

for i in range(len(dataset)):
    features, target = dataset[i]
    print(features, "->", target)
```
</details>

---

## 5. Phần 2.4 — `@dataclass`: `mlkit/config.py` (`TrainConfig`)

### Lý thuyết

```python
from dataclasses import dataclass, field

@dataclass
class TrainConfig:
    learning_rate: float = 1e-3
    tags: list[str] = field(default_factory=list)   # KHÔNG viết tags: list = []
```

`@dataclass` tự sinh `__init__`, `__repr__`, `__eq__` — phù hợp cho `TrainConfig` (chủ yếu chứa dữ liệu, ít logic). `field(default_factory=list)` tránh bẫy mutable default (Bài 1.2) cho field `tags`.

### Bài tập 2.4 — `mlkit/config.py`

- [ ] **BT 2.4.1** — Tạo `mlkit/config.py`: `@dataclass TrainConfig` với `model_type: str = "linear"`, `precision: int = 4`, `tags: list[str] = field(default_factory=list)`.
- [ ] **BT 2.4.2** — Validate bằng `__post_init__`: `precision > 0`, ném `ValueError` nếu vi phạm.
- [ ] **BT 2.4.3** — Chứng minh 2 instance `TrainConfig()` khác nhau không chia sẻ chung `tags` (độc lập nhờ `default_factory`).

<details>
<summary><strong>Lời giải chi tiết Phần 2.4</strong></summary>

**`mlkit/config.py`:**

```python
"""Training configuration for mlkit, validated on construction."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrainConfig:
    """Configuration for a training run. Validated immediately so an
    invalid config fails fast, before any training starts."""

    model_type: str = "linear"
    precision: int = 4
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.precision <= 0:
            raise ValueError(f"precision must be > 0, got {self.precision}")
```

```python
from mlkit.config import TrainConfig

TrainConfig(model_type="dummy", precision=2)   # OK
try:
    TrainConfig(precision=0)
except ValueError as e:
    print("Error:", e)

c1, c2 = TrainConfig(), TrainConfig()
c1.tags.append("run1")
print(c1.tags, c2.tags)   # ['run1'] []  — độc lập
```
</details>

---

## 6. Phần 2.5 — ABC vs Protocol: hoàn thiện `BaseModel` và `Dataset`

### Lý thuyết

Phần **quan trọng nhất** bài học.

**ABC — "nominal typing"**: lớp con phải kế thừa tường minh, quên implement → `TypeError` ngay lúc khởi tạo.

```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def fit(self, X, y) -> None: ...
    @abstractmethod
    def predict(self, X): ...
```

**Protocol — "structural typing"**: không cần kế thừa, chỉ cần đúng cấu trúc.

```python
from typing import Protocol

class Dataset(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, index: int): ...
```

`CSVDataset` (Phần 2.3) **đã** có `__len__`/`__getitem__` — nó tự động thoả mãn `Dataset` Protocol **mà không cần sửa gì**. Đây chính là điểm mạnh của Protocol: bạn viết class trước, định nghĩa "hợp đồng" sau, và class cũ tự động hợp lệ.

| | ABC | Protocol |
|---|---|---|
| Đăng ký hợp lệ | Kế thừa tường minh | Đúng cấu trúc, không kế thừa |
| Dùng trong `mlkit` cho | `BaseModel` (ép buộc `DummyModel`/`LinearModel` implement đủ `fit`/`predict`) | `Dataset` (để `CSVDataset` và mọi dataset tương lai — kể cả từ PyTorch — đều hợp lệ) |

### Bài tập 2.5 — Hoàn thiện `BaseModel` (ABC) và `Dataset` (Protocol)

- [ ] **BT 2.5.1** — Sửa `mlkit/models/base.py`: đổi `_FittableMixin` thành `BaseModel(ABC)` với `@abstractmethod fit` và `@abstractmethod predict`, **giữ nguyên** `@property is_fitted`. Thêm concrete method `save(path)`/classmethod `load(path)` dùng `pickle` (không phải abstract — mọi model dùng chung logic này).
- [ ] **BT 2.5.2** — Sửa `DummyModel(_FittableMixin)` và `LinearModel(_FittableMixin)` (Phần 2.2) thành kế thừa `BaseModel` mới.
- [ ] **BT 2.5.3** — Thêm `Dataset(Protocol)` vào `mlkit/data/datasets.py`, đặt phía trên `CSVDataset`. Chứng minh `isinstance(csv_dataset_instance, Dataset)` trả `True` dù `CSVDataset` không kế thừa `Dataset` (dùng `@runtime_checkable`).
- [ ] **BT 2.5.4** — Cố tình viết 1 class con của `BaseModel` thiếu `predict`, chứng minh `TypeError` khi khởi tạo.

<details>
<summary><strong>Lời giải chi tiết Phần 2.5</strong></summary>

**`mlkit/models/base.py`** (bản hoàn chỉnh, thay thế `_FittableMixin`):

```python
"""Base building blocks for all mlkit models."""
from __future__ import annotations

import pickle
from abc import ABC, abstractmethod

import numpy as np


class BaseModel(ABC):
    """Every concrete model in mlkit must implement this contract, so
    Trainer/pipeline code can work with any model interchangeably."""

    def __init__(self) -> None:
        self._is_fitted: bool = False

    @property
    def is_fitted(self) -> bool:
        """Read-only — only fit() is allowed to flip this internally."""
        return self._is_fitted

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model on features X and targets y."""

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predictions for features X."""

    def save(self, path: str) -> None:
        """Shared implementation — subclasses do not override this."""
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> "BaseModel":
        with open(path, "rb") as f:
            model = pickle.load(f)
        if not isinstance(model, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__}")
        return model
```

**Sửa `mlkit/models/dummy.py`** — chỉ đổi import và class cha:

```python
from mlkit.models.base import BaseModel   # thay _FittableMixin

class DummyModel(BaseModel):                # thay _FittableMixin
    ...   # phần thân giữ nguyên như Phần 2.2
```

**Sửa `mlkit/models/linear.py`** tương tự — đổi `_FittableMixin` thành `BaseModel`.

**Thêm `Dataset` Protocol vào `mlkit/data/datasets.py`** (đặt trước class `CSVDataset`):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Dataset(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> tuple[list[float], float]: ...
```

```python
from mlkit.data.datasets import CSVDataset, Dataset

dataset = CSVDataset("sample_data.csv", target_column="target")
print(isinstance(dataset, Dataset))   # True — dù CSVDataset không hề kế thừa Dataset!
print(CSVDataset.__bases__)             # (<class 'object'>,) — chứng minh không kế thừa
```

**BT 2.5.4 — chứng minh ABC ép buộc implement:**

```python
from mlkit.models.base import BaseModel

class IncompleteModel(BaseModel):
    def fit(self, X, y):
        pass
    # predict bị thiếu — cố ý

try:
    IncompleteModel()
except TypeError as e:
    print("Error:", e)
    # Can't instantiate abstract class IncompleteModel without an
    # implementation for abstract method 'predict'
```
</details>

---

## 7. Phần 2.6 — Enum, Factory: `mlkit/models/registry.py`

### Lý thuyết

```python
from enum import Enum

class ModelType(Enum):
    LINEAR = "linear"
    DUMMY = "dummy"

def create_model(model_type: ModelType) -> "BaseModel":
    """Factory pattern — tách 'tạo model nào' khỏi nơi sử dụng.
    Thêm model mới chỉ cần sửa factory, không cần sửa nơi gọi."""
    if model_type == ModelType.LINEAR:
        return LinearModel()
    if model_type == ModelType.DUMMY:
        return DummyModel()
    raise ValueError(f"Unknown model type: {model_type}")
```

Đây chính là cơ chế `demo_train.py` sẽ dùng ở Phần 2.7 — chỉ cần biết tên chuỗi `"linear"`/`"dummy"`, không cần `import LinearModel` trực tiếp ở nơi gọi.

### Bài tập 2.6 — `mlkit/models/registry.py`

- [ ] **BT 2.6.1** — Tạo `mlkit/models/registry.py`: `ModelType` (Enum, 2 giá trị `LINEAR = "linear"`/`DUMMY = "dummy"`) và `create_model(model_type: ModelType) -> BaseModel`.
- [ ] **BT 2.6.2** — Thêm hàm `create_model_from_name(name: str) -> BaseModel` chuyển chuỗi sang `ModelType` rồi gọi `create_model` — hàm này `demo_train.py` sẽ dùng trực tiếp.
- [ ] **BT 2.6.3** — Cập nhật `mlkit/models/__init__.py` expose `BaseModel`, `DummyModel`, `LinearModel`, `ModelType`, `create_model_from_name`.

<details>
<summary><strong>Lời giải chi tiết Phần 2.6</strong></summary>

**`mlkit/models/registry.py`:**

```python
"""Model registry: maps a model name/type to a concrete BaseModel instance."""
from __future__ import annotations

from enum import Enum

from mlkit.models.base import BaseModel
from mlkit.models.dummy import DummyModel
from mlkit.models.linear import LinearModel


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
```

**`mlkit/models/__init__.py`:**

```python
"""mlkit.models — model base class, concrete models, and the registry."""
from mlkit.models.base import BaseModel
from mlkit.models.dummy import DummyModel
from mlkit.models.linear import LinearModel
from mlkit.models.registry import ModelType, create_model_from_name

__all__ = [
    "BaseModel",
    "DummyModel",
    "LinearModel",
    "ModelType",
    "create_model_from_name",
]
```

```python
from mlkit.models import create_model_from_name

model = create_model_from_name("linear")
print(model)   # <mlkit.models.linear.LinearModel object at 0x...>

try:
    create_model_from_name("random_forest")
except ValueError as e:
    print("Error:", e)   # Unknown model 'random_forest'. Valid options: ['linear', 'dummy']
```
</details>

---

## 8. Phần 2.7 — Hoàn thiện: `demo_train.py`

Ghép **toàn bộ** Phần 2.1-2.6 (`BaseModel`, `DummyModel`/`LinearModel`, `CSVDataset`/`Dataset`, `TrainConfig`, `ModelType`/`create_model_from_name`) thành 1 script chạy được thật — điểm hội tụ cuối cùng của project `mlkit`.

### Bài tập 2.7 — `run_pipeline` + `demo_train.py`

- [ ] **BT 2.7.1** — Hoàn thiện `mlkit/pipeline.py`: thêm hàm `run_pipeline(dataset: Dataset, config: TrainConfig) -> Trainer` — tạo model qua `create_model_from_name(config.model_type)`, chuyển `dataset` sang numpy array, gọi `Trainer(model).train(X, y)`, in MSE, trả về `Trainer` đã huấn luyện.
- [ ] **BT 2.7.2** — Viết `mlkit/__init__.py` (rỗng hoặc chỉ có docstring — package gốc không cần expose gì đặc biệt).
- [ ] **BT 2.7.3** — Viết `demo_train.py` ở **ngoài** package `mlkit/` (cùng cấp): tạo `CSVDataset` từ `sample_data.csv`, chạy `run_pipeline` với **cả 2** `TrainConfig(model_type="linear", ...)` và `TrainConfig(model_type="dummy", ...)` — chỉ đổi 1 tham số `model_type`, **không sửa** `run_pipeline`/`Trainer`.

<details>
<summary><strong>Lời giải chi tiết Phần 2.7 — hoàn thiện project</strong></summary>

**`mlkit/pipeline.py`** (bản đầy đủ):

```python
"""Training orchestration for mlkit: Trainer (composition) + run_pipeline
(wires Dataset + model registry + TrainConfig together)."""
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
```

**`mlkit/__init__.py`:**

```python
"""mlkit — a tiny training pipeline toolkit for the Lesson 04 project."""
```

**`demo_train.py`** (ngoài package, điểm chạy chính):

```python
"""Demo script: trains two different mlkit models on the same dataset,
proving run_pipeline() and Trainer never need to change when the model
type changes — this is the Lesson 04 capstone."""
from mlkit.config import TrainConfig
from mlkit.data.datasets import CSVDataset
from mlkit.pipeline import run_pipeline

dataset = CSVDataset("sample_data.csv", target_column="target")

print("=== Training with model_type='linear' ===")
run_pipeline(dataset, TrainConfig(model_type="linear", tags=["demo-linear"]))

print("\n=== Training with model_type='dummy' ===")
run_pipeline(dataset, TrainConfig(model_type="dummy", tags=["demo-dummy"]))
```

**Chạy toàn bộ project đã hoàn thiện:**

```bash
cd mlkit-project
pip install numpy   # duy nhất dependency ngoài chuẩn
python demo_train.py
```

> **Điều cần quan sát:** `run_pipeline()` và `Trainer` được viết **đúng 1 lần**, không hề nhắc tới `DummyModel`/`LinearModel` theo tên (chỉ qua `create_model_from_name`) — đổi `model_type="linear"` sang `model_type="dummy"` không sửa bất kỳ dòng code nào trong `pipeline.py`. Đây chính là nguyên lý Liskov Substitution + Dependency Injection áp dụng vào 1 script thật, không phải ví dụ minh hoạ.
</details>

---

## 9. Đáp án Quiz

- [ ] Đã trả lời cả 3 câu bằng lời của bạn trong `SUBMISSION.md` trước khi mở phần dưới.

<details>
<summary><strong>Đáp án tham khảo</strong></summary>

**Câu 1: Khác nhau ABC vs Protocol?**
> ABC dùng nominal typing: lớp con phải kế thừa tường minh, kiểm tra ngay lúc khởi tạo object (`TypeError` nếu thiếu abstract method). Protocol dùng structural typing: object chỉ cần đúng cấu trúc, không cần kế thừa. `mlkit.models.BaseModel` dùng ABC vì `mlkit` kiểm soát toàn bộ họ model, muốn ép buộc `fit`/`predict`. `mlkit.data.Dataset` dùng Protocol vì muốn cả `CSVDataset` lẫn dataset PyTorch sau này đều hợp lệ mà không cần sửa code của chúng.

**Câu 2: Khi nào dùng dataclass thay class thường?**
> Khi lớp chủ yếu chứa dữ liệu, ít logic phức tạp — như `TrainConfig`. `@dataclass` tự sinh `__init__`/`__repr__`/`__eq__`. `BaseModel` (có logic `fit`/`predict`/`save`/`load` phức tạp, cần kế thừa) thì dùng class thường + ABC.

**Câu 3: `__eq__` mà không có `__hash__` gây lỗi gì?**
> Python tự đặt `__hash__ = None` khi override `__eq__` (vì 2 object bằng nhau theo giá trị nhưng hash theo id cũ sẽ khác nhau, vi phạm nguyên tắc hash). Hệ quả: object không dùng làm dict key/phần tử set được nữa. `@dataclass` mặc định (không `frozen`) tự sinh `__eq__` nhưng không sinh `__hash__` — đây là lý do `TrainConfig` (mutable, có `tags: list`) không nên và không thể hash được.
</details>

---

## 10. Tổng kết & bước tiếp theo

- ✅ `mlkit` là 1 project OOP hoàn chỉnh, độc lập, chạy được thật bằng `python demo_train.py`.
- ✅ Không có ví dụ OOP nào (class A/B/C, Vector, BankAccount...) bị dùng rồi bỏ — mọi khái niệm được áp dụng trực tiếp vào code sống của `mlkit`.
- ✅ Kỹ năng ABC/Protocol/composition/factory sẽ dùng lại (dưới dạng pattern, không phải dùng lại code) ở Unit 04, 05, 08, 09 khi pipeline ML thật phức tạp hơn nhiều.

**Bài tiếp theo:** U01-05 — Type hints, Pydantic v2 và cấu hình.

---

## 11. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| `BaseModel` (ABC) + `DummyModel`/`LinearModel` đúng chuẩn, `is_fitted` hoạt động | 2 |
| `CSVDataset` đúng magic methods, thoả mãn `Dataset` Protocol không kế thừa | 2 |
| `TrainConfig` validate đúng, `ModelType`/`create_model_from_name` đúng | 2 |
| `demo_train.py` chạy đúng với ≥2 model, `run_pipeline` không tham chiếu class cụ thể | 3 |
| Trả lời đúng 3/3 câu quiz | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
