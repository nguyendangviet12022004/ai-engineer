# U01-03 — Hàm, Module, Package và Cấu trúc Import

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 6 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.7-9 · Python Docs: Modules
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm/lớp trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.

## Dự án xuyên suốt bài học: đóng gói `ai_lab`

Từ bài này, repo `ai-lab` (tạo ở Bài 01) được **chuyển thành 1 package Python cài đặt được**, tên `ai_lab`, có lệnh CLI `ai-lab`. **Mọi bài tập trong bài học này đều là 1 bước xây dựng package thật này** — không có ví dụ minh hoạ rời rạc nào bị bỏ đi. Cuối bài, bạn có 1 package hoàn chỉnh, không phải 1 "dự án tổng hợp" ghép thêm.

```
ai-lab/                          # repo (đã có từ Bài 01)
├── pyproject.toml               # -> Phần 2.4
├── check_env.py                 # (đã có từ Bài 01)
├── python_core.py               # (đã có từ Bài 02)
└── src/
    └── ai_lab/
        ├── __init__.py          # -> Phần 2.4
        ├── __main__.py          # -> Phần 2.4
        ├── stats.py             # -> Phần 2.1, 2.2
        ├── fib.py                # -> Phần 2.3
        └── cli.py                 # -> Phần 2.4, 2.6 (Phần 2.5 chỉ diễn tập lỗi, không sửa file thật)
```

> **Cách dùng file này:** Đọc lý thuyết từng phần → làm ngay bài tập của phần đó (thêm đúng file/hàm được chỉ định vào `ai_lab/`) → tick ☐ → ☑. Cuối bài, `ai-lab` chạy được như 1 CLI thật.

---

## 1. Mục tiêu bài học

- [ ] Dùng thành thạo mọi kiểu tham số hàm: positional, keyword, `*args`, `**kwargs`, keyword-only.
- [ ] Hiểu quy tắc scope LEGB, phân biệt khi nào cần `global`/`nonlocal`.
- [ ] Dùng `functools.lru_cache`/`wraps` đúng chỗ.
- [ ] Phân biệt module vs package, `__init__.py`, absolute vs relative import.
- [ ] Hiểu `if __name__ == "__main__":`, viết CLI bằng `typer`.
- [ ] Biết circular import xảy ra khi nào và cách phá vỡ.
- [ ] **Sản phẩm:** package `ai_lab` cài bằng `pip install -e .`, lệnh `ai-lab stats`/`ai-lab fib-benchmark` chạy được từ bất kỳ thư mục nào.

---

## 2. Phần 2.1 — Tham số hàm: xây `ai_lab/stats.py`

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

**Vì sao cần keyword-only?** Buộc người gọi hàm ghi rõ tên tham số, tránh nhầm lẫn khi nhiều tham số cùng kiểu — cực kỳ quan trọng cho hàm thống kê có nhiều tham số số học dễ nhầm thứ tự.

### Bài tập 2.1 — Viết `ai_lab/stats.py` với `compute_stats`

- [ ] **BT 2.1.1** — Tạo file `src/ai_lab/stats.py`. Viết hàm `load_column(file_path: str, column: str) -> list[float]` đọc 1 cột số từ file CSV (dùng module `csv`).
- [ ] **BT 2.1.2** — Trong cùng file, viết `compute_stats(values: list[float], *, precision: int = 4) -> ColumnStats` — `precision` **bắt buộc** truyền bằng tên (keyword-only), dùng để làm tròn kết quả. Trả về 1 `@dataclass ColumnStats(mean, median, stdev, count)` (sẽ hiểu sâu `@dataclass` ở Bài 04 — tạm dùng như 1 class chứa dữ liệu).
- [ ] **BT 2.1.3** — Gọi thử `compute_stats(values, precision=2)` (đúng) và `compute_stats(values, 2)` (sai, không dùng tên) — ghi lại lỗi Python báo.

<details>
<summary><strong>Lời giải chi tiết Phần 2.1</strong></summary>

**`src/ai_lab/stats.py`:**

```python
"""Compute basic descriptive statistics for a numeric CSV column."""
from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass


@dataclass
class ColumnStats:
    """Container for descriptive statistics of one numeric column."""

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


def compute_stats(values: list[float], *, precision: int = 4) -> ColumnStats:
    """Compute mean, median, and sample standard deviation.

    `precision` is keyword-only so callers can never accidentally swap it
    with `values` by position.
    """
    if not values:
        raise ValueError("Cannot compute stats on an empty list")
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return ColumnStats(
        mean=round(statistics.mean(values), precision),
        median=round(statistics.median(values), precision),
        stdev=round(stdev, precision),
        count=len(values),
    )
```

