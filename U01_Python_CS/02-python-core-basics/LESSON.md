# U01-02 — Python Core: Kiểu dữ liệu & Luồng điều khiển

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 8 · **Độ khó:** Dễ
> **Tài liệu tham khảo:** Harvard CS50P · Fluent Python (Ramalho) ch.2-3 · Python Docs Tutorial
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.

---

## 1. Mục tiêu bài học

Sau bài này bạn phải:

1. Hiểu rõ mutable vs immutable, và cạm bẫy `id()`/tham chiếu khi truyền object qua hàm.
2. Chọn đúng cấu trúc dữ liệu (`list`/`tuple`/`set`/`dict`) dựa trên **độ phức tạp thao tác**, không chọn theo thói quen.
3. Dùng thành thạo slicing, unpacking, starred expression, walrus operator (`:=`).
4. Viết comprehension (list/dict/set) và generator expression thay cho vòng lặp tường minh khi phù hợp.
5. Format chuỗi bằng f-string và viết được regex cơ bản để trích xuất thông tin.
6. Phân biệt copy nông (shallow) vs copy sâu (deep), tránh bug kinh điển "sửa 1 chỗ, đổi luôn chỗ khác".
7. Tạo module `python_core.py` gồm **15 hàm tiện ích** tái sử dụng được cho các bài sau.

---

## 2. Lý thuyết

### 2.1. Mutable vs Immutable, và `id()`

Trong Python, **mọi thứ đều là object**, và mỗi object có 1 `id()` (địa chỉ bộ nhớ, cố định trong vòng đời object đó).

| Immutable (không đổi được) | Mutable (đổi được tại chỗ) |
|---|---|
| `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes` | `list`, `dict`, `set`, `bytearray` |

```python
a = [1, 2, 3]
b = a          # b tham chiếu tới CÙNG 1 object với a, không phải bản sao
b.append(4)
print(a)       # [1, 2, 3, 4] — a cũng bị đổi vì a và b trỏ chung 1 vùng nhớ!
print(a is b)  # True — is so sánh id(), không so sánh giá trị
```

**Cạm bẫy kinh điển: mutable default argument.**

```python
def append_item(item, container=[]):   # NGUY HIỂM — [] chỉ được tạo 1 LẦN DUY NHẤT
    container.append(item)
    return container

print(append_item(1))  # [1]
print(append_item(2))  # [1, 2]  <-- không phải [2]! container cũ vẫn còn nguyên
```

Lý do: giá trị mặc định của tham số được **tạo 1 lần duy nhất khi hàm được định nghĩa**, không phải mỗi lần gọi hàm. Cách sửa đúng:

```python
def append_item_fixed(item, container=None):
    if container is None:
        container = []   # tạo list MỚI mỗi lần gọi
    container.append(item)
    return container
```

### 2.2. Độ phức tạp thao tác: list vs tuple vs set vs dict

| Thao tác | `list` | `tuple` | `set` | `dict` |
|---|---|---|---|---|
| Truy cập theo index | O(1) | O(1) | không hỗ trợ | không hỗ trợ (dùng key) |
| Tìm phần tử (`x in container`) | **O(n)** | O(n) | **O(1)** trung bình | **O(1)** trung bình (theo key) |
| Thêm phần tử ở cuối | O(1) khấu hao | không đổi được | O(1) trung bình | O(1) trung bình |
| Thêm/xoá ở đầu | O(n) | không đổi được | O(1) trung bình | O(1) trung bình |
| Có thứ tự? | Có | Có | Không (trước Python 3.7 hoàn toàn không đảm bảo) | Có (từ 3.7+, theo thứ tự chèn) |
| Trùng lặp? | Cho phép | Cho phép | Không (tự loại trùng) | Key không trùng |
| Hashable (dùng làm key/phần tử set)? | Không | **Có, nếu mọi phần tử bên trong đều hashable** | Không | Không |

