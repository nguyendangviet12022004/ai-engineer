from typing import TypeVar
import re
from collections import Counter
from typing import Callable, Iterable, Hashable, Any
from collections import defaultdict



T = TypeVar("T")
K = TypeVar("K")

def flatten(nested: list) -> list:
  result: list = []
  for item in nested:
    if isinstance(item, list):
      result.extend(flatten(item))
    else:
      result.append(item)
  return result

def word_frequency(text: str) -> dict[str, int]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return dict(Counter(words))

def merge_dicts(d1: dict[K,T], d2: dict[K,T], on_conflict: Callable[[T,T],T]) -> dict[T,K]:
  merged = dict(d1)
  for key, value in d2.items():
      if key in merged:
          merged[key] = on_conflict(merged[key], value)
      else:
          merged[key] = value
  return merged

def chunk(items: list[T], size: int) -> list[list[T]]:
    if size <= 0:
      raise ValueError("size must be positive")

    length = len(items)
    return [items[i:i+size] for i in range(0,length,size)]

def group_by(items: Iterable[T], key_fn: Callable[[T], K]) -> dict[K,list[T]]:
  groups: dict[K, list[T]] = defaultdict(list)
  for item in items:
    groups[key_fn(item)].append(item)
  return dict(groups)

def dedupe_keep_order(items: Iterable[Hashable]) -> list[Hashable]:
  seen: set[Hashable] = set()
  result: list[Hashable] = list()

  for item in items:
    if item not in seen:
       seen.add(item)
       result.append(item)

  return result

def invert_dict(d: dict[K,T]) -> dict[T,K]:
  return {value:key for key,value in d.items()}

def sliding_window(items: list[T], size: int) -> list[list[T]]:
  length = len(items)
  if size <= 0 or size > length:
    return [] 
  return [items[i:i+size] for i in range(0, length - size + 1)]

def most_common(items: Iterable[Hashable], n: int) -> list[tuple[Hashable, int]]:
	return Counter(items).most_common(n)

def transpose(matrix: list[list[T]]) -> list[list[T]]:
	return [list(row) for row in zip(*matrix)]

def partition(items: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
	matching: list[T] = []
	non_matching: list[T] = []
	for item in items:
			(matching if predicate(item) else non_matching).append(item)
	return matching, non_matching

def running_sum(numbers: list[float]) -> list[float]:
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
