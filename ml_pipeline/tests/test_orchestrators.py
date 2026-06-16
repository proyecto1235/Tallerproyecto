"""Tests for the top-level orchestration scripts (01-04 and run_all)."""

import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch, call, mock_open

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_script(name: str):
    """Import an orchestrator script as a module."""
    import importlib
    mod = importlib.import_module(f"ml_pipeline.{name}")
    importlib.reload(mod)
    return mod


# ---------------------------------------------------------------------------
# 01_generate_dataset.py
# ---------------------------------------------------------------------------

class TestGenerateDataset:

    def test_main_success(self):
        mod = _import_script("01_generate_dataset")
        mock_df = pd.DataFrame({"student_id": [1]})
        mock_stats = {
            "n_rows": 1, "n_students": 1, "n_weeks": 1,
            "n_dropouts": 0, "dropout_rate": 0.0, "archetype_distribution": {},
        }

        with patch.object(mod, "generate_dataset", return_value=mock_df) as mock_gen:
            with patch.object(mod, "get_dataset_stats", return_value=mock_stats) as mock_stats_fn:
                with patch.object(mod.os, "makedirs") as mock_mkdir:
                    with patch.object(mod.os.path, "getsize", return_value=1000):
                        result = mod.main()

        assert result == 0
        mock_gen.assert_called_once_with(n_students=10_000, n_weeks=16)
        mock_stats_fn.assert_called_once_with(mock_df)

    _STATS = {
        "n_rows": 100, "n_students": 10, "n_weeks": 6,
        "n_dropouts": 1, "dropout_rate": 0.1, "archetype_distribution": {},
    }

    def test_main_creates_data_dir(self):
        mod = _import_script("01_generate_dataset")
        mock_df = pd.DataFrame({"x": [1]})

        with patch.object(mod, "generate_dataset", return_value=mock_df):
            with patch.object(mod, "get_dataset_stats", return_value=self._STATS):
                with patch.object(mod.os, "makedirs") as mock_mkdir:
                    with patch.object(mod.os.path, "getsize", return_value=100):
                        mod.main()

        import os as os_mod
        mock_mkdir.assert_called_once_with("data", exist_ok=True)

    def test_main_saves_both_formats(self):
        mod = _import_script("01_generate_dataset")
        mock_df = pd.DataFrame({"student_id": [1, 2], "value": [0.5, 0.8]})

        with patch.object(mod, "generate_dataset", return_value=mock_df):
            with patch.object(mod, "get_dataset_stats", return_value=self._STATS):
                with patch.object(mod.os, "makedirs"):
                    with patch.object(mod.os.path, "getsize", return_value=200):
                        with patch.object(mock_df, "to_parquet") as mock_pq:
                            with patch.object(mock_df, "to_csv") as mock_csv:
                                mod.main()

        import os as os_mod
        expected_pq = os_mod.path.join("data", "robolearn_dataset.parquet")
        expected_csv = os_mod.path.join("data", "robolearn_dataset.csv")
        mock_pq.assert_called_once_with(expected_pq, index=False)
        mock_csv.assert_called_once_with(expected_csv, index=False)


# ---------------------------------------------------------------------------
# 02_train_models.py
# ---------------------------------------------------------------------------

class TestTrainModels:

    def _mock_window(self, n_train=100, n_test=30):
        X_train = pd.DataFrame(np.random.randn(n_train, 10))
        y_train = pd.Series(np.random.randn(n_train))
        X_test = pd.DataFrame(np.random.randn(n_test, 10))
        y_test = pd.Series(np.random.randn(n_test))
        return {
            "engagement": {"train": (X_train, y_train), "test": (X_test, y_test)},
            "performance": {"train": (X_train, y_train), "test": (X_test, y_test)},
            "dropout": {"train": (X_train, (y_train > 0).astype(int)), "test": (X_test, (y_test > 0).astype(int))},
            "frustration": {"train": (X_train, (y_train > 0).astype(int)), "test": (X_test, (y_test > 0).astype(int))},
        }

    def test_main_trains_all_models(self):
        mod = _import_script("02_train_models")
        windows = self._mock_window()
        mock_model = MagicMock()
        mock_scaler = MagicMock()

        with patch.object(mod.pd, "read_parquet", return_value=pd.DataFrame({"student_id": [1]})):
            with patch.object(mod, "build_sliding_windows", return_value=windows):
                with patch.object(mod, "train_engagement", return_value=(mock_model, mock_scaler)) as eng:
                    with patch.object(mod, "train_performance", return_value=(mock_model, mock_scaler)) as perf:
                        with patch.object(mod, "train_dropout", return_value=(mock_model, mock_scaler)) as drop:
                            with patch.object(mod, "train_frustration", return_value=(mock_model, mock_scaler)) as frust:
                                with patch.object(mod, "save_model") as save:
                                    result = mod.main()

        assert result == 0
        eng.assert_called_once()
        perf.assert_called_once()
        drop.assert_called_once()
        frust.assert_called_once()
        assert save.call_count == 4

    def test_main_returns_zero(self):
        mod = _import_script("02_train_models")
        windows = self._mock_window()

        with patch.object(mod.pd, "read_parquet", return_value=pd.DataFrame({"student_id": [1]})):
            with patch.object(mod, "build_sliding_windows", return_value=windows):
                with patch.object(mod, "train_engagement", return_value=(MagicMock(), MagicMock())):
                    with patch.object(mod, "train_performance", return_value=(MagicMock(), MagicMock())):
                        with patch.object(mod, "train_dropout", return_value=(MagicMock(), MagicMock())):
                            with patch.object(mod, "train_frustration", return_value=(MagicMock(), MagicMock())):
                                with patch.object(mod, "save_model"):
                                    rc = mod.main()

        assert rc == 0


