import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np

from ml_pipeline.src.dataset import generate_dataset, get_dataset_stats


@pytest.fixture(scope="session")
def dataset() -> pd.DataFrame:
    return generate_dataset(n_students=200, n_weeks=6, seed=123)
