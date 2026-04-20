from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable

import numpy as np
import pandas as pd


def season_from_date(value: datetime | pd.Timestamp) -> str:
    """Map a date to a meteorological season label."""

    month = value.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def mode_or_default(values: Iterable[str], default: str = "unknown") -> str:
    """Return the most common item from an iterable."""

    cleaned = [value for value in values if value not in (None, "", np.nan)]
    if not cleaned:
        return default
    return Counter(cleaned).most_common(1)[0][0]


def coefficient_of_variation(series: pd.Series) -> float:
    """Compute a safe coefficient of variation."""

    mean_value = float(series.mean()) if len(series) else 0.0
    if mean_value == 0:
        return 0.0
    return float(series.std(ddof=0) / mean_value)


def frequency_from_interval(avg_interval_days: float) -> str:
    """Map interval ranges to PM frequency buckets."""

    if avg_interval_days <= 14:
        return "Weekly"
    if avg_interval_days <= 45:
        return "Monthly"
    if avg_interval_days <= 90:
        return "Quarterly"
    if avg_interval_days <= 180:
        return "Semi-Annual"
    return "Annual"