**Hệ quả thực tế cực kỳ quan trọng:** nếu bạn cần kiểm tra "phần tử X có nằm trong tập hợp Y không" nhiều lần, dùng `set`/`dict` thay vì `list` — chênh lệch O(n) vs O(1) trở nên khủng khiếp khi n lớn (ví dụ: kiểm tra 100,000 từ có nằm trong danh sách stopword 50,000 từ hay không — dùng `list` sẽ chậm gấp hàng nghìn lần dùng `set`).

### 2.3. Tại sao tuple hashable còn list thì không?

`hash()` yêu cầu giá trị của object **không được đổi** trong suốt vòng đời (nếu đổi thì hash cũ sẽ sai, phá vỡ cấu trúc dict/set bên trong). Vì `tuple` immutable → hashable (miễn là mọi phần tử bên trong cũng hashable). `list` mutable → không hashable → không thể dùng làm key của dict hay phần tử của set.

```python
d = {}
d[(1, 2)] = "ok"        # tuple làm key — OK
d[[1, 2]] = "fail"      # TypeError: unhashable type: 'list'
```

### 2.4. Slicing, Unpacking, Starred Expression, Walrus Operator

```python
data = [10, 20, 30, 40, 50]

# Slicing: [start:stop:step]
data[1:4]      # [20, 30, 40]
data[::-1]     # [50, 40, 30, 20, 10] — đảo ngược
data[::2]      # [10, 30, 50] — mỗi 2 phần tử

# Unpacking
first, *middle, last = data
# first = 10, middle = [20, 30, 40], last = 50

# Walrus operator (:=) — gán giá trị NGAY TRONG một biểu thức, từ Python 3.8
if (n := len(data)) > 3:
    print(f"List has {n} elements")   # tránh phải gọi len(data) 2 lần
```

### 2.5. Comprehension và Generator Expression

```python
squares = [x**2 for x in range(10)]                  # list comprehension — tạo NGAY toàn bộ list
squares_gen = (x**2 for x in range(10))               # generator expression — LAZY, tính khi cần
even_set = {x for x in range(10) if x % 2 == 0}        # set comprehension
square_map = {x: x**2 for x in range(5)}               # dict comprehension
```

**Khi nào dùng generator thay vì list?** Khi dữ liệu lớn và bạn chỉ cần duyệt qua 1 lần — generator không giữ toàn bộ kết quả trong RAM cùng lúc. Sẽ đào sâu ở Bài 1.7.

### 2.6. f-string và Format Spec

```python
name, score = "Alice", 92.567
f"{name}: {score:.2f}"       # 'Alice: 92.57' — làm tròn 2 chữ số thập phân
f"{score:>10.2f}"            # căn phải, độ rộng 10 ký tự
f"{1234567:,}"                # '1,234,567' — phân cách hàng nghìn
f"{name=}"                    # 'name=Alice' — debug nhanh, in cả tên biến (Python 3.8+)
```

### 2.7. Regex cơ bản với module `re`

```python
import re

pattern = r"\d+"                     # r"" = raw string, tránh xung đột escape sequence
re.findall(pattern, "abc123def456")  # ['123', '456']
re.search(pattern, "abc123")          # Match object, hoặc None nếu không tìm thấy
re.sub(pattern, "#", "abc123")        # 'abc#' — thay thế
```

### 2.8. Shallow Copy vs Deep Copy

```python
import copy

original = {"name": "Bob", "scores": [80, 90]}

shallow = original.copy()              # hoặc copy.copy(original)
shallow["scores"].append(100)
print(original["scores"])              # [80, 90, 100] — BỊ ĐỔI THEO vì "scores" vẫn trỏ chung 1 list!

deep = copy.deepcopy(original)
deep["scores"].append(200)
print(original["scores"])              # [80, 90, 100] — KHÔNG đổi, deepcopy tạo bản sao độc lập hoàn toàn
```

**Quy tắc:** `copy()`/slicing chỉ sao chép **tầng ngoài cùng** — nếu bên trong còn chứa list/dict lồng nhau, chúng vẫn được **chia sẻ tham chiếu**. Muốn độc lập hoàn toàn phải dùng `copy.deepcopy()`.

---

## 3. Bài tập thực hành

### BT1 — Viết 15 hàm tiện ích trong `python_core.py`

