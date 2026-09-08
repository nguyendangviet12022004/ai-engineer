# U01-03 — Hàm, Module, Package và Cấu trúc Import

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 6 · **Độ khó:** TB
> **Tài liệu tham khảo:** Fluent Python (Ramalho) ch.7-9 · Python Docs: Modules
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.

---

## 1. Mục tiêu bài học

Sau bài này bạn phải:

1. Dùng thành thạo mọi kiểu tham số hàm: positional, keyword, `*args`, `**kwargs`, keyword-only.
2. Hiểu rõ quy tắc scope LEGB và phân biệt được khi nào cần `global`/`nonlocal`.
3. Biết Python coi hàm là "công dân hạng nhất" (first-class function) — truyền hàm như 1 giá trị, dùng `map`/`filter`/`functools.reduce`, và các decorator hữu ích trong `functools`.
4. Phân biệt module vs package, `__init__.py` dùng để làm gì, absolute vs relative import.
5. Hiểu `if __name__ == "__main__":` và viết được CLI bằng `typer`.
6. Biết circular import xảy ra khi nào và 3 cách phá vỡ nó.
7. Đóng gói được `mytools/` — 1 package cài bằng `pip install -e .`, chạy CLI bằng `python -m mytools`, **không cần sửa `sys.path`** khi chuyển sang máy khác.

---

## 2. Lý thuyết

### 2.1. Các kiểu tham số hàm

```python
def describe(name, age=18, *hobbies, country="VN", **extra_info):
    #        ^positional  ^default   ^*args      ^keyword-only  ^**kwargs
    ...
```

| Kiểu | Cú pháp | Ví dụ gọi |
|---|---|---|
| Positional | `def f(a, b)` | `f(1, 2)` |
| Positional có default | `def f(a, b=10)` | `f(1)` hoặc `f(1, 2)` |
| Var-positional (`*args`) | `def f(*args)` | `f(1, 2, 3)` → `args = (1, 2, 3)` |
| Keyword-only | `def f(*, a)` | `f(a=1)` — **bắt buộc** truyền bằng tên, `f(1)` sẽ lỗi |
| Var-keyword (`**kwargs`) | `def f(**kwargs)` | `f(x=1, y=2)` → `kwargs = {"x": 1, "y": 2}` |

**Vì sao cần keyword-only?** Buộc người gọi hàm phải ghi rõ tên tham số, tránh nhầm lẫn thứ tự khi hàm có nhiều tham số cùng kiểu dữ liệu:

```python
def create_user(name, *, is_admin=False, is_active=True):
    ...

create_user("Alice", is_admin=True)      # rõ ràng
# create_user("Alice", True)              # nếu is_admin không phải keyword-only,
                                           # dễ nhầm True là is_active hay is_admin
```

**Mutable default argument** (đã học ở Bài 1.2) áp dụng y hệt cho mọi tham số có default là `list`/`dict`/`set` — luôn dùng `None` rồi khởi tạo bên trong hàm.

### 2.2. Scope LEGB

Khi Python tra cứu tên 1 biến, nó tìm theo thứ tự **LEGB**:

1. **L**ocal — bên trong hàm hiện tại.
2. **E**nclosing — bên trong hàm cha (nếu đây là hàm lồng nhau/closure).
3. **G**lobal — cấp module (toàn bộ file).
4. **B**uilt-in — các tên có sẵn của Python (`len`, `print`, `range`...).

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)   # "local" — tìm thấy ngay ở Local, dừng tra cứu

    inner()
    print(x)       # "enclosing"

outer()
print(x)           # "global"
```

**`global` và `nonlocal`** dùng khi bạn muốn **gán lại** (không chỉ đọc) một biến ở scope ngoài:

```python
counter = 0

def increment():
    global counter          # không có dòng này, Python sẽ tạo biến LOCAL mới tên counter
    counter += 1             # thay vì sửa biến global

def make_counter():
    count = 0
    def increment():
        nonlocal count      # tương tự global, nhưng cho biến ở Enclosing scope
        count += 1
        return count
    return increment
