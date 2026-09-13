# U01-05 — Type Hints, Pydantic v2 và Cấu hình

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 2 · **Giờ dự kiến:** 6 · **Độ khó:** TB
> **Tài liệu tham khảo:** Pydantic Docs v2 · mypy docs · Hydra docs
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.
> **Lưu ý về lời giải:** Từ bài này, lời giải được **hiện thẳng ngay dưới mỗi bài tập**, không ẩn trong khối gập nữa — đọc xong bài tập, đọc luôn lời giải, tự đối chiếu cách làm của bạn.

## Dự án của bài học: package `expconfig`

Bài này xây **1 project mới, độc lập** — package `expconfig`, mô phỏng lớp cấu hình + validate dữ liệu cho 1 dịch vụ huấn luyện mô hình (giống hệt thứ bạn sẽ cần khi xây API thật ở Unit 08). Không liên quan tới `mytools` (Bài 03) hay `mlkit` (Bài 04).

```
expconfig-project/
├── .env                # -> Phần 2.4
├── schemas.py          # -> Phần 2.1, 2.3 (typing thuần -> Pydantic models)
├── config.py           # -> Phần 2.4 (AppSettings)
└── demo.py             # -> Phần 2.6 (điểm hội tụ cuối bài)
```

> **Cách dùng file này:** Đọc lý thuyết từng phần → tạo đúng file/hàm/class được chỉ định → đọc lời giải ngay bên dưới để đối chiếu → tick ☐ → ☑. Cuối bài, `python demo.py` chạy được thật.

**Cài đặt trước khi bắt đầu:**

```bash
pip install "pydantic>=2.5" "pydantic-settings>=2.0" mypy
```

---

## 1. Mục tiêu bài học

- [ ] Dùng thành thạo `Optional`, `Union`/`|`, `Literal`, `TypedDict`, `Generic`, `TypeVar`, `Callable`.
- [ ] Chạy `mypy --strict`, đọc hiểu lỗi, biết khi nào dùng `# type: ignore`.
- [ ] Dùng Pydantic v2: `BaseModel`, `field_validator`, `model_validator`, serialization.
- [ ] Dùng `pydantic-settings` nạp config từ `.env` + biến môi trường.
- [ ] Hiểu vì sao type + schema quan trọng khi làm việc với output của LLM (giới thiệu, đào sâu ở Unit 08).
- [ ] **Sản phẩm:** `demo.py` chạy 1 luồng request→validate→train→eval hoàn chỉnh, `mypy --strict` pass 0 lỗi trên toàn bộ package.

---

## 2. Phần 2.1 — Typing cơ bản: `schemas.py` (bản nháp thuần typing)

### Lý thuyết

| Công cụ | Dùng khi | Ví dụ |
|---|---|---|
| `Optional[X]` (= `X \| None`) | Giá trị có thể vắng mặt | `Optional[str]` |
| `Union[X, Y]` (= `X \| Y`) | Giá trị có thể là 1 trong nhiều kiểu | `int \| str` |
| `Literal[...]` | Giá trị chỉ được nằm trong tập cố định | `Literal["linear", "dummy"]` |
| `TypedDict` | Mô tả **hình dạng** của 1 dict (không phải class thật lúc runtime) | dữ liệu JSON thô trước khi validate |
| `Generic[T]` + `TypeVar` | Class/hàm tái sử dụng cho nhiều kiểu dữ liệu | `Box[int]`, `Box[str]` |
| `Callable[[Arg], Ret]` | Tham số là 1 hàm | `Callable[[int], int]` |

Từ Python 3.10, `X | None` viết gọn hơn `Optional[X]` và `X | Y` gọn hơn `Union[X, Y]` — cùng ý nghĩa, cú pháp mới được khuyến khích dùng trong code mới.

### Bài tập 2.1 — Viết `schemas.py` bản thuần typing (chưa dùng Pydantic)