```python
values = [10.0, 20.0, 30.0, 40.0]

from ai_lab.stats import compute_stats
print(compute_stats(values, precision=2))    # OK

try:
    compute_stats(values, 2)                  # TypeError: takes 1 positional argument but 2 were given
except TypeError as e:
    print("Error:", e)
```
</details>

---

## 3. Phần 2.2 — Scope LEGB: thêm cache đếm lượt gọi vào `ai_lab/stats.py`

### Lý thuyết

Python tra cứu tên biến theo **LEGB**: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

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

`nonlocal` dùng khi muốn **gán lại** biến ở scope Enclosing (không chỉ đọc):

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
```

> **Nguyên tắc thực hành:** hạn chế `global` trong code thật — khiến hàm phụ thuộc trạng thái ẩn, khó test. Closure với `nonlocal` là cách "đóng gói trạng thái nhỏ" an toàn hơn nhiều.

### Bài tập 2.2 — `ai_lab/stats.py`: đếm số lần `compute_stats` được gọi

- [ ] **BT 2.2.1** — Trong `ai_lab/stats.py`, viết hàm `make_call_counter()` trả về 1 hàm đếm số lần gọi (dùng `nonlocal`) — đây sẽ là nền tảng cho việc log số lượt tính thống kê trong CLI.
- [ ] **BT 2.2.2** — Tạo 1 biến module-level `_stats_call_counter = make_call_counter()` ngay trong `ai_lab/stats.py`, gọi nó bên trong `compute_stats()` mỗi lần hàm chạy. Thêm hàm `get_stats_call_count() -> int` trả về số lần đã gọi.

<details>
<summary><strong>Lời giải chi tiết Phần 2.2</strong></summary>

Thêm vào `src/ai_lab/stats.py` — sửa lại `compute_stats` để gọi bộ đếm mỗi lần chạy:

```python
def make_call_counter():
    """Return a closure that increments and returns a call count.

    Uses `nonlocal` (not `global`) so the counter state lives inside the
    closure itself, not in freely-writable module-level global state.
    """
    count = 0
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment


_increment_call_count = make_call_counter()
_last_call_count = 0


def compute_stats(values: list[float], *, precision: int = 4) -> ColumnStats:
    """Compute mean, median, and sample standard deviation.

    `precision` is keyword-only so callers can never accidentally swap it
    with `values` by position. Also updates the module-level call counter.
    """
    global _last_call_count
    _last_call_count = _increment_call_count()
    if not values:
        raise ValueError("Cannot compute stats on an empty list")
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return ColumnStats(
        mean=round(statistics.mean(values), precision),
        median=round(statistics.median(values), precision),
        stdev=round(stdev, precision),
        count=len(values),
    )


def get_stats_call_count() -> int:
    """Return how many times compute_stats() has been called so far."""
    return _last_call_count
```

> **Bài học rút ra:** đây là ví dụ thực tế cho thấy vì sao đôi khi `global` vẫn cần thiết (đồng bộ 1 giá trị đọc được từ module scope), nhưng bọc logic tăng đếm chính bên trong closure (`nonlocal`) để giới hạn phạm vi trạng thái mutable — kết hợp cả 2 kỹ thuật đúng chỗ, thay vì để `_last_call_count += 1` tự do khắp nơi.

```python
from ai_lab.stats import compute_stats, get_stats_call_count

compute_stats([1.0, 2.0, 3.0])
compute_stats([4.0, 5.0])
print(get_stats_call_count())   # 2
```
</details>

---

## 4. Phần 2.3 — `functools.lru_cache`: xây `ai_lab/fib.py`

### Lý thuyết

```python
from functools import lru_cache, wraps

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def my_decorator(func):
    @wraps(func)   # giữ __name__/__doc__ của hàm gốc
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

`ai_lab/fib.py` sẽ là module demo trực quan cho thấy hiệu quả của `lru_cache` — dùng để giới thiệu `ai-lab` với người khác qua lệnh `ai-lab fib-benchmark`.

### Bài tập 2.3 — Viết `ai_lab/fib.py`

- [ ] **BT 2.3.1** — Tạo `src/ai_lab/fib.py` với `fibonacci_uncached(n)` và `fibonacci_cached(n)` (dùng `lru_cache`).
- [ ] **BT 2.3.2** — Viết `benchmark(n=32)` đo và in thời gian chạy cả 2, cùng tỉ lệ speedup.
- [ ] **BT 2.3.3** — Viết decorator `@timeit` (dùng `wraps`) trong cùng file, áp dụng thử lên `fibonacci_uncached` để in thời gian mỗi lần gọi — chứng minh `wrapper.__name__` vẫn đúng là `"fibonacci_uncached"` nhờ `@wraps`.

