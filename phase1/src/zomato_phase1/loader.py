from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def load_rows_from_parquet(path: str) -> List[Dict[str, Any]]:
    import pandas as pd

    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return []
    df = pd.read_parquet(path)
    return df.to_dict(orient="records")


def write_rows_to_parquet(rows: List[Dict[str, Any]], path: str) -> None:
    import pandas as pd

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(out, index=False)


def load_rows_from_hf(
    dataset_id: str,
    *,
    split: str = "train",
    max_rows: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    from datasets import load_dataset

    ds = load_dataset(dataset_id, split=split)
    revision = None
    try:
        revision = str(ds.info.version) if ds.info.version is not None else None
    except Exception:
        revision = None
    if revision in (None, "None"):
        revision = getattr(ds.info, "dataset_name", None) or "unknown"

    n = len(ds)
    if max_rows is not None:
        n = min(n, max_rows)
    subset = ds.select(range(n))
    try:
        rows = subset.to_list()
    except Exception:
        rows = [subset[i] for i in range(len(subset))]
    return rows, revision
