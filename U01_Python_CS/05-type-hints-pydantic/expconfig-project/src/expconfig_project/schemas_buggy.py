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