<details>
<summary><strong>Lời giải chi tiết Phần 2.3</strong></summary>

**`src/ai_lab/fib.py`:**

```python
"""Fibonacci implementations demonstrating functools.lru_cache and wraps."""
from __future__ import annotations

import time
from functools import lru_cache, wraps


def timeit(func):
    """Decorator that prints how long the wrapped function took to run."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


def fibonacci_uncached(n: int) -> int:
    """Plain recursive Fibonacci — exponential time complexity O(2^n)."""
    if n < 2:
        return n
    return fibonacci_uncached(n - 1) + fibonacci_uncached(n - 2)


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    """Recursive Fibonacci memoized with lru_cache — linear time O(n)."""
    if n < 2:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def benchmark(n: int = 32) -> None:
    """Compare the runtime of the cached and uncached implementations."""
    start = time.perf_counter()
    result_uncached = fibonacci_uncached(n)
    time_uncached = time.perf_counter() - start

    fibonacci_cached.cache_clear()
    start = time.perf_counter()
    result_cached = fibonacci_cached(n)
    time_cached = time.perf_counter() - start

    assert result_uncached == result_cached, "Both implementations must agree"

    print(f"fibonacci({n}) = {result_uncached}")
    print(f"Uncached: {time_uncached:.4f}s")
    print(f"Cached  : {time_cached:.6f}s")
    print(f"Speedup : {time_uncached / max(time_cached, 1e-9):.0f}x")
```

```python
from ai_lab.fib import fibonacci_uncached, timeit

fibonacci_uncached_timed = timeit(fibonacci_uncached)
fibonacci_uncached_timed(28)
print(fibonacci_uncached_timed.__name__)   # "fibonacci_uncached" — preserved by @wraps
```
</details>

---

## 5. Phần 2.4 — Đóng gói package: `pyproject.toml`, `__init__.py`, `__main__.py`

### Lý thuyết

**Module** = 1 file `.py`. **Package** = 1 thư mục chứa nhiều module, đánh dấu bằng `__init__.py`.

**`__init__.py`** dùng để: (1) đánh dấu thư mục là package, (2) expose API công khai (`from ai_lab import compute_stats` thay vì `from ai_lab.stats import compute_stats`).

**Absolute vs relative import:**

```python
from ai_lab.stats import compute_stats     # absolute — luôn dùng trong lộ trình này
from .stats import compute_stats            # relative — chỉ dùng bên trong package
```

> **Khuyến nghị:** ưu tiên absolute import — dễ đọc, dễ grep, không lỗi khi refactor.

**`if __name__ == "__main__":`** — chỉ chạy khi file được thực thi trực tiếp. **`__main__.py`** — file đặc biệt, chạy khi gõ `python -m <package>`.

### Bài tập 2.4 — Biến `ai-lab` thành package cài đặt được

- [ ] **BT 2.4.1** — Di chuyển `src/ai_lab/stats.py` và `src/ai_lab/fib.py` (đã viết ở Phần 2.1-2.3) vào đúng vị trí src-layout: `src/ai_lab/`.
- [ ] **BT 2.4.2** — Viết `src/ai_lab/__init__.py`, dùng **absolute import** expose `compute_stats`, `load_column` ra cấp package.
- [ ] **BT 2.4.3** — Viết `src/ai_lab/__main__.py` cho phép chạy `python -m ai_lab`.
- [ ] **BT 2.4.4** — Viết `pyproject.toml` ở gốc repo `ai-lab` (src-layout, entry point `ai-lab`).
- [ ] **BT 2.4.5** — Cài bằng `uv pip install -e .`. Chứng minh `from ai_lab import compute_stats` chạy được từ **bất kỳ thư mục nào** trên máy (không phải chỉ trong `ai-lab/`).

<details>
<summary><strong>Lời giải chi tiết Phần 2.4</strong></summary>

**Cấu trúc cuối cùng:**

```
ai-lab/
├── pyproject.toml
├── check_env.py          # từ Bài 01, vẫn ở gốc repo, không thuộc package
├── python_core.py         # từ Bài 02, vẫn ở gốc repo, không thuộc package
└── src/
    └── ai_lab/
        ├── __init__.py
        ├── __main__.py
        ├── stats.py        # Phần 2.1 + 2.2
        ├── fib.py            # Phần 2.3
        └── cli.py              # Phần 2.6
```

**`pyproject.toml`:**