- [ ] **BT 2.1.1** — Tạo `schemas.py`. Viết `ModelName = Literal["linear", "dummy", "boosting"]` và hàm `select_model(name: ModelName) -> str`.
- [ ] **BT 2.1.2** — Viết `TypedDict RawRecord` với 2 field `name: str`, `score: float`, và hàm `process_record(record: RawRecord) -> str`.
- [ ] **BT 2.1.3** — Viết `class Box(Generic[T])` với `__init__(self, value: T)` và `get(self) -> T`.
- [ ] **BT 2.1.4** — Viết hàm `apply_twice(fn: Callable[[int], int], x: int) -> int` áp dụng `fn` lên `x` 2 lần.

### Lời giải Phần 2.1

```python
"""Type-hinted helpers for the expconfig project (pre-Pydantic version).
Will be replaced by Pydantic models in Section 2.3 — this version exists
only to practice raw typing constructs first.
"""
from __future__ import annotations

from typing import Callable, Generic, Literal, Optional, TypedDict, TypeVar

ModelName = Literal["linear", "dummy", "boosting"]


class RawRecord(TypedDict):
    name: str
    score: float


def find_user(user_id: int) -> Optional[str]:
    """Optional[str] means the return value is either a str or None."""
    return "Alice" if user_id == 1 else None


def select_model(name: ModelName) -> str:
    """`name` is statically restricted to the 3 allowed literals."""
    return f"selected {name}"


def process_record(record: RawRecord) -> str:
    return f"{record['name']}: {record['score']}"


T = TypeVar("T")


class Box(Generic[T]):
    """A generic single-value container, reusable for any type T."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


def apply_twice(fn: Callable[[int], int], x: int) -> int:
    return fn(fn(x))
```

**Chạy thử — kết quả đã kiểm chứng thật:**

```python
print(find_user(1), find_user(2))        # Alice None
print(select_model("linear"))            # selected linear
print(process_record({"name": "Alice", "score": 9.5}))   # Alice: 9.5
box = Box(42)
print(box.get())                          # 42
print(apply_twice(lambda x: x + 1, 5))    # 7
```

---

## 3. Phần 2.2 — `mypy --strict`: kiểm tra và sửa lỗi

### Lý thuyết

`mypy --strict` bật **toàn bộ** cờ kiểm tra nghiêm ngặt cùng lúc: bắt buộc mọi hàm phải có type hint đầy đủ, không cho phép `Any` ngầm định, kiểm tra khớp kiểu ở mọi phép gán. Đây là mức kiểm tra khắt khe nhất — dùng cho code production.

**`# type: ignore[mã-lỗi]`** — dùng khi bạn **chắc chắn** mypy sai (hoặc không thể sửa, ví dụ do thư viện ngoài thiếu type stub), không phải để "cho qua" lỗi bạn lười sửa. Luôn ghi kèm mã lỗi cụ thể (`[call-arg]`, `[return-value]`...) thay vì `# type: ignore` trần trụi — để không vô tình che giấu 1 lỗi khác không liên quan trong tương lai.

### Bài tập 2.2 — Chạy `mypy --strict` trên `schemas.py`

- [ ] **BT 2.2.1** — Chạy `mypy --strict schemas.py`. Với code đúng ở Phần 2.1, phải **pass 0 lỗi**.
- [ ] **BT 2.2.2** — Cố tình tạo 1 file `schemas_buggy.py` với 3 lỗi: (a) 1 hàm thiếu type hint hoàn toàn, (b) 1 hàm khai báo trả về `str` nhưng `return` số nguyên, (c) gán 1 giá trị `int` vào biến đã khai báo kiểu `str`. Chạy `mypy --strict` và ghi lại chính xác 3 dòng lỗi.

### Lời giải Phần 2.2

**Kết quả `mypy --strict schemas.py` trên code đúng (đã kiểm chứng thật):**

```
Success: no issues found in 1 source file
```

**`schemas_buggy.py`** (file tạm để luyện đọc lỗi, không phải file thật của project):