```

> **Nguyên tắc thực hành:** hạn chế tối đa dùng `global` trong code thật — nó khiến hàm phụ thuộc vào trạng thái ẩn bên ngoài, rất khó test và dễ gây bug khi code lớn dần. Trong 52 tuần tới, bạn sẽ thấy cách thay thế bằng class hoặc truyền tham số tường minh.

### 2.3. First-class Function

Ở Python, hàm là 1 **giá trị** như mọi giá trị khác — có thể gán cho biến, truyền làm tham số, trả về từ hàm khác.

```python
def square(x):
    return x ** 2

operation = square          # gán hàm cho biến, không gọi (không có dấu ngoặc)
print(operation(5))         # 25

numbers = [1, 2, 3, 4]
list(map(square, numbers))              # [1, 4, 9, 16]
list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

from functools import reduce
reduce(lambda acc, x: acc + x, numbers, 0)   # 10 — tổng dồn
```

**`functools` — 3 công cụ quan trọng nhất:**

```python
from functools import lru_cache, partial, wraps

# 1. lru_cache: nhớ (memoize) kết quả hàm theo tham số đầu vào — tăng tốc hàm đệ quy/tốn kém
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 2. partial: "đóng băng" trước 1 số tham số, tạo hàm mới ít tham số hơn
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
square(5)   # 25

# 3. wraps: giữ nguyên __name__/__doc__ của hàm gốc khi viết decorator
def my_decorator(func):
    @wraps(func)   # thiếu dòng này, help(decorated_func) sẽ hiện sai tên/docstring
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### 2.4. Module vs Package

- **Module** = 1 file `.py` bất kỳ. `import mymodule` sẽ chạy toàn bộ file `mymodule.py` 1 lần và cho bạn truy cập vào các tên bên trong.
- **Package** = 1 thư mục chứa nhiều module, có (hoặc trước Python 3.3 bắt buộc phải có) file `__init__.py` để đánh dấu đây là 1 package.

```
mytools/
├── __init__.py       # chạy khi "import mytools", thường dùng để expose API công khai
├── stats.py           # module con
├── cli.py              # module con
└── fib.py               # module con
```

**`__init__.py` dùng để làm gì?**
1. Đánh dấu thư mục là 1 package (bắt buộc với "regular package" — cách truyền thống, tương thích mọi phiên bản).
2. Kiểm soát API công khai: `from mytools.stats import compute_stats` có thể được rút gọn thành `from mytools import compute_stats` nếu bạn import nó vào `__init__.py`.
3. Chạy code khởi tạo khi package được import lần đầu.

**Absolute vs Relative import:**

```python
# Absolute import — luôn ghi đường dẫn đầy đủ từ gốc package
from mytools.stats import compute_stats

# Relative import — chỉ dùng BÊN TRONG package, tương đối với vị trí file hiện tại
from .stats import compute_stats      # cùng cấp (1 dấu chấm)
from ..utils import helper             # lên 1 cấp cha (2 dấu chấm)
```

> **Khuyến nghị của lộ trình:** ưu tiên **absolute import** trong hầu hết trường hợp — dễ đọc, dễ tìm kiếm (grep), và không lỗi khi refactor di chuyển file. Chỉ dùng relative import khi viết package sẽ được publish và có thể đổi tên.

### 2.5. `if __name__ == "__main__":`

```python
# stats.py
def compute_stats(numbers):
    ...

if __name__ == "__main__":
    # Chỉ chạy khi file này được thực thi TRỰC TIẾP (python stats.py)
    # KHÔNG chạy khi file này được import từ nơi khác (import stats)
    print(compute_stats([1, 2, 3]))
```

**Vì sao cần?** Mỗi module Python có 1 biến ẩn `__name__`. Khi chạy trực tiếp (`python stats.py`), `__name__` mang giá trị `"__main__"`. Khi bị import từ file khác (`import stats`), `__name__` mang giá trị `"stats"` (tên module thật). Nhờ vậy 1 file vừa dùng được như thư viện (import, không chạy code demo) vừa dùng được như script độc lập (chạy trực tiếp, có demo/CLI).

