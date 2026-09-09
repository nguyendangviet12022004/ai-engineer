# U01-02 — Python Core: Kiểu dữ liệu & Luồng điều khiển

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 8 · **Độ khó:** Dễ
> **Tài liệu tham khảo:** Harvard CS50P · Fluent Python (Ramalho) ch.2-3 · Python Docs Tutorial
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.
> **Cách dùng file này:** Đọc lý thuyết từng phần → làm ngay bài tập của phần đó (tick ☐ → ☑) → cuối bài có 1 dự án tổng hợp dùng lại mọi thứ đã làm.

---

## 1. Mục tiêu bài học

- [ ] Hiểu mutable vs immutable, cạm bẫy `id()`/tham chiếu.
- [ ] Chọn đúng cấu trúc dữ liệu dựa trên độ phức tạp thao tác.
- [ ] Dùng thành thạo slicing, unpacking, starred expression, walrus operator.
- [ ] Viết comprehension và generator expression.
- [ ] Format chuỗi bằng f-string, viết regex cơ bản.
- [ ] Phân biệt shallow copy vs deep copy.
- [ ] Xây `python_core.py` với các hàm tiện ích tái sử dụng cho các bài sau.

---

## 2. Phần 2.1 — Mutable vs Immutable, và `id()`

### Lý thuyết

Mọi thứ trong Python đều là object, mỗi object có 1 `id()` (địa chỉ bộ nhớ, cố định trong vòng đời object).

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes` | `list`, `dict`, `set`, `bytearray` |

```python
a = [1, 2, 3]
b = a          # b tham chiếu tới CÙNG 1 object với a
b.append(4)
print(a)       # [1, 2, 3, 4] — a cũng đổi vì a và b trỏ chung 1 vùng nhớ!
print(a is b)  # True — is so sánh id(), không so sánh giá trị
```

**Cạm bẫy mutable default argument:**

```python
def append_item(item, container=[]):   # NGUY HIỂM — [] chỉ tạo 1 LẦN DUY NHẤT
    container.append(item)
    return container

print(append_item(1))  # [1]
print(append_item(2))  # [1, 2]  <-- không phải [2]!

# Cách sửa đúng:
def append_item_fixed(item, container=None):
    if container is None:
        container = []   # tạo list MỚI mỗi lần gọi
    container.append(item)
    return container
```

### Bài tập 2.1 — Aliasing và mutable default

- [ ] **BT 2.1.1** — Viết hàm `add_score(name, scores={})` (cố ý sai như trên), gọi 2 lần với `name` khác nhau, quan sát bug, giải thích bằng lời.
- [ ] **BT 2.1.2** — Sửa lại hàm trên đúng chuẩn dùng `None` làm default.
- [ ] **BT 2.1.3** — Viết 3 dòng code chứng minh `a is b` (aliasing) khác `a == b` (giá trị) khi 2 list có nội dung giống hệt nhau nhưng được tạo riêng biệt.

<details>
<summary><strong>Lời giải chi tiết BT 2.1</strong></summary>

```python
def add_score_buggy(name: str, scores: dict = {}) -> dict:
    """Intentionally buggy: mutable default dict is shared across calls."""
    scores[name] = scores.get(name, 0) + 1
    return scores

print(add_score_buggy("alice"))  # {'alice': 1}
print(add_score_buggy("bob"))    # {'alice': 1, 'bob': 1}  <- alice leaked in!


def add_score_fixed(name: str, scores: dict | None = None) -> dict:
    """Correct version: a fresh dict is created on every call."""
    if scores is None:
        scores = {}
    scores[name] = scores.get(name, 0) + 1
    return scores

print(add_score_fixed("alice"))  # {'alice': 1}
print(add_score_fixed("bob"))    # {'bob': 1}  <- independent, as expected