```python
"""Deliberately buggy version to demonstrate what mypy --strict catches."""
from __future__ import annotations

from typing import Literal

ModelName = Literal["linear", "dummy", "boosting"]


def find_user(user_id):   # (a) missing type hints entirely
    return "Alice" if user_id == 1 else None


def select_model(name: ModelName) -> str:
    return 123   # (b) returns int, but annotated -> str


def add(a: int, b: int) -> int:
    return a + b


result: str = add(1, 2)   # (c) assigning int to a str-annotated variable
```

**Kết quả `mypy --strict schemas_buggy.py` (đã chạy thật, đúng 3 lỗi):**

```
schemas_buggy.py:9: error: Function is missing a type annotation  [no-untyped-def]
schemas_buggy.py:14: error: Incompatible return value type (got "int", expected "str")  [return-value]
schemas_buggy.py:20: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
Found 3 errors in 1 file (checked 1 source file)
```

---

## 4. Phần 2.3 — Pydantic v2: chuyển `schemas.py` thành model thật

### Lý thuyết

`TypedDict` chỉ mô tả hình dạng — **không tự kiểm tra** giá trị lúc runtime (bạn có thể tạo `RawRecord` với `score` là chuỗi mà không có lỗi gì). **Pydantic `BaseModel`** thì có: nó **validate thật** ngay khi tạo object, tự động ép kiểu hợp lý (`"5"` → `5` cho field `int`), và ném `ValidationError` rõ ràng khi dữ liệu sai.

```python
from pydantic import BaseModel, Field, field_validator, model_validator

class TrainConfig(BaseModel):
    train_ratio: float
    val_ratio: float
    test_ratio: float

    @field_validator("train_ratio")          # chạy cho TỪNG field riêng lẻ
    @classmethod
    def check_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("must be between 0 and 1")
        return value

    @model_validator(mode="after")            # chạy SAU KHI tất cả field đã có giá trị
    def check_sum(self) -> "TrainConfig":
        if abs(self.train_ratio + self.val_ratio + self.test_ratio - 1.0) > 1e-9:
            raise ValueError("ratios must sum to 1.0")
        return self
```

`field_validator` kiểm tra **1 field** độc lập; `model_validator(mode="after")` kiểm tra **quan hệ giữa nhiều field** (như tổng 3 tỉ lệ phải bằng 1) — chỉ chạy được sau khi mọi field riêng lẻ đã hợp lệ.

### Bài tập 2.3 — 4 model Pydantic cho `schemas.py`

- [ ] **BT 2.3.1** — Viết `TrainRequest(BaseModel)`: `dataset_path: str`, `model_type: Literal["linear","dummy","boosting"] = "linear"`, `epochs: int` (dùng `Field(gt=0, default=10)` — bắt buộc dương).
- [ ] **BT 2.3.2** — Viết `TrainResponse(BaseModel)`: `run_id: str`, `status: Literal["queued","running","done","failed"]`.
- [ ] **BT 2.3.3** — Viết `TrainConfig(BaseModel)` với `train_ratio`/`val_ratio`/`test_ratio: float`, có `field_validator` kiểm tra mỗi tỉ lệ nằm trong `[0, 1]`, và `model_validator(mode="after")` kiểm tra tổng 3 tỉ lệ bằng 1.0 (sai số cho phép `1e-9` vì số thực dấu phẩy động — nhắc lại Bài 2.10 sẽ học kỹ hơn).
- [ ] **BT 2.3.4** — Viết `EvalResult(BaseModel)`: `accuracy`/`f1_score: float`, dùng `Field(ge=0.0, le=1.0)` cho cả 2.
- [ ] **BT 2.3.5** — Tạo 1 `TrainRequest` hợp lệ, gọi `.model_dump()` và `.model_dump_json()`, in kết quả.
- [ ] **BT 2.3.6** — Tạo `TrainConfig` với tổng tỉ lệ = 1.1 (sai), bắt `ValidationError`, in `e.errors()[0]["msg"]`.