# ---------------------------------------------------------------------------
# 03_evaluate_models.py
# ---------------------------------------------------------------------------

class TestEvaluateModels:

    def _mock_window(self):
        X_test = pd.DataFrame(np.random.randn(30, 10))
        y_test = pd.Series(np.random.randn(30))
        return {
            "engagement": {"train": (None, None), "test": (X_test, y_test)},
            "performance": {"train": (None, None), "test": (X_test, y_test)},
            "dropout": {"train": (None, None), "test": (X_test, (y_test > 0).astype(int))},
            "frustration": {"train": (None, None), "test": (X_test, (y_test > 0).astype(int))},
        }

    def test_main_evaluates_all_models(self):
        mod = _import_script("03_evaluate_models")
        windows = self._mock_window()
        mock_model = MagicMock()
        mock_scaler = MagicMock()
        mock_model.predict.return_value = np.array([0.5])
        mock_model.predict_proba.return_value = np.array([[0.5, 0.5]])

        with patch.object(mod.pd, "read_parquet", return_value=pd.DataFrame({"student_id": [1]})):
            with patch.object(mod, "build_sliding_windows", return_value=windows):
                with patch.object(mod, "load_model", return_value=mock_model):
                    with patch.object(mod, "load_scaler", return_value=mock_scaler):
                        with patch.object(mod, "evaluate_regression",
                                          return_value={"r2": 0.85, "mae": 0.1}) as eval_reg:
                            with patch.object(mod, "evaluate_binary_classification",
                                              return_value={"roc_auc": 0.9, "accuracy": 0.8}) as eval_bin:
                                with patch.object(mod, "evaluate_multiclass_classification",
                                                  return_value={"accuracy": 0.8}) as eval_mc:
                                    with patch.object(mod, "save_metrics_json",
                                                      return_value="reports/metrics.json") as save_json:
                                        with patch.object(mod, "save_training_summary",
                                                          return_value="reports/summary.md") as save_md:
                                            result = mod.main()

        assert result == 0
        assert eval_reg.call_count == 2
        eval_bin.assert_called_once()
        eval_mc.assert_called_once()
        save_json.assert_called_once()
        save_md.assert_called_once()

    def test_main_handles_no_test_data(self):
        mod = _import_script("03_evaluate_models")
        empty_windows = {
            k: {"train": (None, None), "test": (pd.DataFrame(), pd.Series(dtype=float))}
            for k in ["engagement", "performance", "dropout", "frustration"]
        }

        with patch.object(mod.pd, "read_parquet", return_value=pd.DataFrame()):
            with patch.object(mod, "build_sliding_windows", return_value=empty_windows):
                with patch.object(mod, "load_model", return_value=MagicMock()):
                    with patch.object(mod, "load_scaler", return_value=MagicMock()):
                        with patch.object(mod, "save_metrics_json", return_value="json"):
                            with patch.object(mod, "save_training_summary", return_value="md"):
                                result = mod.main()

        assert result == 0


# ---------------------------------------------------------------------------
# 04_train_unsupervised.py
# ---------------------------------------------------------------------------

