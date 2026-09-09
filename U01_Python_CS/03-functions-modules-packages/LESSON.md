# U01-03 — Hàm, Module, Package và Cấu trúc Import

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 6 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.7-9 · Python Docs: Modules
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.
> **Cách dùng file này:** Đọc lý thuyết từng phần → làm ngay bài tập của phần đó (tick ☐ → ☑) → cuối bài có 1 dự án tổng hợp dùng lại mọi thứ đã làm.

---

## 1. Mục tiêu bài học

- [ ] Dùng thành thạo mọi kiểu tham số hàm: positional, keyword, `*args`, `**kwargs`, keyword-only.
- [ ] Hiểu quy tắc scope LEGB, phân biệt khi nào cần `global`/`nonlocal`.
- [ ] Dùng `map`/`filter`/`functools.reduce` và các decorator hữu ích trong `functools`.
- [ ] Phân biệt module vs package, `__init__.py`, absolute vs relative import.
- [ ] Hiểu `if __name__ == "__main__":`, viết CLI bằng `typer`.
- [ ] Biết circular import xảy ra khi nào và cách phá vỡ.
- [ ] Đóng gói `mytools/` — cài bằng `pip install -e .`, chạy CLI `python -m mytools`, không cần sửa `sys.path`.

---

## 2. Phần 2.1 — Các kiểu tham số hàm

### Lý thuyết

```python
def describe(name, age=18, *hobbies, country="VN", **extra_info):
    #        ^positional  ^default   ^*args      ^keyword-only  ^**kwargs
    ...
```

| Kiểu | Cú pháp | Ví dụ gọi |
|---|---|---|
| Positional | `def f(a, b)` | `f(1, 2)` |
| Positional có default | `def f(a, b=10)` | `f(1)` hoặc `f(1, 2)` |
| Var-positional | `def f(*args)` | `f(1, 2, 3)` → `args = (1, 2, 3)` |
| Keyword-only | `def f(*, a)` | `f(a=1)` — bắt buộc dùng tên |
| Var-keyword | `def f(**kwargs)` | `f(x=1, y=2)` → `kwargs = {"x": 1, "y": 2}` |

**Vì sao cần keyword-only?** Buộc người gọi hàm ghi rõ tên tham số, tránh nhầm lẫn khi nhiều tham số cùng kiểu:

```python
def create_user(name, *, is_admin=False, is_active=True):
    ...

create_user("Alice", is_admin=True)      # rõ ràng, không thể nhầm thứ tự
```

### Bài tập 2.1 — Thiết kế hàm với keyword-only

- [ ] **BT 2.1.1** — Viết hàm `train_model(X, y, *, learning_rate=0.01, epochs=10, verbose=False)` — bắt buộc `learning_rate`/`epochs`/`verbose` phải truyền bằng tên. Gọi thử đúng và gọi sai (không dùng tên) để thấy lỗi.
- [ ] **BT 2.1.2** — Viết hàm `summarize(*numbers, **options)` in ra tổng, trung bình của `numbers`, và in thêm mọi cặp key=value trong `options`.

<details>
<summary><strong>Lời giải chi tiết BT 2.1</strong></summary>

```python
def train_model(X, y, *, learning_rate=0.01, epochs=10, verbose=False):
    """Dummy training stub demonstrating keyword-only parameters."""
    if verbose:
        print(f"Training with lr={learning_rate}, epochs={epochs}")
    return {"lr": learning_rate, "epochs": epochs}

train_model([1, 2], [3, 4], learning_rate=0.05, epochs=20, verbose=True)  # OK

try:
    train_model([1, 2], [3, 4], 0.05, 20, True)   # TypeError: too many positional args
except TypeError as e:
    print("Error:", e)


def summarize(*numbers: float, **options: str) -> None:
    """Print total/average of positional numbers plus any keyword options."""
    total = sum(numbers)
    average = total / len(numbers) if numbers else 0
    print(f"total={total}, average={average}")
    for key, value in options.items():
        print(f"  option {key} = {value}")

summarize(1, 2, 3, 4, unit="kg", source="sensor_a")
```
</details>