### Lời giải Phần 2.3

**`schemas.py`** (thay thế hoàn toàn bản Phần 2.1):

```python
"""Pydantic v2 schemas for the expconfig project."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TrainRequest(BaseModel):
    """Incoming request to start a training run."""

    dataset_path: str
    model_type: Literal["linear", "dummy", "boosting"] = "linear"
    epochs: int = Field(gt=0, default=10)


class TrainResponse(BaseModel):
    """Response returned after a training run is accepted."""

    run_id: str
    status: Literal["queued", "running", "done", "failed"]


class TrainConfig(BaseModel):
    """Split ratios for a training run — must sum to 1.0."""

    train_ratio: float
    val_ratio: float
    test_ratio: float

    @field_validator("train_ratio", "val_ratio", "test_ratio")
    @classmethod
    def ratio_must_be_between_0_and_1(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"ratio must be between 0 and 1, got {value}")
        return value

    @model_validator(mode="after")
    def ratios_must_sum_to_one(self) -> "TrainConfig":
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"train_ratio + val_ratio + test_ratio must equal 1.0, got {total}"
            )
        return self


class EvalResult(BaseModel):
    """Metrics produced after evaluating a trained model."""

    accuracy: float = Field(ge=0.0, le=1.0)
    f1_score: float = Field(ge=0.0, le=1.0)
```

**Chạy thử — kết quả đã kiểm chứng thật:**

```python
from pydantic import ValidationError
from schemas import TrainRequest, TrainResponse, TrainConfig, EvalResult

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
```

**Lưu ý quan trọng đã kiểm chứng:** thông báo lỗi tổng tỉ lệ ghi `got 1.0999999999999999` chứ không phải `1.1` sạch đẹp — đây chính là hệ quả của số thực dấu phẩy động (`0.7 + 0.2 + 0.2` không tính đúng tuyệt đối trong hệ nhị phân), lý do `model_validator` phải so sánh bằng `abs(total - 1.0) > 1e-9` thay vì `total != 1.0`.

---

## 5. Phần 2.4 — `pydantic-settings`: `config.py` (`AppSettings`)

### Lý thuyết

`pydantic-settings` là package riêng (tách khỏi `pydantic` core từ v2), cho phép định nghĩa cấu hình ứng dụng dưới dạng 1 `BaseModel` đặc biệt — **tự động đọc giá trị từ file `.env` và biến môi trường**, theo đúng thứ tự ưu tiên: **biến môi trường ghi đè `.env`** (đã kiểm chứng thực tế bên dưới).

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    app_name: str = "myapp"
    api_key: str          # bắt buộc — không có default, phải có trong .env/env var
```

`SecretStr` (từ `pydantic`) dùng cho dữ liệu nhạy cảm (API key, password) — tự động **che giấu giá trị khi `print()`/`repr()`**, chỉ lộ ra khi gọi tường minh `.get_secret_value()`.

### Bài tập 2.4 — `config.py` và `.env`

- [ ] **BT 2.4.1** — Tạo file `.env` với 4 dòng: `APP_NAME`, `API_KEY`, `MAX_EPOCHS`, `DEBUG`.
- [ ] **BT 2.4.2** — Viết `config.py`: `AppSettings(BaseSettings)` với `app_name: str`, `api_key: SecretStr` (bắt buộc, không default), `max_epochs: int = 100`, `debug: bool = False`. Đọc từ `.env`.
- [ ] **BT 2.4.3** — Chạy `python config.py`, in `settings.api_key` (phải bị che) và `settings.api_key.get_secret_value()` (phải hiện giá trị thật).
- [ ] **BT 2.4.4** — Kiểm chứng thứ tự ưu tiên: chạy `MAX_EPOCHS=999 python config.py` — giá trị `999` phải **thắng** giá trị trong `.env`.
- [ ] **BT 2.4.5** — Chạy `mypy --strict config.py` — sẽ gặp 1 lỗi thật `[call-arg]` vì mypy không biết `pydantic-settings` tự điền `api_key` lúc runtime. Sửa bằng `# type: ignore[call-arg]` kèm comment giải thích rõ lý do (đúng nguyên tắc Phần 2.2: luôn ghi mã lỗi cụ thể + lý do).

