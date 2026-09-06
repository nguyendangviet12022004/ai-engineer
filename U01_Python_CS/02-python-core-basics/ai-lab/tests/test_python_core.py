"""Tests for python_core.py. Run with: uv run pytest test_python_core.py -v"""

from ai_lab.helper.python_core import (
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