class TestTrainUnsupervised:

    def test_main_trains_clustering_and_anomaly(self):
        mod = _import_script("04_train_unsupervised")
        df = pd.DataFrame({"student_id": [1, 2], "value": [0.1, 0.9]})
        mock_scaler = MagicMock()
        mock_scaler.fit_transform.side_effect = lambda x: x
        mock_kmeans = MagicMock()
        mock_pca = MagicMock()
        mock_iso = MagicMock()

        with patch.object(mod.pd, "read_parquet", return_value=df):
            with patch.object(mod, "extract_for_clustering", return_value=np.array([0.5, 0.5])):
                with patch.object(mod, "extract_for_anomaly", return_value=np.array([0.1, 0.2])):
                    with patch.object(mod, "StandardScaler", return_value=mock_scaler):
                        with patch.object(mod, "KMeans", return_value=mock_kmeans):
                            with patch.object(mod, "PCA", return_value=mock_pca):
                                with patch.object(mod, "IsolationForest", return_value=mock_iso):
                                    with patch.object(mod, "evaluate_clustering",
                                                      return_value={"silhouette_score": 0.5,
                                                                    "cluster_distribution": {}}):
                                        with patch.object(mod, "evaluate_anomaly",
                                                          return_value={"n_anomalies": 1, "anomaly_rate": 0.5}):
                                            with patch.object(mod.joblib, "dump"):
                                                with patch.object(mod.os, "makedirs"):
                                                    with patch("builtins.open", mock_open(read_data="{}")):
                                                        result = mod.main()

        assert result == 0
        mock_kmeans.fit.assert_called()
        mock_iso.fit.assert_called()
        mock_pca.fit.assert_called()

    def test_main_without_existing_metrics_json(self):
        mod = _import_script("04_train_unsupervised")
        df = pd.DataFrame({"student_id": [1], "value": [0.5]})
        mock_scaler = MagicMock()
        mock_scaler.fit_transform.side_effect = lambda x: x

        with patch.object(mod.pd, "read_parquet", return_value=df):
            with patch.object(mod, "extract_for_clustering", return_value=np.array([0.5])):
                with patch.object(mod, "extract_for_anomaly", return_value=np.array([0.1])):
                    with patch.object(mod, "StandardScaler", return_value=mock_scaler):
                        with patch.object(mod, "KMeans", return_value=MagicMock()):
                            with patch.object(mod, "PCA", return_value=MagicMock()):
                                with patch.object(mod, "IsolationForest", return_value=MagicMock()):
                                    with patch.object(mod, "evaluate_clustering",
                                                      return_value={"silhouette_score": 0.4,
                                                                    "cluster_distribution": {}}):
                                        with patch.object(mod, "evaluate_anomaly",
                                                          return_value={"n_anomalies": 0, "anomaly_rate": 0.0}):
                                            with patch.object(mod.joblib, "dump"):
                                                with patch.object(mod.os.path, "exists", return_value=False):
                                                    with patch.object(mod.os, "makedirs"):
                                                        with patch("builtins.open", mock_open(read_data="{}")):
                                                            result = mod.main()

        assert result == 0


# ---------------------------------------------------------------------------
# run_all.py
# ---------------------------------------------------------------------------

class TestRunAll:

    def test_main_runs_all_scripts(self):
        mod = _import_script("run_all")

        with patch.object(mod.subprocess, "run",
                          return_value=MagicMock(returncode=0)) as mock_run:
            with patch.object(mod.os.path, "exists", return_value=True):
                with patch.object(sys, "argv", ["run_all.py"]):
                    result = mod.main()

        assert result == 0
        assert mock_run.call_count == 4

    def test_main_skip_one_stage(self):
        mod = _import_script("run_all")

        with patch.object(mod.subprocess, "run",
                          return_value=MagicMock(returncode=0)) as mock_run:
            with patch.object(mod.os.path, "exists", return_value=True):
                with patch.object(sys, "argv", ["run_all.py", "--skip=03"]):
                    result = mod.main()

        assert result == 0
        assert mock_run.call_count == 3

    def test_main_only_one_stage(self):
        mod = _import_script("run_all")

        with patch.object(mod.subprocess, "run",
                          return_value=MagicMock(returncode=0)) as mock_run:
            with patch.object(mod.os.path, "exists", return_value=True):
                with patch.object(sys, "argv", ["run_all.py", "--only=02"]):
                    result = mod.main()

        assert result == 0
        assert mock_run.call_count == 1

    def test_main_aborts_on_failure(self):
        mod = _import_script("run_all")

        with patch.object(mod.subprocess, "run",
                          return_value=MagicMock(returncode=1)) as mock_run:
            with patch.object(mod.os.path, "exists", return_value=True):
                with patch.object(sys, "argv", ["run_all.py"]):
                    result = mod.main()

        assert result == 1
        mock_run.assert_called_once()

    def test_main_script_not_found(self):
        mod = _import_script("run_all")

        with patch.object(mod.os.path, "exists", return_value=False):
            with patch.object(sys, "argv", ["run_all.py"]):
                result = mod.main()

        assert result == 1

    def test_main_skip_and_only_flags(self):
        mod = _import_script("run_all")

        with patch.object(mod.subprocess, "run",
                          return_value=MagicMock(returncode=0)) as mock_run:
            with patch.object(mod.os.path, "exists", return_value=True):
                with patch.object(sys, "argv", ["run_all.py", "--skip=01", "--only=02"]):
                    result = mod.main()

        assert result == 0
        assert mock_run.call_count == 1