list_a = [1, 2, 3]
list_b = [1, 2, 3]
print(list_a == list_b)   # True  — same VALUE
print(list_a is list_b)   # False — different OBJECT in memory
```
</details>

---

## 3. Phần 2.2 — Độ phức tạp: list vs tuple vs set vs dict

### Lý thuyết

| Thao tác | `list` | `tuple` | `set` | `dict` |
|---|---|---|---|---|
| Truy cập theo index | O(1) | O(1) | — | — (theo key) |
| Tìm phần tử (`x in container`) | **O(n)** | O(n) | **O(1)** trung bình | **O(1)** trung bình |
| Thêm ở cuối | O(1) khấu hao | không đổi được | O(1) trung bình | O(1) trung bình |
| Thêm/xoá ở đầu | O(n) | không đổi được | O(1) trung bình | O(1) trung bình |
| Có thứ tự? | Có | Có | Không | Có (từ 3.7+) |
| Hashable? | Không | **Có, nếu mọi phần tử bên trong hashable** | Không | Không |

**Hệ quả thực tế:** kiểm tra "X có trong Y không" nhiều lần → dùng `set`/`dict` thay `list`. Chênh lệch O(n) vs O(1) trở nên khủng khiếp khi n lớn.

`tuple` hashable vì immutable (giá trị không đổi trong vòng đời → hash ổn định); `list` mutable → không hashable → không dùng làm key/phần tử set được.

### Bài tập 2.2 — Đo độ phức tạp bằng số thật

- [ ] **BT 2.2.1** — Tạo 1 `list` và 1 `set` cùng chứa 100,000 số nguyên ngẫu nhiên. Đo thời gian kiểm tra 1000 giá trị ngẫu nhiên có nằm trong mỗi cấu trúc không (`timeit`). So sánh và ghi lại tỉ lệ chênh lệch.
- [ ] **BT 2.2.2** — Thử `d = {}; d[[1,2]] = "x"` và `d[(1,2)] = "x"` — quan sát lỗi, giải thích vì sao.

<details>
<summary><strong>Lời giải chi tiết BT 2.2</strong></summary>

```python
import random
import timeit

data_list = list(range(100_000))
data_set = set(data_list)
queries = [random.randint(0, 200_000) for _ in range(1000)]

def search_in_list():
    return [q in data_list for q in queries]

def search_in_set():
    return [q in data_set for q in queries]

time_list = timeit.timeit(search_in_list, number=10)
time_set = timeit.timeit(search_in_set, number=10)

print(f"list: {time_list:.4f}s")
print(f"set : {time_set:.4f}s")
print(f"set is {time_list / time_set:.0f}x faster")
```

```python
d = {}
d[(1, 2)] = "ok"        # tuple làm key — OK, tuple is hashable
try:
    d[[1, 2]] = "fail"  # TypeError: unhashable type: 'list'
except TypeError as e:
    print("Error:", e)
```
</details>

---

## 4. Phần 2.3 — Slicing, Unpacking, Starred Expression, Walrus

### Lý thuyết

```python
data = [10, 20, 30, 40, 50]

data[1:4]      # [20, 30, 40]
data[::-1]     # [50, 40, 30, 20, 10] — đảo ngược
data[::2]      # [10, 30, 50]

first, *middle, last = data
# first = 10, middle = [20, 30, 40], last = 50

# Walrus operator (:=), Python 3.8+ — gán NGAY TRONG một biểu thức
if (n := len(data)) > 3:
    print(f"List has {n} elements")   # tránh gọi len(data) 2 lần
```

### Bài tập 2.3 — Unpacking thực chiến

- [ ] **BT 2.3.1** — Cho 1 list gồm 10 số, dùng unpacking lấy ra: số đầu tiên, số cuối cùng, và list các số ở giữa — chỉ trong 1 dòng.
- [ ] **BT 2.3.2** — Viết 1 vòng `while` đọc từng dòng từ 1 list mô phỏng file, dùng walrus operator để vừa gán vừa kiểm tra điều kiện dừng.

<details>
<summary><strong>Lời giải chi tiết BT 2.3</strong></summary>

```python
numbers = list(range(10))
first, *middle, last = numbers
print(first, middle, last)   # 0 [1, 2, 3, 4, 5, 6, 7, 8] 9