### 2.6. Circular Import

Xảy ra khi module A import module B, và module B (trực tiếp hoặc gián tiếp) lại import module A.

```python
# a.py
import b
def func_a():
    return b.func_b()

# b.py
import a          # LỖI: khi Python đang load a.py (chưa xong), b.py cố import lại a
def func_b():
    return a.func_a()
```

**3 cách phá vỡ circular import:**
1. **Tái cấu trúc code**: đưa phần dùng chung ra 1 module thứ 3 (`common.py`) mà cả A và B cùng import — cách tốt nhất, giải quyết tận gốc.
2. **Import trễ (local import)**: chuyển `import b` xuống bên trong hàm thay vì đầu file — trì hoãn việc import tới khi thực sự cần, lúc đó module kia đã load xong.
3. **Import cả module thay vì import tên cụ thể**: `import b` rồi gọi `b.func_b()` thay vì `from b import func_b` — đôi khi tránh được lỗi vì Python chỉ cần "biết" module tồn tại, chưa cần tên cụ thể bên trong đã sẵn sàng.

### 2.7. Xây CLI với `typer`

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

`typer` tự sinh `--help`, kiểm tra kiểu dữ liệu tham số dựa trên type hint, và tạo ra CLI chuyên nghiệp chỉ với vài dòng — dùng thay cho `argparse` (verbose hơn nhiều) trong lộ trình này.

---

## 3. Bài tập thực hành

### BT1 — CLI `mytools stats`

Xây package `mytools/` với lệnh CLI:

```bash
mytools stats --file data.csv --col price
```

In ra `mean`, `median`, `stdev` của cột `price` trong file CSV.

### BT2 — `lru_cache` cho Fibonacci

Viết hàm Fibonacci đệ quy **không** cache và **có** cache bằng `lru_cache`. Đo thời gian chạy `fibonacci(32)` ở cả 2 phiên bản, so sánh và giải thích chênh lệch.

### Tiêu chí hoàn thành (DoD)

- [ ] Package `mytools/` có `pyproject.toml`, cài được bằng `uv pip install -e .` (hoặc `pip install -e .`).
- [ ] Chạy được cả 2 cách: `python -m mytools stats --file data.csv --col price` **và** `mytools stats --file data.csv --col price` (sau khi cài).
- [ ] **Chạy trên thư mục khác** (không phải thư mục chứa source code) vẫn hoạt động bình thường — chứng minh package đã cài đúng, không phụ thuộc `sys.path` thủ công.
- [ ] `fibonacci` có cache nhanh hơn rõ rệt (đo bằng số, không chỉ "cảm thấy nhanh hơn") so với không cache ở `n=32`.

---

## 4. Lời giải chi tiết

### 4.1. Cấu trúc package `mytools/`

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

> **Vì sao dùng cấu trúc `src/mytools/` thay vì đặt `mytools/` ngay ở gốc?** Đây là "src layout" — cách bố trí được khuyến nghị chính thức bởi Python Packaging Authority. Nó buộc bạn phải **cài đặt** package (`pip install -e .`) trước khi import được, thay vì vô tình import trực tiếp từ thư mục làm việc — giúp phát hiện sớm lỗi thiếu khai báo dependency mà lẽ ra sẽ chỉ lộ ra khi người khác cài package của bạn.

### 4.2. `pyproject.toml`

```toml
[project]
name = "mytools"
version = "0.1.0"
description = "Personal utility CLI for Unit 01 exercises"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
]

[project.scripts]
mytools = "mytools.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mytools"]
```

**Giải thích:** khai báo `[project.scripts]` là thứ tạo ra lệnh `mytools` trong terminal sau khi cài — `pip`/`uv` sẽ tự sinh 1 file thực thi nhỏ gọi `mytools.cli:app()`.

### 4.3. `src/mytools/stats.py`

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


