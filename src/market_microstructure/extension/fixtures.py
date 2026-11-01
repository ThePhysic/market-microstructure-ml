"""Independently generated spot test observations, never historical evidence."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import random

import numpy as np
import pandas as pd

from ..data import NORMALIZED_COLUMNS


def synthetic_states(dates: list[str], rows_per_date: int = 120, seed: int = 42) -> pd.DataFrame:
    if type(rows_per_date) is not int or not 40 <= rows_per_date <= 100000:
        raise ValueError("rows_per_date must be 40-100000")
    records = []
    source_order = 0
    for day in dates:
        stamp = int(datetime.fromisoformat(day).replace(hour=12, tzinfo=timezone.utc).timestamp()) * 1000000
        rng = random.Random(int(hashlib.sha256(f"spot-fixture:{seed}:{day}".encode()).hexdigest(), 16))
        size_rng = random.Random(int(hashlib.sha256(f"spot-size:{seed}:{day}".encode()).hexdigest(), 16))
        price_ticks = 3000000
        for index in range(rows_per_date):
            source_order += 1
            price_ticks += rng.choice([-3, -1, 0, 0, 1, 3])
            receive = stamp + index * 100000
            row = {"exchange": "bitstamp", "symbol": "BTCUSD", "session_date": day,
                   "segment_id": f"synthetic:{day}", "source_file": f"synthetic:{day}",
                   "source_row_position": index+1, "provenance_key": f"synthetic:{seed}:{day}:{index}",
                   "event_time_us": receive-1000, "receive_time_us": receive, "source_order": source_order}
            for level in range(1, 6):
                row[f"bid_price_{level}"] = (price_ticks-level+1)/100
                row[f"ask_price_{level}"] = (price_ticks+level+1)/100
                row[f"bid_size_{level}"] = size_rng.randint(100, 100000)/1000000
                row[f"ask_size_{level}"] = size_rng.randint(100, 100000)/1000000
            records.append(row)
    result = pd.DataFrame(records, columns=NORMALIZED_COLUMNS)
    for name in ("source_row_position", "source_order", "event_time_us", "receive_time_us"):
        result[name] = result[name].astype(np.int64)
    return result