Không dùng thư viện ngoài (chỉ dùng thư viện chuẩn Python). Mỗi hàm phải có type hint và docstring.

1. `flatten(nested)` — làm phẳng list lồng nhau ở bất kỳ độ sâu nào.
2. `word_frequency(text)` — đếm tần suất xuất hiện của mỗi từ trong 1 đoạn văn bản.
3. `merge_dicts(d1, d2, on_conflict)` — gộp 2 dict, khi trùng key thì áp dụng hàm `on_conflict(v1, v2)`.
4. `chunk(items, size)` — chia 1 list thành các list con có độ dài `size`.
5. `group_by(items, key_fn)` — nhóm các phần tử theo giá trị trả về của `key_fn`.
6. `dedupe_keep_order(items)` — loại bỏ phần tử trùng lặp nhưng giữ nguyên thứ tự xuất hiện đầu tiên.
7. `invert_dict(d)` — đảo key/value của dict (giả định value là duy nhất và hashable).
8. `sliding_window(items, size)` — sinh ra các cửa sổ trượt kích thước `size` từ 1 dãy.
9. `most_common(items, n)` — trả về `n` phần tử xuất hiện nhiều nhất, kèm số lần xuất hiện.
10. `transpose(matrix)` — chuyển vị 1 ma trận biểu diễn dạng list-of-lists.
11. `partition(items, predicate)` — chia 1 list thành 2 list: thoả và không thoả điều kiện.
12. `running_sum(numbers)` — trả về danh sách tổng dồn (cumulative sum).
13. `safe_get(d, path, default=None)` — lấy giá trị từ dict lồng nhau theo đường dẫn kiểu `"a.b.c"`, trả về `default` nếu không tồn tại.
14. `extract_emails(text)` — dùng regex trích tất cả địa chỉ email hợp lệ trong văn bản.
15. `extract_vn_phone_numbers(text)` — dùng regex trích số điện thoại Việt Nam (định dạng `0xxxxxxxxx` hoặc `+84xxxxxxxxx`).

### BT2 — 20 bài luyện tập độ khó Easy

Giải 20 bài trên HackerRank/LeetCode liên quan tới thao tác list/dict/string cơ bản (tự chọn, ghi lại link + lời giải vào thư mục `src/leetcode/`).

### BT3 — Regex thực chiến

Viết script trích xuất từ 1 đoạn văn bản mẫu: email, số điện thoại Việt Nam, và ngày tháng theo định dạng `dd/mm/yyyy` hoặc `dd-mm-yyyy`.

### Tiêu chí hoàn thành (DoD)

- [ ] `python_core.py` có đủ 15 hàm, mỗi hàm có type hint + docstring, có test đi kèm (`test_python_core.py`).
- [ ] 20/20 bài luyện tập BT2 pass.
- [ ] Giải thích đúng vì sao 5 đoạn code "đánh lừa" (mutable default, shallow copy...) cho kết quả bất ngờ — viết vào `SUBMISSION.md`.

---

## 4. Lời giải chi tiết

### 4.1. Lời giải BT1 — `python_core.py`

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
    not flattened further, to avoid accidentally exploding strings
    into individual characters.
    """
    result: list[Any] = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def word_frequency(text: str) -> dict[str, int]:
    """Count how many times each word appears in a text.

    Words are lowercased and matched using a simple alphanumeric regex,
    so punctuation is ignored.
    """
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return dict(Counter(words))


def merge_dicts(
    d1: dict[K, T],
    d2: dict[K, T],
    on_conflict: Callable[[T, T], T],
) -> dict[K, T]:
    """Merge two dicts, resolving key collisions with on_conflict(v1, v2)."""
    merged = dict(d1)
    for key, value in d2.items():
        if key in merged:
            merged[key] = on_conflict(merged[key], value)
        else:
            merged[key] = value
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
    international (+84xxxxxxxxx) format.
    """
    pattern = r"(?:\+84|0)(?:3|5|7|8|9)\d{8}"
    return re.findall(pattern, text)
