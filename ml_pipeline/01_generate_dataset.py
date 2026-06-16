#!/usr/bin/env python3
"""01_generate_dataset.py — Generate synthetic longitudinal dataset for RoboLearn.

Saves to:
  - data/robolearn_dataset.parquet (fast, compressed)
  - data/robolearn_dataset.csv    (human-readable)
"""

import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_pipeline.src.dataset import generate_dataset, get_dataset_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = "data"
PARQUET_PATH = os.path.join(DATA_DIR, "robolearn_dataset.parquet")
CSV_PATH = os.path.join(DATA_DIR, "robolearn_dataset.csv")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    logger.info("Generating longitudinal dataset (10,000 students x 16 weeks)...")
    df = generate_dataset(n_students=10_000, n_weeks=16)
    stats = get_dataset_stats(df)

    logger.info(f"Rows: {stats['n_rows']:,}")
    logger.info(f"Students: {stats['n_students']:,}")
    logger.info(f"Weeks: {stats['n_weeks']}")
    logger.info(f"Dropouts: {stats['n_dropouts']:,} ({stats['dropout_rate']*100:.1f}%)")
    logger.info(f"Archetypes: {stats['archetype_distribution']}")

    df.to_parquet(PARQUET_PATH, index=False)
    logger.info(f"Saved: {PARQUET_PATH} ({os.path.getsize(PARQUET_PATH) / 1e6:.1f} MB)")

    df.to_csv(CSV_PATH, index=False)
    logger.info(f"Saved: {CSV_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