---

## 3. Phần 2.2 — Scope LEGB

### Lý thuyết

Python tra cứu tên biến theo thứ tự **LEGB**: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)   # "local"
    inner()
    print(x)       # "enclosing"

outer()
print(x)           # "global"
```

`global`/`nonlocal` dùng khi muốn **gán lại** (không chỉ đọc) biến ở scope ngoài:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
```

> **Nguyên tắc thực hành:** hạn chế `global` trong code thật — khiến hàm phụ thuộc trạng thái ẩn, khó test.

### Bài tập 2.2 — Closure với `nonlocal`

- [ ] **BT 2.2.1** — Viết `make_counter()` như trên, tạo 2 counter độc lập, chứng minh chúng không ảnh hưởng lẫn nhau.
- [ ] **BT 2.2.2** — Viết hàm `make_accumulator(start=0)` trả về 1 hàm `add(x)` cộng dồn vào `start` mỗi lần gọi, dùng `nonlocal`.

<details>
<summary><strong>Lời giải chi tiết BT 2.2</strong></summary>

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter_a = make_counter()
counter_b = make_counter()
print(counter_a(), counter_a(), counter_a())   # 1 2 3
print(counter_b())                              # 1 — độc lập với counter_a


def make_accumulator(start: int = 0):
    total = start
    def add(x: int) -> int:
        nonlocal total
        total += x
        return total
    return add

acc = make_accumulator(100)
print(acc(10))   # 110
print(acc(5))    # 115
```
</details>

---

## 4. Phần 2.3 — First-class Function và `functools`

### Lý thuyết

Hàm là 1 giá trị — gán cho biến, truyền làm tham số, trả về từ hàm khác.

```python
def square(x): return x ** 2
operation = square
list(map(square, [1, 2, 3, 4]))              # [1, 4, 9, 16]
list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4]))  # [2, 4]

from functools import reduce
reduce(lambda acc, x: acc + x, [1, 2, 3, 4], 0)   # 10
```

**3 công cụ quan trọng của `functools`:**

```python
from functools import lru_cache, partial, wraps

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def power(base, exponent): return base ** exponent
square = partial(power, exponent=2)

def my_decorator(func):
    @wraps(func)   # giữ __name__/__doc__ của hàm gốc
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### Bài tập 2.3 — `lru_cache` và benchmark

- [ ] **BT 2.3.1** — Viết `fibonacci_uncached` và `fibonacci_cached` (dùng `lru_cache`). Đo thời gian chạy `fibonacci(32)` ở cả 2, so sánh bằng số liệu thật.
- [ ] **BT 2.3.2** — Viết decorator `@timeit` (dùng `wraps`) in ra thời gian chạy của bất kỳ hàm nào nó bọc.

<details>
<summary><strong>Lời giải chi tiết BT 2.3</strong></summary>

```python
import time
from functools import lru_cache, wraps


def fibonacci_uncached(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_uncached(n - 1) + fibonacci_uncached(n - 2)


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def benchmark(n: int = 32) -> None:
    start = time.perf_counter()
    result_uncached = fibonacci_uncached(n)
    time_uncached = time.perf_counter() - start

    fibonacci_cached.cache_clear()
    start = time.perf_counter()
    result_cached = fibonacci_cached(n)
    time_cached = time.perf_counter() - start

    assert result_uncached == result_cached
    print(f"fibonacci({n}) = {result_uncached}")
    print(f"Uncached: {time_uncached:.4f}s")
    print(f"Cached  : {time_cached:.6f}s")
    print(f"Speedup : {time_uncached / max(time_cached, 1e-9):.0f}x")


def timeit_decorator(func):
    """Print how long the wrapped function took to run."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


@timeit_decorator
def slow_sum(n: int) -> int:
    return sum(range(n))

slow_sum(10_000_000)
print(slow_sum.__name__)   # "slow_sum" — correctly preserved thanks to @wraps
```
</details>

