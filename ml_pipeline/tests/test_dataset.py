import pytest
import pandas as pd
import numpy as np

from ml_pipeline.src.dataset import generate_dataset, get_dataset_stats


class TestDatasetGeneration:
    def test_shape(self, dataset):
        assert len(dataset) == 200 * 6
        assert dataset["student_id"].nunique() == 200
        assert dataset["week"].max() == 6

    def test_columns(self, dataset):
        expected = [
            "student_id", "week", "archetype",
            "session_days", "total_sessions", "total_time_minutes",
            "exercise_attempts", "passed_exercises", "error_rate",
            "forum_interactions", "content_views",
            "engagement_score", "frustration_score", "performance_score",
            "dropout_prob", "dropout",
        ]
        for col in expected:
            assert col in dataset.columns, f"Missing column: {col}"

    def test_archetypes(self, dataset):
        assert set(dataset["archetype"].unique()) == {"high", "medium", "low", "burnout"}

    def test_stats(self, dataset):
        stats = get_dataset_stats(dataset)
        assert stats["n_students"] == 200
        assert stats["n_weeks"] == 6
        assert stats["n_rows"] == 1200
