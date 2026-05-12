#!/usr/bin/env python3
"""
Force Phase 1 dataset load: download from Hugging Face (if needed), normalize, write parquet cache.

Ignores SKIP_DATASET_LOAD for this run so data is always extracted when you execute this script.

Usage (from repo root, with venv activated):
  python3 scripts/prefetch_zomato_dataset.py

Requires network on first run. Reuses DATA_CACHE_PATH when the file already exists (use_cache=True).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

for rel in (
    "src",
    "phase1/src",
    "phase2/src",
    "phase3/src",
    "phase4/src",
    "phase5/src",
    "phase6/src",
):
    p = ROOT / rel
    if p.is_dir():
        sys.path.insert(0, str(p))

from recommender.config import Settings  # noqa: E402
from zomato_phase1 import load_restaurants  # noqa: E402


def main() -> None:
    env_file = ROOT / ".env"
    settings = Settings(
        skip_dataset_load=False,
        _env_file=str(env_file) if env_file.is_file() else None,
    )
    cache = Path(settings.data_cache_path)
    cache.parent.mkdir(parents=True, exist_ok=True)

    print(f"dataset_id={settings.hf_dataset!r}")
    print(f"cache_path={settings.data_cache_path!r}")
    print("Loading (this may take several minutes on first download)...")

    restaurants, meta = load_restaurants(
        dataset_id=settings.hf_dataset,
        cache_path=settings.data_cache_path,
        use_cache=True,
        write_cache_after_hf=True,
    )

    print("--- done ---")
    print(f"source={meta.source!r} revision={meta.dataset_revision!r}")
    print(f"raw_row_count={meta.raw_row_count} normalized={meta.normalized_row_count} dropped={meta.dropped_row_count}")
    print(f"restaurants_in_memory={len(restaurants)}")
    if cache.is_file():
        print(f"parquet_bytes={cache.stat().st_size}")


if __name__ == "__main__":
    main()