---

## 5. Phần 2.4 — Module vs Package, Import

### Lý thuyết

**Module** = 1 file `.py`. **Package** = 1 thư mục chứa nhiều module, đánh dấu bằng `__init__.py`.

```
mytools/
├── __init__.py       # chạy khi "import mytools", expose API công khai
├── stats.py
├── cli.py
└── fib.py
```

**Absolute vs relative import:**

```python
# Absolute — luôn ghi đường dẫn đầy đủ
from mytools.stats import compute_stats

# Relative — chỉ dùng BÊN TRONG package
from .stats import compute_stats      # cùng cấp
from ..utils import helper             # lên 1 cấp cha
```

> **Khuyến nghị:** ưu tiên absolute import — dễ đọc, dễ grep, không lỗi khi refactor di chuyển file.

**`if __name__ == "__main__":`** — chỉ chạy khi file được thực thi trực tiếp, không chạy khi bị import.

### Bài tập 2.4 — Module tự viết có cả 2 chế độ

- [ ] **BT 2.4.1** — Viết 1 file `geometry.py` có hàm `circle_area(r)`, và 1 khối `if __name__ == "__main__":` in demo. Chạy trực tiếp (`python geometry.py`) và import từ file khác — quan sát khối demo chỉ chạy ở trường hợp đầu.
- [ ] **BT 2.4.2** — Tạo package nhỏ `shapes/` gồm `__init__.py` và `circle.py`, dùng absolute import để expose `circle_area` ra ở cấp `shapes` (`from shapes import circle_area`).

<details>
<summary><strong>Lời giải chi tiết BT 2.4</strong></summary>

```python
# geometry.py
"""Simple geometry utilities with a __main__ demo block."""

def circle_area(radius: float) -> float:
    """Return the area of a circle with the given radius."""
    return 3.14159 * radius ** 2

if __name__ == "__main__":
    print(f"Demo: circle_area(5) = {circle_area(5)}")
```

```bash
python geometry.py          # prints the demo line
```
```python
# from another file:
from geometry import circle_area
circle_area(5)   # 78.53975 — the demo line does NOT print here
```

```
shapes/
├── __init__.py
└── circle.py
```

```python
# shapes/circle.py
"""Circle-related geometry functions."""

def circle_area(radius: float) -> float:
    return 3.14159 * radius ** 2
```

```python
# shapes/__init__.py
"""shapes package — exposes circle_area at the package level."""
from shapes.circle import circle_area

__all__ = ["circle_area"]
```

```python
from shapes import circle_area   # works thanks to __init__.py re-export
print(circle_area(3))
```
</details>

---

## 6. Phần 2.5 — Circular Import

### Lý thuyết

Xảy ra khi module A import module B, và B (trực tiếp/gián tiếp) lại import A.

**3 cách phá vỡ:**
1. **Tái cấu trúc**: đưa phần dùng chung ra module thứ 3 — cách tốt nhất.
2. **Import trễ**: chuyển `import b` xuống bên trong hàm.
3. **Import cả module**: `import b` rồi gọi `b.func_b()` thay vì `from b import func_b`.

### Bài tập 2.5 — Tự tạo và phá vỡ circular import

- [ ] **BT 2.5.1** — Cố tình tạo 2 file `a.py`/`b.py` circular import lẫn nhau, chạy và ghi lại lỗi chính xác Python báo.
- [ ] **BT 2.5.2** — Sửa lỗi trên bằng cách 2 (import trễ), chứng minh chạy được.

<details>
<summary><strong>Lời giải chi tiết BT 2.5</strong></summary>

```python
# a.py (buggy)
from b import func_b   # kích hoạt việc load b.py NGAY tại đây

def func_a():
    return "a"

if __name__ == "__main__":
    print(func_a())
```