```toml
[project]
name = "ai-lab"
version = "0.1.0"
description = "Personal AI Engineer roadmap toolkit — grows with every lesson."
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
]

[project.scripts]
ai-lab = "ai_lab.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ai_lab"]
```

**`src/ai_lab/__init__.py`:**

```python
"""ai_lab — personal AI Engineer roadmap toolkit.

Grows one module per lesson: stats (U01-03), models/data/pipeline (U01-04),
and onward through the rest of the 52-week roadmap.
"""
from ai_lab.stats import ColumnStats, compute_stats, load_column

__all__ = ["ColumnStats", "compute_stats", "load_column"]
__version__ = "0.1.0"
```

**`src/ai_lab/__main__.py`:**

```python
"""Enables `python -m ai_lab ...` as an alternative to the installed `ai-lab` command."""
from ai_lab.cli import app

if __name__ == "__main__":
    app()
```

**Cài đặt và kiểm chứng:**

```bash
cd ai-lab
uv pip install -e .

# Từ thư mục hoàn toàn khác:
cd /tmp
python -c "from ai_lab import compute_stats; print(compute_stats([1.0, 2.0, 3.0], precision=2))"
```
</details>

---

## 6. Phần 2.5 — Diễn tập Circular Import (không đưa vào package thật)

### Lý thuyết

Xảy ra khi module A import module B, và B (trực tiếp/gián tiếp) lại import A. **3 cách phá vỡ:** (1) tái cấu trúc — đưa phần dùng chung ra module thứ 3, (2) import trễ — chuyển `import` xuống trong hàm, (3) import cả module thay vì `from ... import tên`.

> Bài tập này **cố ý gây lỗi** trong 2 file tạm — không sửa vào `ai_lab/` thật, vì mục đích là quan sát cơ chế lỗi, không phải giữ lại code lỗi.

### Bài tập 2.5 — Tự tái tạo circular import bằng chính 2 module thật của `ai_lab`

- [ ] **BT 2.5.1** — Tạo 1 bản sao tạm của `ai_lab/stats.py` và `ai_lab/cli.py` (đặt tên `stats_buggy.py`/`cli_buggy.py` trong thư mục `scratch/`, **ngoài** package thật) — cho `stats_buggy.py` thêm dòng `from cli_buggy import app` ở đầu file (giả lập tình huống bạn lỡ tay làm `stats.py` phụ thuộc ngược vào `cli.py`), và `cli_buggy.py` có `from stats_buggy import compute_stats` ở đầu. Chạy và ghi lại `ImportError` chính xác.
- [ ] **BT 2.5.2** — Giải thích bằng lời: nếu lỡ viết đúng tình huống này vào `ai_lab/` thật, bạn sẽ sửa bằng cách nào trong 3 cách đã học — và vì sao (gợi ý: `cli.py` phụ thuộc `stats.py` là hướng phụ thuộc đúng, nên hướng cần phá vỡ là chiều ngược lại).

<details>
<summary><strong>Lời giải chi tiết Phần 2.5</strong></summary>

**`scratch/stats_buggy.py`:**

```python
from cli_buggy import app   # SAI: stats không nên phụ thuộc cli

def compute_stats(values):
    return sum(values) / len(values)
```

**`scratch/cli_buggy.py`:**

```python
from stats_buggy import compute_stats   # cli phụ thuộc stats — đây là hướng ĐÚNG

app = "fake_typer_app"
```

Chạy `python scratch/stats_buggy.py` (sau khi thêm 1 dòng gọi thử ở cuối) ném lỗi thật:
```
ImportError: cannot import name 'app' from partially initialized module 'cli_buggy'
(most likely due to a circular import) (.../scratch/cli_buggy.py)
```

**Giải thích (BT 2.5.2):** Trong kiến trúc `ai_lab` thật, `cli.py` **nên** phụ thuộc `stats.py` (CLI gọi vào logic nghiệp vụ), không bao giờ nên có chiều ngược lại. Nếu phát hiện `stats.py` cần thứ gì đó từ `cli.py`, đó là dấu hiệu thiết kế sai — nên **tái cấu trúc** (cách 1): đưa phần dùng chung đó ra 1 module thứ 3 (ví dụ `ai_lab/types.py` chứa các kiểu dữ liệu chung), thay vì dùng import trễ để "chữa cháy" — vì import trễ chỉ che giấu vấn đề kiến trúc, không giải quyết tận gốc.
</details>

---

## 7. Phần 2.6 — CLI với `typer`: hoàn thiện `ai_lab/cli.py`

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