lines = ["line1", "line2", "", "line3"]
it = iter(lines)
while (line := next(it, None)) is not None and line != "":
    print("Processing:", line)
```
</details>

---

## 5. Phần 2.4 — Comprehension và Generator Expression

### Lý thuyết

```python
squares = [x**2 for x in range(10)]                  # list comprehension — tạo NGAY
squares_gen = (x**2 for x in range(10))                # generator — LAZY, tính khi cần
even_set = {x for x in range(10) if x % 2 == 0}          # set comprehension
square_map = {x: x**2 for x in range(5)}                  # dict comprehension
```

Dùng generator khi dữ liệu lớn và chỉ duyệt 1 lần — không giữ toàn bộ kết quả trong RAM. Đào sâu ở Bài 1.7.

### Bài tập 2.4 — Comprehension thay vòng lặp

- [ ] **BT 2.4.1** — Viết dict comprehension tạo bảng ánh xạ `{số: bình phương}` chỉ cho các số chẵn từ 0-20.
- [ ] **BT 2.4.2** — So sánh RAM ước lượng (dùng `sys.getsizeof`) giữa `[x for x in range(1_000_000)]` và `(x for x in range(1_000_000))`.

<details>
<summary><strong>Lời giải chi tiết BT 2.4</strong></summary>

```python
even_squares = {x: x**2 for x in range(21) if x % 2 == 0}
print(even_squares)

import sys
list_version = [x for x in range(1_000_000)]
gen_version = (x for x in range(1_000_000))
print(f"list: {sys.getsizeof(list_version):,} bytes")
print(f"generator: {sys.getsizeof(gen_version):,} bytes")
# generator chỉ tốn vài trăm byte cố định, bất kể "range" lớn thế nào
```
</details>

---

## 6. Phần 2.5 — f-string, Format Spec, Regex cơ bản

### Lý thuyết

```python
name, score = "Alice", 92.567
f"{name}: {score:.2f}"       # 'Alice: 92.57'
f"{score:>10.2f}"            # căn phải, độ rộng 10
f"{1234567:,}"                 # '1,234,567'
f"{name=}"                     # 'name=Alice' — debug nhanh (Python 3.8+)
```

```python
import re
pattern = r"\d+"                     # r"" = raw string, tránh xung đột escape
re.findall(pattern, "abc123def456")  # ['123', '456']
re.search(pattern, "abc123")          # Match object hoặc None
re.sub(pattern, "#", "abc123")        # 'abc#'
```

### Bài tập 2.5 — Regex trích xuất thông tin

- [ ] **BT 2.5.1** — Viết regex trích tất cả địa chỉ email hợp lệ trong 1 đoạn văn bản.
- [ ] **BT 2.5.2** — Viết regex trích số điện thoại Việt Nam (định dạng `0xxxxxxxxx` hoặc `+84xxxxxxxxx`, đầu số 3/5/7/8/9).
- [ ] **BT 2.5.3** — Viết regex trích ngày tháng định dạng `dd/mm/yyyy` hoặc `dd-mm-yyyy`.

<details>
<summary><strong>Lời giải chi tiết BT 2.5</strong></summary>

```python
import re

sample_text = """
Contact John at john.doe@company.com or call 0912345678.
Meeting scheduled on 15/03/2026, follow-up on 20-04-2026.
Backup contact: +84987654321, alt email: support@ai-lab.io
"""

EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+84|0)(?:3|5|7|8|9)\d{8}"
DATE_PATTERN = r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"

print("Emails:", re.findall(EMAIL_PATTERN, sample_text))
# ['john.doe@company.com', 'support@ai-lab.io']
print("Phones:", re.findall(PHONE_PATTERN, sample_text))
# ['0912345678', '+84987654321']
print("Dates:", re.findall(DATE_PATTERN, sample_text))
# ['15/03/2026', '20-04-2026']
```
</details>

---

## 7. Phần 2.6 — Shallow Copy vs Deep Copy

### Lý thuyết

```python
import copy