```python
# b.py (buggy)
from a import func_a   # a.py CHƯA định nghĩa xong func_a lúc này -> lỗi

def func_b():
    return "b"
```

Chạy `python a.py` ném lỗi **chính xác** (đã kiểm chứng thực tế, không phải suy đoán):
```
ImportError: cannot import name 'func_b' from partially initialized module 'b'
(most likely due to a circular import) (.../b.py)
```

> **Lưu ý quan trọng đã tự kiểm chứng khi soạn bài:** nếu viết ví dụ circular import bằng `import a`/`import b` (import cả module, không dùng `from ... import tên_cụ_thể`) và để 2 hàm gọi lẫn nhau, Python **không** ném `ImportError` — 2 module vẫn import thành công (vì lúc import chỉ cần biết module tồn tại, chưa cần tên bên trong sẵn sàng). Lỗi thật sự chỉ lộ ra khi bạn dùng `from module import tên_cụ_thể` — vì lúc đó Python cần tên đó **đã được định nghĩa xong** trong module kia ngay tại thời điểm import.

**Sửa bằng import trễ:**

```python
# a.py (fixed)
def func_a():
    return "a"

if __name__ == "__main__":
    print(func_a())
```

```python
# b.py (fixed)
def func_b():
    from a import func_a   # import trễ — a.py đã load xong khi hàm này thực sự chạy
    return "b calls " + func_a()

if __name__ == "__main__":
    print(func_b())
```

```bash
python a.py   # "a"
python b.py   # "b calls a"
```
</details>

---

## 7. Phần 2.6 — CLI với `typer`

### Lý thuyết

```python
import typer

app = typer.Typer()

@app.command()
def stats(file: str, col: str):
    """Compute mean/median/stdev for a column in a CSV file."""
    ...

if __name__ == "__main__":
    app()
```

`typer` tự sinh `--help`, kiểm tra kiểu dữ liệu tham số dựa trên type hint — dùng thay `argparse` (verbose hơn) trong lộ trình này.

### Bài tập 2.6 — CLI 1 lệnh đơn giản

- [ ] **BT 2.6.1** — Viết 1 CLI `typer` với lệnh `greet --name Alice --times 3` in "Hello, Alice!" 3 lần.

<details>
<summary><strong>Lời giải chi tiết BT 2.6</strong></summary>

```python
"""Minimal typer CLI demo."""
import typer

app = typer.Typer()

@app.command()
def greet(
    name: str = typer.Option(..., "--name"),
    times: int = typer.Option(1, "--times"),
) -> None:
    """Print a greeting `times` times."""
    for _ in range(times):
        typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

```bash
# Lưu ý: khi app CHỈ có 1 lệnh duy nhất, Typer coi nó là "single-command app"
# và KHÔNG cần gõ tên lệnh (không phải "python greet_cli.py greet ..."):
python greet_cli.py --name Alice --times 3
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

> Đây là hành vi đã kiểm chứng thực tế của Typer — khác với mytools CLI ở dự án tổng hợp bên dưới, nơi có **2** lệnh (`stats`, `fib-benchmark`) nên **phải** gõ tên lệnh trước các option.
</details>

---

## 8. Dự án tổng hợp — Package `mytools/` hoàn chỉnh

Dùng lại **toàn bộ** Phần 2.1-2.6: tham số hàm chuẩn, `lru_cache`, absolute import, `if __name__=="__main__"`, và CLI `typer` — đóng gói thành 1 package cài đặt được thật.

### Yêu cầu