### Lời giải Phần 2.4

**`.env`:**

```env
APP_NAME=expconfig-dev
API_KEY=sk-from-dotenv-12345
MAX_EPOCHS=50
DEBUG=true
```

**`config.py`:**

```python
"""Application settings loaded from .env and environment variables."""
from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Central place for all configuration — never hardcode these values."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "expconfig"
    api_key: SecretStr
    max_epochs: int = 100
    debug: bool = False


if __name__ == "__main__":
    # mypy sees AppSettings() as missing the required `api_key` argument,
    # because it cannot know pydantic-settings fills it in from .env/env
    # vars at runtime. This is a known, deliberate mismatch — not a real
    # bug — so we silence exactly this error code with a clear reason.
    settings = AppSettings()  # type: ignore[call-arg]
    print(settings.app_name, settings.max_epochs, settings.debug)
    print(settings.api_key)                     # masked in repr
    print(settings.api_key.get_secret_value())   # real value, on purpose
```

**Kết quả `python config.py` — đọc từ `.env` (đã kiểm chứng thật):**

```
expconfig-dev 50 True
**********
sk-from-dotenv-12345
```

**Kết quả `MAX_EPOCHS=999 python config.py` — biến môi trường thắng `.env` (đã kiểm chứng thật):**

```
expconfig-dev 999 True
**********
sk-from-dotenv-12345
```

**Kết quả `mypy --strict config.py` TRƯỚC khi thêm `# type: ignore`:**

```
config.py:20: error: Missing named argument "api_key" for "AppSettings"  [call-arg]
Found 1 error in 1 file (checked 1 source file)
```

**Sau khi thêm `# type: ignore[call-arg]` như trong code trên:**

```
Success: no issues found in 1 source file
```

---

## 6. Phần 2.5 — Xử lý JSON lỗi định dạng và `ValidationError` thân thiện

### Lý thuyết

2 loại lỗi hoàn toàn khác nhau cần phân biệt khi nhận dữ liệu từ bên ngoài (API, file, LLM output):

1. **Lỗi cú pháp JSON** (`json.JSONDecodeError`) — chuỗi không parse được thành dict/list ngay từ đầu.
2. **Lỗi validate** (`pydantic.ValidationError`) — JSON hợp lệ, nhưng dữ liệu bên trong sai kiểu/thiếu field/vi phạm validator.

Phải bắt **cả 2 loại riêng biệt** để đưa ra thông báo đúng nguyên nhân — đây chính là kỹ năng nền tảng cho Unit 08 khi phải parse output của LLM (LLM có thể trả JSON sai cú pháp, hoặc đúng cú pháp nhưng sai schema).

### Bài tập 2.5 — `parse_train_request`

- [ ] **BT 2.5.1** — Viết hàm `parse_train_request(raw_json: str) -> TrainRequest | None` trong `schemas.py` (hoặc file riêng): bắt `json.JSONDecodeError` in lỗi cú pháp, bắt `ValidationError` in từng lỗi field kèm tên field, trả `None` nếu lỗi.
- [ ] **BT 2.5.2** — Thử với 4 trường hợp: (a) JSON sai cú pháp, (b) JSON đúng cú pháp nhưng `epochs` là chuỗi không parse được thành số, (c) `model_type` không nằm trong `Literal` cho phép, (d) JSON hợp lệ hoàn toàn.

### Lời giải Phần 2.5

```python
"""JSON parsing with friendly, distinguished error messages."""
import json

from pydantic import ValidationError

from schemas import TrainRequest


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
```

**Kết quả chạy 4 trường hợp — đã kiểm chứng thật:**

```python
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
```

---

## 7. Phần 2.6 — Hoàn thiện: `demo.py` + giới thiệu Hydra/OmegaConf