original = {"name": "Bob", "scores": [80, 90]}

shallow = original.copy()              # hoặc copy.copy(original)
shallow["scores"].append(100)
print(original["scores"])              # [80, 90, 100] — BỊ ĐỔI THEO!

deep = copy.deepcopy(original)
deep["scores"].append(200)
print(original["scores"])              # [80, 90, 100] — KHÔNG đổi
```

`.copy()`/slicing chỉ sao chép **tầng ngoài cùng**. Nếu bên trong còn list/dict lồng nhau, chúng vẫn được **chia sẻ tham chiếu**. Muốn độc lập hoàn toàn phải dùng `copy.deepcopy()`.

### Bài tập 2.6 — Bẫy shallow copy kinh điển

- [ ] **BT 2.6.1** — Tạo `matrix = [[0]*3]*3`, gán `matrix[0][0] = 1`, quan sát tất cả 3 dòng bị đổi. Giải thích và sửa đúng bằng list comprehension.
- [ ] **BT 2.6.2** — Viết hàm `backup_config(config)` dùng `deepcopy` đúng cách để đảm bảo sửa bản backup không ảnh hưởng config gốc, dù config lồng nhau bao nhiêu tầng.

<details>
<summary><strong>Lời giải chi tiết BT 2.6</strong></summary>

```python
matrix_buggy = [[0] * 3] * 3      # 3 tham chiếu tới CÙNG 1 list con!
matrix_buggy[0][0] = 1
print(matrix_buggy)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] <- tất cả đều đổi!

matrix_fixed = [[0] * 3 for _ in range(3)]   # 3 list ĐỘC LẬP
matrix_fixed[0][0] = 1
print(matrix_fixed)   # [[1, 0, 0], [0, 0, 0], [0, 0, 0]] <- đúng!


import copy

def backup_config(config: dict) -> dict:
    """Return a fully independent copy, safe to mutate without affecting
    the original — regardless of how deeply nested config is."""
    return copy.deepcopy(config)

config = {"db": {"host": "localhost", "port": 5432}}
backup = backup_config(config)
backup["db"]["port"] = 9999
print(config["db"]["port"])   # 5432 — KHÔNG đổi, đúng như mong đợi
```
</details>

---

## 8. Dự án tổng hợp — Công cụ phân tích văn bản mini

Dùng lại **toàn bộ** kiến thức Phần 2.1-2.6 để xây `python_core.py`: 1 module tiện ích hoàn chỉnh + 1 script phân tích văn bản thật kết hợp nhiều hàm với nhau.

### Yêu cầu

- [ ] **DA.1** — Viết đủ 15 hàm tiện ích trong `python_core.py` (danh sách bên dưới), mỗi hàm có type hint + docstring.
- [ ] **DA.2** — Viết `test_python_core.py` test đủ 15 hàm, `pytest -v` pass 100%.
- [ ] **DA.3** — Viết script `analyze_text.py` **kết hợp ≥5 hàm trong `python_core.py`** để phân tích 1 đoạn văn bản thật: đếm tần suất từ, tìm email/SĐT, nhóm câu theo độ dài, loại trùng lặp — xuất ra 1 báo cáo tóm tắt.
- [ ] **DA.4** — Giải 20 bài luyện tập Easy trên HackerRank/LeetCode liên quan list/dict/string, lưu lời giải vào `src/leetcode/`.

### Danh sách 15 hàm cần có trong `python_core.py`

1. `flatten(nested)` 2. `word_frequency(text)` 3. `merge_dicts(d1, d2, on_conflict)` 4. `chunk(items, size)` 5. `group_by(items, key_fn)` 6. `dedupe_keep_order(items)` 7. `invert_dict(d)` 8. `sliding_window(items, size)` 9. `most_common(items, n)` 10. `transpose(matrix)` 11. `partition(items, predicate)` 12. `running_sum(numbers)` 13. `safe_get(d, path, default=None)` 14. `extract_emails(text)` 15. `extract_vn_phone_numbers(text)`

<details>
<summary><strong>Lời giải chi tiết — Dự án tổng hợp</strong></summary>

**`python_core.py`** (đầy đủ 15 hàm):

```python
"""Reusable Python utility functions — Unit 01, Lesson 02.

All functions here use only the standard library and are covered by
tests in test_python_core.py. Import them in later lessons instead of
rewriting the same logic.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Callable, Hashable, Iterable, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def flatten(nested: Iterable[Any]) -> list[Any]:
    """Flatten an arbitrarily nested list into a single flat list.

    Non-list iterables (str, tuple) inside are treated as leaf values,
    not flattened further, to avoid exploding strings into characters.
    """
    result: list[Any] = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def word_frequency(text: str) -> dict[str, int]:
    """Count how many times each word appears in a text (case-insensitive)."""
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return dict(Counter(words))


def merge_dicts(
    d1: dict[K, T], d2: dict[K, T], on_conflict: Callable[[T, T], T]
) -> dict[K, T]:
    """Merge two dicts, resolving key collisions with on_conflict(v1, v2)."""
    merged = dict(d1)
    for key, value in d2.items():
        merged[key] = on_conflict(merged[key], value) if key in merged else value
    return merged


def chunk(items: list[T], size: int) -> list[list[T]]:
    """Split a list into consecutive chunks of at most `size` elements."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i : i + size] for i in range(0, len(items), size)]