`typer` tự sinh `--help`, kiểm tra kiểu dữ liệu dựa trên type hint. **Lưu ý quan trọng đã kiểm chứng thực tế:** khi `Typer()` app chỉ có **1 lệnh duy nhất**, gọi CLI **không cần** gõ tên lệnh (`ai-lab --file ... --col ...`). Khi có **từ 2 lệnh trở lên**, **phải** gõ tên lệnh (`ai-lab stats --file ...`). `ai_lab/cli.py` sẽ có 2 lệnh ngay từ đầu nên luôn cần gõ tên lệnh.

### Bài tập 2.6 — Hoàn thiện `ai_lab/cli.py`

- [ ] **BT 2.6.1** — Viết `src/ai_lab/cli.py`: import `compute_stats`/`load_column` từ `ai_lab.stats` (absolute import — Phần 2.4) và `benchmark` từ `ai_lab.fib` (Phần 2.3). Định nghĩa 2 lệnh: `stats` (dùng `precision` keyword-only từ Phần 2.1) và `fib-benchmark`.
- [ ] **BT 2.6.2** — Chạy `ai-lab stats --file <csv> --col <cột> --precision 2` và `ai-lab fib-benchmark --n 30` — cả 2 phải hoạt động.
- [ ] **BT 2.6.3** — Chạy `ai-lab --help` và `python -m ai_lab stats --help`, xác nhận cả 2 cách chạy đều hiển thị đúng danh sách lệnh.

<details>
<summary><strong>Lời giải chi tiết Phần 2.6 — hoàn thiện package</strong></summary>

**`src/ai_lab/cli.py`** (điểm hội tụ của toàn bộ Phần 2.1-2.4):

```python
"""Typer-based command-line interface for the ai_lab package."""
from __future__ import annotations

import typer

from ai_lab.fib import benchmark
from ai_lab.stats import compute_stats, load_column

app = typer.Typer(help="ai-lab — personal AI Engineer roadmap toolkit.")


@app.command()
def stats(
    file: str = typer.Option(..., "--file", help="Path to the CSV file."),
    col: str = typer.Option(..., "--col", help="Name of the numeric column."),
    precision: int = typer.Option(4, "--precision", help="Decimal places to round to."),
) -> None:
    """Compute mean, median, and stdev for a numeric column in a CSV file."""
    values = load_column(file, col)
    result = compute_stats(values, precision=precision)
    typer.echo(f"count : {result.count}")
    typer.echo(f"mean  : {result.mean}")
    typer.echo(f"median: {result.median}")
    typer.echo(f"stdev : {result.stdev}")


@app.command()
def fib_benchmark(n: int = typer.Option(32, "--n", help="Fibonacci index to benchmark.")) -> None:
    """Compare cached vs. uncached Fibonacci runtime."""
    benchmark(n)


if __name__ == "__main__":
    app()
```

**Chạy toàn bộ package đã hoàn thiện:**

```bash
uv pip install -e .

ai-lab stats --file sample_data.csv --col price --precision 2
ai-lab fib-benchmark --n 30
python -m ai_lab stats --file sample_data.csv --col price
ai-lab --help
```

**Kết quả đo thật khi soạn bài này:** `fibonacci(30)` cached nhanh hơn uncached khoảng **4,400x** (số liệu thực tế đo được, khác nhau tuỳ máy — quan trọng là cached luôn nhanh hơn hàng nghìn lần).
</details>

---

## 8. Đáp án Quiz

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

## 9. Tổng kết & bước tiếp theo

- ✅ `ai_lab` giờ là 1 package cài đặt được thật, có CLI 2 lệnh, chạy từ bất kỳ đâu.
- ✅ Mọi khái niệm (tham số hàm, LEGB, `lru_cache`, module/package, import) đều nằm trong code thật của `ai_lab`, không có ví dụ minh hoạ nào bị bỏ đi.
- ✅ Bài 04 sẽ tiếp tục mở rộng **chính package này** với các module OOP (`models/`, `data/`, `config.py`, `pipeline.py`) và thêm lệnh `ai-lab train`.

**Bài tiếp theo:** U01-04 — OOP và thiết kế lớp trong Python.

---

## 10. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| `ai_lab/stats.py` đúng (keyword-only `precision`, closure đếm lượt gọi) | 2 |
| `ai_lab/fib.py` đúng (`lru_cache`, `@timeit` giữ đúng `__name__`) | 2 |
| Package cài đặt đúng bằng `pip install -e .`, đúng src-layout | 2 |
| CLI `ai-lab stats`/`ai-lab fib-benchmark` chạy đúng, cả entry point lẫn `python -m ai_lab`, chạy từ thư mục khác | 2 |
| Diễn tập circular import đúng, giải thích hướng phụ thuộc hợp lý | 1 |
| Trả lời đúng 3/3 câu quiz | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
