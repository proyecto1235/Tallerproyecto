"""Model export and import utilities.

All files are saved to the shared `models/` directory at the project root.
Convention: {name}_model.pkl, {name}_scaler.pkl, {name}_features.json
"""

import json
import os
import joblib
from typing import Any, List, Optional

MODEL_DIR = "models"


def _ensure_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def _path(name: str, suffix: str) -> str:
    return os.path.join(MODEL_DIR, f"{name}_{suffix}")


def save_model(model: Any, scaler: Any, features: List[str], name: str) -> None:
    _ensure_dir()
    joblib.dump(model, _path(name, "model.pkl"))
    joblib.dump(scaler, _path(name, "scaler.pkl"))
    with open(_path(name, "features.json"), "w") as f:
        json.dump(features, f)


def load_model(name: str) -> Optional[Any]:
    path = _path(name, "model.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None


def load_scaler(name: str) -> Optional[Any]:
    path = _path(name, "scaler.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None


def load_features(name: str) -> Optional[List[str]]:
    path = _path(name, "features.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def model_exists(name: str) -> bool:
    return os.path.exists(_path(name, "model.pkl"))
