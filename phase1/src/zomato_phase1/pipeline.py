from __future__ import annotations

from pathlib import Path
from typing import List, Mapping, Optional, Tuple

from zomato_phase1.loader import load_rows_from_hf, load_rows_from_parquet, write_rows_to_parquet
from zomato_phase1.models import LoadMetadata, Restaurant
from zomato_phase1.transform import normalize_rows


def load_restaurants(
    *,
    dataset_id: str,
    cache_path: Optional[str] = None,
    use_cache: bool = True,
    max_rows: Optional[int] = None,
    hf_split: str = "train",
    write_cache_after_hf: bool = True,
) -> Tuple[List[Restaurant], LoadMetadata]:
    """
    Load, normalize, and return canonical restaurants.

    Resolution order:
    1. If ``use_cache`` and ``cache_path`` points to a non-empty Parquet file, load from cache.
    2. Else load from Hugging Face and optionally persist Parquet to ``cache_path``.
    """
    rows: List[Mapping[str, object]]
    source: str
    revision: Optional[str] = None
    loaded_from_cache = False

    if use_cache and cache_path:
        p = Path(cache_path)
        if p.exists() and p.stat().st_size > 0:
            rows = load_rows_from_parquet(cache_path)
            loaded_from_cache = True
            source = "parquet_cache"
            revision = f"parquet:{cache_path}:{int(p.stat().st_mtime)}"

    if not loaded_from_cache:
        hf_rows, revision = load_rows_from_hf(dataset_id, split=hf_split, max_rows=max_rows)
        rows = hf_rows
        source = "huggingface"
        if write_cache_after_hf and cache_path and rows:
            write_rows_to_parquet([dict(r) for r in rows], cache_path)

    if not rows:
        raise ValueError(
            "Empty dataset after load (edge case D2). "
            "Check HF_DATASET / network, or delete a corrupt cache file."
        )

    restaurants, raw_count, dropped = normalize_rows(revision or "unknown", rows)
    if not restaurants:
        raise ValueError(
            "All rows were dropped during normalization (edge case D2/D4). "
            "Inspect raw columns vs normalize rules."
        )

    meta = LoadMetadata(
        dataset_id=dataset_id,
        dataset_revision=revision,
        source=source,  # type: ignore[arg-type]
        raw_row_count=raw_count,
        normalized_row_count=len(restaurants),
        dropped_row_count=dropped,
        cache_path=cache_path,
    )
    return restaurants, meta
