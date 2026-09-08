from functools import lru_cache, wraps
from typing import Callable
import time





def benchmark(func: Callable):
  @wraps(func) 
  def wrapper(*args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"Time of {func.__name__}: {elapsed}s")
    return result
  return wrapper



@benchmark
@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
  """Plain recursive Fibonacci — exponential time complexity O(2^n)."""
  if n < 2:
      return n
  return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)

@benchmark
def fibonacci_uncached(n: int) -> int:
    """Plain recursive Fibonacci — exponential time complexity O(2^n)."""
    if n < 2:
        return n
    return fibonacci_uncached(n - 1) + fibonacci_uncached(n - 2)


if __name__ == "__main__":
  cache = fibonacci_cached(10)
  uncache = fibonacci_uncached(10)