def compute_stats(values: list[float]) -> ColumnStats:
    """Compute mean, median, and sample standard deviation for a list of numbers."""
    if not values:
        raise ValueError("Cannot compute stats on an empty list")
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return ColumnStats(
        mean=statistics.mean(values),
        median=statistics.median(values),
        stdev=stdev,
        count=len(values),
    )


if __name__ == "__main__":
    # Quick manual check when running this file directly: python stats.py
    demo_values = [10.0, 20.0, 30.0, 40.0]
    print(compute_stats(demo_values))
```

### 4.4. `src/mytools/fib.py`

```python
"""Fibonacci implementations used to demonstrate functools.lru_cache."""
from __future__ import annotations

import time
from functools import lru_cache


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

    fibonacci_cached.cache_clear()  # ensure a fair, cold-cache comparison
    start = time.perf_counter()
    result_cached = fibonacci_cached(n)
    time_cached = time.perf_counter() - start

    assert result_uncached == result_cached, "Both implementations must agree"

    print(f"fibonacci({n}) = {result_uncached}")
    print(f"Uncached: {time_uncached:.4f}s")
    print(f"Cached  : {time_cached:.6f}s")
    print(f"Speedup : {time_uncached / max(time_cached, 1e-9):.0f}x")


if __name__ == "__main__":
    benchmark()
```

### 4.5. `src/mytools/cli.py`

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
def fib_benchmark(n: int = typer.Option(32, "--n", help="Fibonacci index to benchmark.")) -> None:
    """Compare cached vs. uncached Fibonacci runtime."""
    benchmark(n)


if __name__ == "__main__":
    app()
```

**Lưu ý quan trọng:** `cli.py` dùng **absolute import** (`from mytools.fib import benchmark`), đúng khuyến nghị ở mục 2.4 — vì package này sẽ được cài đặt (`pip install -e .`), absolute import luôn hoạt động đúng bất kể file được chạy từ đâu.

### 4.6. `src/mytools/__init__.py`

```python
"""mytools — personal utility CLI for the AI Engineer roadmap, Unit 01."""
from mytools.stats import ColumnStats, compute_stats, load_column

__all__ = ["ColumnStats", "compute_stats", "load_column"]
__version__ = "0.1.0"
```

> Đây là ví dụ cho mục 2.4: nhờ dòng import này, người dùng package có thể viết `from mytools import compute_stats` thay vì phải biết chi tiết `compute_stats` nằm ở module con `stats.py`.

### 4.7. `src/mytools/__main__.py`

```python
"""Enables `python -m mytools ...` as an alternative to the installed `mytools` command."""
from mytools.cli import app

if __name__ == "__main__":
    app()
```

> File `__main__.py` là quy ước đặc biệt của Python: khi bạn chạy `python -m <package_name>`, Python tìm và thực thi chính xác file này bên trong package.

### 4.8. Dữ liệu mẫu và cách chạy

```bash
# sample_data.csv
cat > sample_data.csv << 'EOF'
id,price,quantity
1,19.99,3
2,45.50,1
3,12.00,10
4,89.99,2
5,5.25,20
EOF
```

**Cài đặt và chạy:**

```bash
cd mytools-project
uv pip install -e .

# Cách 1: qua entry point đã cài
mytools stats --file sample_data.csv --col price

# Cách 2: qua python -m
python -m mytools stats --file sample_data.csv --col price

# Benchmark lru_cache
mytools fib-benchmark --n 32
```

**Output mẫu:**

```
count : 5
mean  : 34.5460
median: 19.9900
stdev : 34.5416
```

```
fibonacci(32) = 2178309
Uncached: 0.2332s
Cached  : 0.000029s
Speedup : 8062x
```

> **Lưu ý:** số liệu `stdev`, thời gian benchmark và speedup thực tế sẽ khác nhau tuỳ máy/phiên bản Python — output trên là kết quả thật đo được khi soạn bài này (đã chạy kiểm chứng, không phải số bịa). Đừng ngạc nhiên nếu máy bạn ra con số khác — quan trọng là **cached luôn nhanh hơn uncached hàng nghìn lần** ở `n=32`.

