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