### Lý thuyết

Bạn vừa dùng Pydantic để validate **1 cấu hình đơn**. Khi chạy **nhiều thí nghiệm ML** với hàng chục biến thể tham số (learning rate, batch size, kiến trúc...), Pydantic vẫn kiểm tra đúng nhưng không có cơ chế "override từ command line" hay "gộp nhiều file config". Đó là lúc dùng **Hydra** hoặc **OmegaConf** — 2 công cụ chuyên quản lý cấu hình thí nghiệm phức tạp, sẽ học sâu ở Unit 05/09 khi thực sự chạy nhiều thí nghiệm huấn luyện song song. Ở mức này, chỉ cần biết: **Pydantic validate "1 config có hợp lệ không"**, **Hydra/OmegaConf quản lý "hàng trăm config đến từ đâu, override thế nào"** — hai việc bổ trợ nhau, không thay thế nhau.

**Vì sao type + schema quan trọng với output LLM?** LLM trả về văn bản tự do, kể cả khi bạn yêu cầu JSON — nó vẫn có thể trả sai cú pháp, thiếu field, hoặc "sáng tạo" thêm field lạ. Pipeline production **luôn** phải validate output LLM qua 1 Pydantic schema chặt trước khi dùng — đúng kỹ thuật Phần 2.5 vừa làm, sẽ dùng lại nguyên vẹn ở Bài 8.3 (Structured Output).

### Bài tập 2.6 — `demo.py`: ghép toàn bộ

- [ ] **BT 2.6.1** — Viết `demo.py`: đọc `AppSettings`, parse 1 `TrainRequest` hợp lệ bằng `parse_train_request` (Phần 2.5), kiểm tra `request.epochs` không vượt `settings.max_epochs` (nếu vượt thì từ chối và dừng), tạo `TrainConfig` + `TrainResponse`, in `EvalResult` cuối cùng.
- [ ] **BT 2.6.2** — Chạy `python demo.py` — toàn bộ luồng phải chạy trót lọt, in đủ 5 dòng kết quả.
- [ ] **BT 2.6.3** — Chạy `mypy --strict schemas.py config.py demo.py` — phải pass 0 lỗi trên **cả 3 file** (đúng DoD gốc của bài học).

### Lời giải Phần 2.6

```python
"""Integration demo: AppSettings + schemas working together end-to-end."""
from __future__ import annotations

import json

from pydantic import ValidationError

from config import AppSettings
from schemas import EvalResult, TrainConfig, TrainRequest, TrainResponse


def parse_train_request(raw_json: str) -> TrainRequest | None:
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


def main() -> None:
    settings = AppSettings()  # type: ignore[call-arg]
    print(f"[{settings.app_name}] max_epochs allowed by server: {settings.max_epochs}")

    raw_request = '{"dataset_path": "sales.csv", "model_type": "linear", "epochs": 30}'
    request = parse_train_request(raw_request)
    if request is None:
        return

    if request.epochs > settings.max_epochs:
        print(f"Rejected: epochs={request.epochs} exceeds server limit "
              f"{settings.max_epochs}")
        return

    config = TrainConfig(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    response = TrainResponse(run_id="run-001", status="queued")
    print(f"Accepted request: {request}")
    print(f"Using split config: {config}")
    print(f"Response: {response}")

    result = EvalResult(accuracy=0.91, f1_score=0.88)
    print(f"Final evaluation: {result}")


if __name__ == "__main__":
    main()
```

**Kết quả `python demo.py` — đã chạy thật:**

```
[expconfig-dev] max_epochs allowed by server: 50
Accepted request: dataset_path='sales.csv' model_type='linear' epochs=30
Using split config: train_ratio=0.7 val_ratio=0.15 test_ratio=0.15
Response: run_id='run-001' status='queued'
Final evaluation: accuracy=0.91 f1_score=0.88
```

**Kết quả `mypy --strict schemas.py config.py demo.py` — đã chạy thật:**