- [ ] **DA.1** — Cấu trúc package `mytools/` dùng src-layout: `pyproject.toml`, `src/mytools/{__init__.py, __main__.py, cli.py, stats.py, fib.py}`.
- [ ] **DA.2** — `stats.py` chứa hàm `compute_stats`/`load_column` (đọc CSV, tính mean/median/stdev) — áp dụng type hint + docstring như Phần 2.1.
- [ ] **DA.3** — `fib.py` chứa `fibonacci_cached`/`fibonacci_uncached`/`benchmark` — tái sử dụng nguyên vẹn lời giải Phần 2.3.
- [ ] **DA.4** — `cli.py` dùng **absolute import** (Phần 2.4) để gọi `stats.py` và `fib.py`, xây 2 lệnh CLI (`stats`, `fib-benchmark`) bằng `typer` (Phần 2.6).
- [ ] **DA.5** — `__init__.py` expose API công khai (Phần 2.4); `__main__.py` cho phép chạy `python -m mytools`.
- [ ] **DA.6** — Cài bằng `uv pip install -e .`, chứng minh chạy đúng cả qua entry point lẫn `python -m mytools`, và chạy được từ **thư mục khác** (không cần sửa `sys.path`).

<details>
<summary><strong>Lời giải chi tiết — Dự án tổng hợp</strong></summary>

**Cấu trúc:**

```
mytools-project/
├── pyproject.toml
├── src/
│   └── mytools/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── stats.py
│       └── fib.py
└── sample_data.csv
```

**`pyproject.toml`:**

```toml
[project]
name = "mytools"
version = "0.1.0"
description = "Personal utility CLI for Unit 01 exercises"
requires-python = ">=3.11"
dependencies = ["typer>=0.12.0"]

[project.scripts]
mytools = "mytools.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mytools"]
```

**`src/mytools/stats.py`:**

```python
"""Compute basic descriptive statistics for a numeric CSV column."""
from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass


@dataclass
class ColumnStats:
    mean: float
    median: float
    stdev: float
    count: int


def load_column(file_path: str, column: str) -> list[float]:
    """Read a numeric column from a CSV file into a list of floats."""
    values: list[float] = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise ValueError(f"Column '{column}' not found in {file_path}")
        for row in reader:
            values.append(float(row[column]))
    return values


def compute_stats(values: list[float]) -> ColumnStats:
    """Compute mean, median, and sample standard deviation."""
    if not values:
        raise ValueError("Cannot compute stats on an empty list")
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return ColumnStats(
        mean=statistics.mean(values),
        median=statistics.median(values),
        stdev=stdev,
        count=len(values),
    )
```

**`src/mytools/fib.py`** (reuses the Section 2.3 solution verbatim):

```python
"""Fibonacci implementations demonstrating functools.lru_cache."""
from __future__ import annotations

import time
from functools import lru_cache


def fibonacci_uncached(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_uncached(n - 1) + fibonacci_uncached(n - 2)


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def benchmark(n: int = 32) -> None:
    start = time.perf_counter()
    result_uncached = fibonacci_uncached(n)
    time_uncached = time.perf_counter() - start

    fibonacci_cached.cache_clear()
    start = time.perf_counter()
    result_cached = fibonacci_cached(n)
    time_cached = time.perf_counter() - start

    assert result_uncached == result_cached
    print(f"fibonacci({n}) = {result_uncached}")
    print(f"Uncached: {time_uncached:.4f}s")
    print(f"Cached  : {time_cached:.6f}s")
    print(f"Speedup : {time_uncached / max(time_cached, 1e-9):.0f}x")
```

**`src/mytools/cli.py`** (absolute import + typer, Phần 2.4 + 2.6):

```python
"""Typer-based command-line interface for the mytools package."""
from __future__ import annotations

import typer

from mytools.fib import benchmark
from mytools.stats import compute_stats, load_column

app = typer.Typer(help="Personal utility CLI built for the AI Engineer roadmap.")


@app.command()
def stats(
    file: str = typer.Option(..., "--file", help="Path to the CSV file."),
    col: str = typer.Option(..., "--col", help="Name of the numeric column."),
) -> None:
    """Compute mean, median, and stdev for a numeric column in a CSV file."""
    values = load_column(file, col)
    result = compute_stats(values)
    typer.echo(f"count : {result.count}")
    typer.echo(f"mean  : {result.mean:.4f}")
    typer.echo(f"median: {result.median:.4f}")
    typer.echo(f"stdev : {result.stdev:.4f}")


@app.command()
def fib_benchmark(n: int = typer.Option(32, "--n")) -> None:
    """Compare cached vs. uncached Fibonacci runtime."""
    benchmark(n)


if __name__ == "__main__":
    app()
```