```

**Giải thích các quyết định thiết kế quan trọng:**

- `flatten`: dùng đệ quy, kiểm tra `isinstance(item, list)` chứ không dùng `isinstance(item, Iterable)` — vì string cũng là Iterable, nếu không cẩn thận sẽ bị "flatten" luôn cả string thành từng ký tự.
- `merge_dicts`: nhận `on_conflict` như 1 hàm (higher-order function) thay vì hardcode "lấy giá trị mới" hay "cộng dồn" — linh hoạt hơn, người gọi tự quyết định logic xử lý xung đột.
- `group_by` dùng `defaultdict(list)` để tránh phải kiểm tra `if key not in groups` thủ công.
- `dedupe_keep_order` dùng `set` để kiểm tra "đã thấy chưa" trong O(1) thay vì `if item not in result` (O(n) mỗi lần, khiến cả hàm thành O(n²)).
- `safe_get` xử lý bài toán rất thực tế khi làm việc với JSON response từ API — tránh phải viết `d.get("a", {}).get("b", {}).get("c")` dài dòng và dễ lỗi.
- Regex `extract_vn_phone_numbers`: đầu số di động Việt Nam hợp lệ hiện tại bắt đầu bằng 3, 5, 7, 8, 9 (sau số 0 hoặc +84).

### 4.2. Test đi kèm — `test_python_core.py`

```python
"""Tests for python_core.py. Run with: uv run pytest test_python_core.py -v"""
from python_core import (
    chunk,
    dedupe_keep_order,
    extract_emails,
    extract_vn_phone_numbers,
    flatten,
    group_by,
    invert_dict,
    merge_dicts,
    most_common,
    partition,
    running_sum,
    safe_get,
    sliding_window,
    transpose,
    word_frequency,
)


def test_flatten_nested_lists():
    assert flatten([1, [2, 3, [4, [5, 6]]], 7]) == [1, 2, 3, 4, 5, 6, 7]


def test_flatten_keeps_strings_intact():
    assert flatten(["ab", [1, "cd"]]) == ["ab", 1, "cd"]


def test_word_frequency_ignores_case_and_punctuation():
    result = word_frequency("Cat cat, dog. CAT!")
    assert result == {"cat": 3, "dog": 1}


def test_merge_dicts_resolves_conflict():
    d1, d2 = {"a": 1, "b": 2}, {"b": 10, "c": 3}
    merged = merge_dicts(d1, d2, on_conflict=lambda x, y: x + y)
    assert merged == {"a": 1, "b": 12, "c": 3}


def test_chunk_splits_evenly_and_with_remainder():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_group_by_key_function():
    words = ["apple", "banana", "avocado", "blueberry"]
    result = group_by(words, key_fn=lambda w: w[0])
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
    data = {"a": {"b": {"c": 42}}}
    assert safe_get(data, "a.b.c") == 42


def test_safe_get_missing_path_returns_default():
    data = {"a": {"b": {}}}
    assert safe_get(data, "a.b.c", default="missing") == "missing"


def test_extract_emails():
    text = "Contact us at hello@example.com or support@ai-lab.io."
    assert extract_emails(text) == ["hello@example.com", "support@ai-lab.io"]


def test_extract_vn_phone_numbers_local_and_international():
    text = "Call 0912345678 or +84987654321 for support."
    assert extract_vn_phone_numbers(text) == ["0912345678", "+84987654321"]
```

### 4.3. Lời giải BT3 — Trích xuất email / SĐT / ngày tháng

```python
"""Extract emails, Vietnamese phone numbers, and dates from free text."""
import re

sample_text = """
Contact John at john.doe@company.com or call 0912345678.
Meeting scheduled on 15/03/2026, follow-up on 20-04-2026.
Backup contact: +84987654321, alt email: support@ai-lab.io
"""

EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+84|0)(?:3|5|7|8|9)\d{8}"
DATE_PATTERN = r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"

emails = re.findall(EMAIL_PATTERN, sample_text)
phones = re.findall(PHONE_PATTERN, sample_text)
dates = re.findall(DATE_PATTERN, sample_text)