```
Success: no issues found in 3 source files
```

> **Quan sát:** `max_epochs allowed by server: 50` đến từ `.env` (Phần 2.4), request có `epochs=30` nên **không** bị từ chối (30 ≤ 50). Thử đổi `epochs` thành `60` trong `raw_request` — bạn sẽ thấy dòng "Rejected" thay vì luồng thành công, chứng minh `AppSettings` và `schemas.py` thực sự phối hợp với nhau, không phải 2 phần độc lập ghép hình thức.

---

## 8. Đáp án Quiz

- [ ] Đã trả lời cả 3 câu bằng lời của bạn trong `SUBMISSION.md` — đọc đáp án dưới đây để đối chiếu.

**Câu 1: Khác nhau `Optional[X]` và `X | None`?**
> Không khác nhau về ý nghĩa — cả 2 đều nghĩa là "kiểu `X` hoặc `None`". `Optional[X]` là cú pháp cũ (từ `typing`, dùng được từ Python 3.5+). `X | None` là cú pháp mới (PEP 604, Python 3.10+), dùng toán tử `|` cho union type — ngắn gọn hơn, không cần import từ `typing`, được khuyến khích trong code mới. Với Python < 3.10, phải dùng `Optional`/`Union` hoặc `from __future__ import annotations` để dùng cú pháp `|` mà không lỗi.

**Câu 2: Pydantic v1 vs v2 khác gì?**
> V2 viết lại core bằng Rust (`pydantic-core`) nên nhanh hơn v1 5-50 lần. Đổi tên nhiều API: `.dict()` → `.model_dump()`, `.json()` → `.model_dump_json()`, `@validator` → `@field_validator` (bắt buộc thêm `@classmethod`), thêm mới `@model_validator` (validate liên field, thay cho `@root_validator` của v1). `Config` class lồng bên trong → `model_config = ConfigDict(...)`. V1 và v2 không tương thích ngược hoàn toàn — code cũ cần migrate.

**Câu 3: `BaseSettings` ưu tiên `.env` hay biến môi trường?**
> **Biến môi trường thắng `.env`** — đã kiểm chứng thực tế trong Phần 2.4 (`MAX_EPOCHS=999 python config.py` cho ra `999` dù `.env` ghi `50`). Thứ tự ưu tiên đầy đủ của `pydantic-settings` (từ cao xuống thấp): tham số truyền trực tiếp khi khởi tạo (`AppSettings(max_epochs=1)`) > biến môi trường > file `.env` > giá trị default khai báo trong class.

---

## 9. Tổng kết & bước tiếp theo

- ✅ `expconfig` là 1 project độc lập, hoàn chỉnh: 4 model Pydantic + `AppSettings` + luồng validate JSON đầu-cuối.
- ✅ `mypy --strict` pass 0 lỗi trên toàn bộ 3 file — đúng DoD gốc, kể cả xử lý đúng trường hợp `# type: ignore` chính đáng (không phải "cho qua" bừa).
- ✅ Kỹ thuật `field_validator`/`model_validator`/xử lý `ValidationError` sẽ dùng lại **nguyên vẹn** ở Bài 8.3 khi validate output LLM.

**Bài tiếp theo:** U01-06 — Lỗi, logging và kiểm thử với pytest.

---

## 10. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Phần 2.1-2.2: typing cơ bản đúng, `mypy --strict` pass + bắt đúng 3 lỗi cố ý | 2 |
| 4 model Pydantic đúng chuẩn, `field_validator`+`model_validator` hoạt động đúng | 3 |
| `AppSettings` đọc đúng `.env`, biến môi trường ghi đè đúng, xử lý `# type: ignore` hợp lý | 2 |
| `parse_train_request` phân biệt đúng lỗi cú pháp JSON vs `ValidationError` | 1 |
| `demo.py` chạy đúng luồng đầy đủ, `mypy --strict` pass 0 lỗi trên cả 3 file | 1 |
| Trả lời đúng 3/3 câu quiz | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