def group_by(items: Iterable[T], key_fn: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items into a dict of lists, keyed by key_fn(item)."""
    groups: dict[K, list[T]] = defaultdict(list)
    for item in items:
        groups[key_fn(item)].append(item)
    return dict(groups)


def dedupe_keep_order(items: Iterable[Hashable]) -> list[Hashable]:
    """Remove duplicates while preserving first-occurrence order."""
    seen: set[Hashable] = set()
    result: list[Hashable] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def invert_dict(d: dict[K, T]) -> dict[T, K]:
    """Invert a dict's keys and values. Assumes values are unique and hashable."""
    return {value: key for key, value in d.items()}


def sliding_window(items: list[T], size: int) -> list[list[T]]:
    """Generate all contiguous windows of length `size` from a sequence."""
    if size <= 0 or size > len(items):
        return []
    return [items[i : i + size] for i in range(len(items) - size + 1)]


def most_common(items: Iterable[Hashable], n: int) -> list[tuple[Hashable, int]]:
    """Return the n most frequent items with their counts, most frequent first."""
    return Counter(items).most_common(n)


def transpose(matrix: list[list[T]]) -> list[list[T]]:
    """Transpose a matrix represented as a list of row lists."""
    return [list(row) for row in zip(*matrix)]


def partition(
    items: Iterable[T], predicate: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    """Split items into (matching, non_matching) based on predicate."""
    matching: list[T] = []
    non_matching: list[T] = []
    for item in items:
        (matching if predicate(item) else non_matching).append(item)
    return matching, non_matching


def running_sum(numbers: list[float]) -> list[float]:
    """Return the cumulative sum at each position."""
    result: list[float] = []
    total = 0.0
    for n in numbers:
        total += n
        result.append(total)
    return result


def safe_get(d: dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely fetch a nested value from a dict using a dotted path like 'a.b.c'."""
    current: Any = d
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def extract_emails(text: str) -> list[str]:
    """Extract all email addresses found in a block of text."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def extract_vn_phone_numbers(text: str) -> list[str]:
    """Extract Vietnamese phone numbers in local (0xxxxxxxxx) or
    international (+84xxxxxxxxx) format."""
    pattern = r"(?:\+84|0)(?:3|5|7|8|9)\d{8}"
    return re.findall(pattern, text)
```

**`analyze_text.py`** — dự án tổng hợp, kết hợp 6 hàm từ `python_core.py`:

```python
"""Mini text analytics tool combining multiple python_core.py utilities
on a real, messy block of text — the Lesson 02 capstone project."""
import re

from python_core import (
    dedupe_keep_order,
    extract_emails,
    extract_vn_phone_numbers,
    group_by,
    most_common,
    word_frequency,
)

SAMPLE_TEXT = """
Contact John at john.doe@company.com or call 0912345678 for support.
John also replied via john.doe@company.com again yesterday.
Backup contact: +84987654321, alt email: support@ai-lab.io.
The meeting covered data pipelines, data quality, and data governance.
"""


def analyze(text: str) -> dict:
    """Run a small analytics pipeline over `text`, combining several
    python_core.py utilities into one coherent report."""
    # Split on '.' only when followed by whitespace/end-of-text, NOT on every
    # '.' — a naive text.split(".") would incorrectly break email addresses
    # like "john.doe@company.com" into multiple fake "sentences".
    sentences = [s.strip() for s in re.split(r"\.(?:\s+|$)", text.strip()) if s.strip()]
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        "emails_found": dedupe_keep_order(extract_emails(text)),
        "phones_found": dedupe_keep_order(extract_vn_phone_numbers(text)),
        "word_frequency": word_frequency(text),
        "top_words": most_common(words, 5),
        "sentences_by_length_bucket": {
            bucket: len(items)
            for bucket, items in group_by(
                sentences, key_fn=lambda s: "short" if len(s.split()) <= 6 else "long"
            ).items()
        },
    }


def print_report(report: dict) -> None:
    """Pretty-print the analysis report."""
    print("=== TEXT ANALYSIS REPORT ===")
    print(f"Unique emails : {report['emails_found']}")
    print(f"Unique phones : {report['phones_found']}")
    print(f"Top 5 words   : {report['top_words']}")
    print(f"Sentence length buckets: {report['sentences_by_length_bucket']}")


if __name__ == "__main__":
    print_report(analyze(SAMPLE_TEXT))
```

**`test_python_core.py`** (18 test, đã verify pass 100%):

```python
"""Tests for python_core.py. Run with: uv run pytest test_python_core.py -v"""
from python_core import (
    chunk, dedupe_keep_order, extract_emails, extract_vn_phone_numbers,
    flatten, group_by, invert_dict, merge_dicts, most_common, partition,
    running_sum, safe_get, sliding_window, transpose, word_frequency,
)


def test_flatten_nested_lists():
    assert flatten([1, [2, 3, [4, [5, 6]]], 7]) == [1, 2, 3, 4, 5, 6, 7]

def test_flatten_keeps_strings_intact():
    assert flatten(["ab", [1, "cd"]]) == ["ab", 1, "cd"]

def test_word_frequency_ignores_case_and_punctuation():
    assert word_frequency("Cat cat, dog. CAT!") == {"cat": 3, "dog": 1}

def test_merge_dicts_resolves_conflict():
    merged = merge_dicts({"a": 1, "b": 2}, {"b": 10, "c": 3}, on_conflict=lambda x, y: x + y)
    assert merged == {"a": 1, "b": 12, "c": 3}

def test_chunk_splits_evenly_and_with_remainder():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

def test_group_by_key_function():
    result = group_by(["apple", "banana", "avocado", "blueberry"], key_fn=lambda w: w[0])
    assert result == {"a": ["apple", "avocado"], "b": ["banana", "blueberry"]}

def test_dedupe_keep_order_preserves_first_occurrence():
    assert dedupe_keep_order([3, 1, 3, 2, 1, 4]) == [3, 1, 2, 4]

def test_invert_dict():
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}

def test_sliding_window():
    assert sliding_window([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]

def test_sliding_window_size_larger_than_list_returns_empty():
    assert sliding_window([1, 2], 5) == []

def test_most_common():
    assert most_common(["a", "b", "a", "a", "b"], 1) == [("a", 3)]

def test_transpose():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]

def test_partition():
    matching, non_matching = partition(range(6), lambda x: x % 2 == 0)
    assert matching == [0, 2, 4]
    assert non_matching == [1, 3, 5]

def test_running_sum():
    assert running_sum([1, 2, 3, 4]) == [1, 3, 6, 10]

def test_safe_get_existing_path():
    assert safe_get({"a": {"b": {"c": 42}}}, "a.b.c") == 42

def test_safe_get_missing_path_returns_default():
    assert safe_get({"a": {"b": {}}}, "a.b.c", default="missing") == "missing"

def test_extract_emails():
    text = "Contact us at hello@example.com or support@ai-lab.io."
    assert extract_emails(text) == ["hello@example.com", "support@ai-lab.io"]

def test_extract_vn_phone_numbers_local_and_international():
    text = "Call 0912345678 or +84987654321 for support."
    assert extract_vn_phone_numbers(text) == ["0912345678", "+84987654321"]
```
</details>

---

## 9. Đáp án Quiz — 10 câu về độ phức tạp

- [ ] Đã trả lời cả 10 câu bằng lời của bạn trong `SUBMISSION.md` trước khi mở phần dưới.

<details>
<summary><strong>Đáp án tham khảo</strong></summary>

1. **Tìm phần tử `list` vs `set`?** `list` O(n) — duyệt tuần tự. `set` O(1) trung bình — bảng băm, tính hash rồi tra thẳng vị trí.
2. **`dict.get(key, default)` vs `dict[key]`?** `dict[key]` ném `KeyError` nếu thiếu key. `.get()` trả `default`, không bao giờ lỗi.
3. **`tuple` có hashable không?** Có, **nếu mọi phần tử bên trong cũng hashable**. `(1, [2,3])` thì không, vì chứa list.
4. **Vì sao không dùng `list` làm default argument?** Default chỉ tạo 1 lần lúc định nghĩa hàm; nếu mutable và bị sửa, thay đổi tồn tại xuyên suốt các lần gọi khác.
5. **`a is b` vs `a == b`?** `is` so sánh danh tính (`id()`). `==` so sánh giá trị (`__eq__`).
6. **Độ phức tạp `.append()` cuối list?** O(1) khấu hao — Python cấp dư bộ nhớ, thỉnh thoảng mới phải cấp lại và copy (O(n) hiếm khi xảy ra).
7. **Vì sao `insert(0, x)` chậm hơn `.append()`?** List lưu liên tục trong bộ nhớ, chèn đầu phải dịch toàn bộ phần tử còn lại sang phải — O(n).
8. **`dict` Python 3.7+ có giữ thứ tự chèn?** Có — chính thức từ 3.7. `set` thì không đảm bảo thứ tự.
9. **Khi nào dùng `frozenset`?** Khi cần tập hợp bất biến để dùng làm key `dict` hoặc phần tử `set` khác (điều `set` thường không làm được vì không hashable).
10. **Vì sao `for item in some_dict` chỉ duyệt key?** `dict.__iter__` mặc định duyệt keys theo thiết kế ngôn ngữ. Dùng `.values()`/`.items()` để duyệt value/cặp.
</details>

---

## 10. Tổng kết & bước tiếp theo

- ✅ Hiểu sâu mutable/immutable, bẫy tham chiếu — nền tảng tránh bug khó hiểu khi xử lý dữ liệu ML.
- ✅ Biết chọn đúng cấu trúc dữ liệu theo độ phức tạp.
- ✅ `python_core.py` — 15 hàm tiện ích tái sử dụng ở Unit 03, 08.
- ✅ `analyze_text.py` — dự án nhỏ chứng minh bạn kết hợp được nhiều hàm thành 1 pipeline có ý nghĩa thật.

**Bài tiếp theo:** U01-03 — Hàm, module, package và cấu trúc import.

---

## 11. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Bài tập Phần 2.1-2.6 (mỗi phần có ít nhất 1 bài đúng) | 3 |
| `python_core.py` đủ 15 hàm, test pass 100% | 3 |
| `analyze_text.py` kết hợp đúng ≥5 hàm, chạy ra báo cáo hợp lý | 2 |
| BT2.0 (LeetCode/HackerRank): 20/20 pass | 1 |
| Trả lời đúng ≥8/10 câu quiz | 1 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