**Kiểm chứng DoD "chạy trên máy khác không cần sửa `sys.path`":** vì đã cài bằng `pip install -e .`, package `mytools` được đăng ký vào site-packages của venv (dưới dạng liên kết tới source, nhờ chế độ "editable"). Bạn có thể `cd` sang **bất kỳ thư mục nào khác** trên máy (miễn còn trong cùng venv) và `mytools stats ...` vẫn chạy được — không cần `sys.path.append(...)` thủ công như khi chạy trực tiếp file `.py` từ 1 thư mục cụ thể.

### 4.9. Đáp án Quiz

**Câu 1: LEGB tra cứu tên biến theo thứ tự nào?**
> Local → Enclosing → Global → Built-in. Python dừng lại ngay khi tìm thấy tên ở tầng đầu tiên khớp; nếu duyệt hết cả 4 tầng mà không thấy sẽ ném `NameError`.

**Câu 2: `lru_cache` lưu gì và rủi ro bộ nhớ là gì?**
> `lru_cache` lưu 1 bảng ánh xạ **từ tổ hợp tham số đầu vào (đã hash được) → giá trị trả về** của hàm, trong bộ nhớ RAM của tiến trình đang chạy. Rủi ro: nếu hàm được gọi với **rất nhiều tổ hợp tham số khác nhau** (ví dụ tham số là 1 đối tượng lớn thay đổi liên tục), cache sẽ phình to không kiểm soát, gây tốn RAM hoặc rò rỉ bộ nhớ nếu không giới hạn (`maxsize=None` nghĩa là không giới hạn số lượng entry — chỉ nên dùng khi chắc chắn không gian tham số hữu hạn và nhỏ, như bài toán Fibonacci). Ngoài ra, tham số phải **hashable** (immutable) — không dùng `lru_cache` được cho hàm nhận `list`/`dict` làm tham số.

**Câu 3: Vì sao relative import lỗi khi chạy trực tiếp file?**
> Relative import (`from .stats import ...`) yêu cầu Python biết được **file hiện tại đang thuộc package nào** — thông tin này chỉ có khi module được **import** như 1 phần của package (Python thiết lập biến `__package__`). Khi bạn chạy trực tiếp 1 file nằm trong package bằng `python somefile.py`, Python coi file đó là script độc lập với `__name__ == "__main__"` và **không có khái niệm package bao quanh nó**, nên `from .stats import ...` sẽ ném `ImportError: attempted relative import with no known parent package`. Cách chạy đúng khi cần relative import: chạy qua `python -m package_name.somefile` (dùng cờ `-m`, không gọi trực tiếp đường dẫn file) — hoặc đơn giản hơn, dùng absolute import như khuyến nghị ở mục 2.4.

---

## 5. Tổng kết & bước tiếp theo

Bạn đã có:
- ✅ Nắm vững mọi kiểu tham số hàm và biết khi nào dùng keyword-only để code rõ ràng hơn.
- ✅ Hiểu LEGB — nền tảng để đọc hiểu closure và decorator (sẽ đào sâu ở Bài 1.7).
- ✅ Package `mytools/` hoàn chỉnh, cài đặt được, có CLI thật — mẫu cấu trúc này sẽ tái sử dụng cho mọi package sau này trong lộ trình.

**Bài tiếp theo:** U01-04 — OOP và thiết kế lớp trong Python.

---

## 6. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Package cài đặt đúng bằng `pip install -e .`, có `pyproject.toml` đúng chuẩn | 3 |
| CLI `mytools stats` chạy đúng, cả 2 cách (entry point + `python -m`) | 3 |
| Chạy được từ thư mục khác, không sửa `sys.path` thủ công | 2 |
| `lru_cache` benchmark có số liệu rõ ràng, giải thích đúng nguyên nhân | 1 |
| Trả lời đúng 3/3 câu quiz bằng lời của bạn | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