print("Emails:", emails)
# ['john.doe@company.com', 'support@ai-lab.io']

print("Phone numbers:", phones)
# ['0912345678', '+84987654321']

print("Dates:", dates)
# ['15/03/2026', '20-04-2026']
```

### 4.4. Đáp án Quiz — 10 câu về độ phức tạp

**Câu 1: Tìm phần tử trong `list` vs `set` — độ phức tạp?**
> `list`: O(n) — Python phải duyệt tuần tự từng phần tử cho tới khi tìm thấy hoặc hết list. `set`: O(1) trung bình — dùng bảng băm (hash table), tính hash của giá trị cần tìm rồi tra thẳng tới vị trí, không cần duyệt.

**Câu 2: `dict.get(key, default)` vs `dict[key]`?**
> `dict[key]` ném `KeyError` nếu key không tồn tại. `dict.get(key, default)` trả về `default` (mặc định là `None`) nếu key không tồn tại, không bao giờ ném lỗi — an toàn hơn khi bạn không chắc key có tồn tại hay không, và code ngắn gọn hơn việc phải viết `try/except KeyError`.

**Câu 3: `tuple` có hashable không?**
> Có, **với điều kiện mọi phần tử bên trong tuple đó cũng phải hashable**. Ví dụ `(1, 2, "a")` hashable, nhưng `(1, [2, 3])` thì **không** — vì bên trong chứa 1 `list` (mutable, không hashable).

**Câu 4: Vì sao không nên dùng `list` làm default argument?**
> Vì giá trị mặc định chỉ được tạo **1 lần duy nhất** tại thời điểm định nghĩa hàm (không phải mỗi lần gọi). Nếu default là `list`/`dict` (mutable) và hàm có sửa đổi nó (`.append()`, `[key] = value`...), thay đổi đó sẽ **tồn tại xuyên suốt** giữa các lần gọi hàm khác nhau — gây bug rất khó phát hiện. Luôn dùng `None` làm default rồi khởi tạo mutable object mới bên trong hàm.

**Câu 5: `a is b` vs `a == b` khác nhau thế nào?**
> `is` so sánh **danh tính** (identity) — 2 biến có trỏ tới cùng 1 object trong bộ nhớ hay không (so sánh `id()`). `==` so sánh **giá trị** (equality) — nội dung 2 object có bằng nhau hay không (gọi `__eq__`). Hai list có nội dung giống hệt nhau nhưng được tạo riêng biệt sẽ có `==` là `True` nhưng `is` là `False`.

**Câu 6: Độ phức tạp thêm 1 phần tử vào cuối `list`?**
> O(1) khấu hao (amortized). Python cấp phát dư bộ nhớ cho list, nên hầu hết lần `.append()` chỉ ghi thêm vào vùng nhớ đã cấp sẵn (O(1) thật sự). Thỉnh thoảng khi vùng nhớ đầy, Python phải cấp phát vùng mới lớn hơn và copy toàn bộ phần tử cũ sang (O(n)) — nhưng việc này xảy ra đủ hiếm để **trung bình** vẫn tính là O(1).

**Câu 7: Vì sao thêm phần tử vào đầu `list` (`insert(0, x)`) chậm hơn thêm vào cuối?**
> Vì list lưu trữ liên tục trong bộ nhớ (giống mảng), thêm vào đầu buộc phải **dịch chuyển toàn bộ các phần tử còn lại sang phải 1 vị trí** — O(n). Thêm vào cuối không cần dịch chuyển gì.

**Câu 8: `dict` trong Python 3.7+ có giữ thứ tự chèn không?**
> Có — từ Python 3.7, việc dict giữ thứ tự chèn (insertion order) trở thành đặc tả chính thức của ngôn ngữ (trước đó là chi tiết cài đặt của CPython 3.6, chưa được đảm bảo). Điều này khác với `set`, vẫn **không đảm bảo thứ tự**.

**Câu 9: Khi nào nên dùng `frozenset` thay vì `set`?**
> Khi bạn cần 1 tập hợp **không đổi** (immutable) để có thể dùng làm key của `dict` hoặc phần tử của `set` khác — điều mà `set` (mutable) không làm được vì không hashable.

**Câu 10: Vì sao `for item in some_dict:` chỉ duyệt qua key, không phải value?**
> Vì `dict` mặc định implement `__iter__` để duyệt qua keys (đây là quyết định thiết kế của ngôn ngữ, tối ưu cho trường hợp dùng phổ biến nhất). Muốn duyệt value dùng `.values()`, muốn duyệt cả cặp dùng `.items()`.

### 4.5. Giải thích 5 đoạn code "đánh lừa" (theo yêu cầu DoD)

**Đoạn 1 — Mutable default argument:**
```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag("a"))  # ['a']
print(add_tag("b"))  # ['a', 'b']  <- bất ngờ!
```
> Giải thích: `[]` chỉ tạo 1 lần khi định nghĩa hàm, mọi lần gọi hàm không truyền `tags` đều dùng chung 1 list đó.

**Đoạn 2 — Aliasing (list gán = tham chiếu, không copy):**
```python
matrix = [[0] * 3] * 3      # 3 dòng, TƯỞNG là độc lập
matrix[0][0] = 1
print(matrix)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] <- cả 3 dòng đều đổi!
```
> Giải thích: `[[0]*3] * 3` tạo ra 1 list chứa **3 tham chiếu tới CÙNG 1 list con** `[0, 0, 0]`, không phải 3 list độc lập. Sửa đúng: `[[0]*3 for _ in range(3)]`.

**Đoạn 3 — Shallow copy với dict lồng nhau:**
```python
config = {"db": {"host": "localhost", "port": 5432}}
backup = config.copy()
backup["db"]["port"] = 9999
print(config["db"]["port"])   # 9999 <- config gốc cũng bị đổi!
```
> Giải thích: `.copy()` chỉ sao chép tầng ngoài. Key `"db"` trong cả 2 dict vẫn trỏ chung 1 object dict con. Phải dùng `copy.deepcopy(config)`.

**Đoạn 4 — Vòng lặp với closure trễ (late binding):**
```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # [2, 2, 2] <- không phải [0, 1, 2]!
```
> Giải thích: closure trong Python không "chụp ảnh" giá trị của `i` tại thời điểm tạo lambda — nó chỉ giữ **tham chiếu tới biến `i`**. Khi các hàm được gọi (sau khi vòng lặp kết thúc), `i` đã mang giá trị cuối cùng là `2`. Sửa đúng: `lambda i=i: i` (dùng default argument để "chốt" giá trị ngay lúc tạo).

**Đoạn 5 — So sánh float:**
```python
print(0.1 + 0.2 == 0.3)   # False <- không phải True!
```
> Giải thích: số thực dấu phẩy động (floating point) không biểu diễn chính xác tuyệt đối mọi giá trị thập phân trong hệ nhị phân — `0.1 + 0.2` thực chất bằng `0.30000000000000004`. Không bao giờ so sánh `==` trực tiếp giữa 2 số float; dùng `abs(a - b) < 1e-9` hoặc `math.isclose(a, b)`.

---

## 5. Tổng kết & bước tiếp theo

Bạn đã có:
- ✅ Hiểu sâu mutable/immutable và các bẫy tham chiếu — nền tảng để không dính bug khó hiểu khi xử lý dữ liệu ML sau này.
- ✅ Biết chọn đúng cấu trúc dữ liệu theo độ phức tạp thao tác, không theo thói quen.
- ✅ Module `python_core.py` với 15 hàm tiện ích — sẽ dùng lại ở nhiều bài sau (đặc biệt Unit 03, 08).

**Bài tiếp theo:** U01-03 — Hàm, module, package và cấu trúc import.

---

## 6. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| 15 hàm đầy đủ, đúng logic, có type hint + docstring (100% tiếng Anh) | 4 |
| Test pass toàn bộ (`pytest -v`) | 2 |
| BT2: 20/20 bài luyện tập pass | 2 |
| Giải thích đúng ≥4/5 đoạn code "đánh lừa" bằng lời của chính bạn | 2 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel.