**`src/mytools/__init__.py`:**

```python
"""mytools — personal utility CLI for the AI Engineer roadmap, Unit 01."""
from mytools.stats import ColumnStats, compute_stats, load_column

__all__ = ["ColumnStats", "compute_stats", "load_column"]
__version__ = "0.1.0"
```

**`src/mytools/__main__.py`:**

```python
"""Enables `python -m mytools ...` as an alternative to the installed command."""
from mytools.cli import app

if __name__ == "__main__":
    app()
```

**Cài đặt và chạy (kiểm chứng DA.6):**

```bash
uv pip install -e .

mytools stats --file sample_data.csv --col price
python -m mytools stats --file sample_data.csv --col price

# Chạy từ thư mục khác — chứng minh không cần sys.path
cd /tmp && mytools stats --file /path/to/sample_data.csv --col price

mytools fib-benchmark --n 32
```

> **Kết quả đo thật** khi soạn bài này: `stdev` phụ thuộc dữ liệu CSV cụ thể của bạn; `fibonacci(32)` cached nhanh hơn uncached khoảng **8,000x** (số liệu thực tế đo được, sẽ khác nhau tuỳ máy — quan trọng là cached luôn nhanh hơn hàng nghìn lần).
</details>

---

## 9. Đáp án Quiz

- [ ] Đã trả lời cả 3 câu bằng lời của bạn trong `SUBMISSION.md` trước khi mở phần dưới.

<details>
<summary><strong>Đáp án tham khảo</strong></summary>

**Câu 1: LEGB tra cứu theo thứ tự nào?**
> Local → Enclosing → Global → Built-in. Dừng ngay khi tìm thấy tên ở tầng đầu tiên khớp.

**Câu 2: `lru_cache` lưu gì và rủi ro bộ nhớ là gì?**
> Lưu bảng ánh xạ từ tổ hợp tham số (hashable) → giá trị trả về, trong RAM tiến trình. Rủi ro: nếu hàm gọi với rất nhiều tổ hợp tham số khác nhau, cache phình to không kiểm soát (`maxsize=None` = không giới hạn). Tham số phải hashable — không dùng được với `list`/`dict`.

**Câu 3: Vì sao relative import lỗi khi chạy trực tiếp file?**
> Relative import cần Python biết file thuộc package nào (`__package__`), chỉ có khi module được import như 1 phần của package. Chạy trực tiếp `python somefile.py` khiến Python coi nó là script độc lập, không có package bao quanh → `ImportError: attempted relative import with no known parent package`. Cách đúng: chạy qua `python -m package.somefile`, hoặc dùng absolute import.
</details>

---

## 10. Tổng kết & bước tiếp theo

- ✅ Nắm vững tham số hàm, LEGB, first-class function, `functools`.
- ✅ Hiểu module/package/import — nền tảng cấu trúc mọi dự án sau này.
- ✅ Package `mytools/` hoàn chỉnh, cài đặt được, có CLI thật — mẫu cấu trúc tái sử dụng cho mọi package sau này trong lộ trình.

**Bài tiếp theo:** U01-04 — OOP và thiết kế lớp trong Python.

---

## 11. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Bài tập Phần 2.1-2.6 (mỗi phần có ít nhất 1 bài đúng) | 3 |
| Package cài đặt đúng, `pyproject.toml` chuẩn src-layout | 2 |
| CLI chạy đúng cả 2 cách (entry point + `python -m`), chạy từ thư mục khác | 3 |
| `lru_cache` benchmark có số liệu rõ ràng | 1 |
| Trả lời đúng 3/3 câu quiz | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
