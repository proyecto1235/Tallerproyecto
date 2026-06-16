import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import joblib
import os
from typing import Dict, List, Any, Optional
from config.settings import settings

MODEL_DIR = settings.ml_model_dir

CLUSTER_LABELS = {
    0: {"name": "Principiante", "desc": "Estudiantes nuevos o con poca actividad semanal"},
    1: {"name": "Regular", "desc": "Estudiantes con actividad y rendimiento moderados"},
    2: {"name": "Avanzado", "desc": "Estudiantes con alto rendimiento y engagement sostenido"},
    3: {"name": "En Riesgo", "desc": "Estudiantes con baja actividad, alta frustración y posible abandono"},
}

FEATURE_NAMES = [
    "session_days", "total_sessions", "total_time_minutes",
    "exercise_attempts", "passed_exercises", "error_rate",
    "forum_interactions", "content_views",
]


class LearningClustering:
    def __init__(self, n_clusters: int = 4):
        self._model: Optional[KMeans] = None
        self._scaler: Optional[StandardScaler] = None
        self._pca: Optional[PCA] = None
        self._n_clusters = n_clusters
        self._label_map = CLUSTER_LABELS
        self._is_trained = False
        self._feature_names = FEATURE_NAMES
        os.makedirs(MODEL_DIR, exist_ok=True)
        self._load()

    def _path(self, name: str) -> str:
        return os.path.join(MODEL_DIR, name)

    def _load(self) -> bool:
        try:
            if os.path.exists(self._path("cluster_model.pkl")):
                self._model = joblib.load(self._path("cluster_model.pkl"))
            if os.path.exists(self._path("cluster_scaler.pkl")):
                self._scaler = joblib.load(self._path("cluster_scaler.pkl"))
            if os.path.exists(self._path("cluster_pca.pkl")):
                self._pca = joblib.load(self._path("cluster_pca.pkl"))
            if os.path.exists(self._path("cluster_trained.pkl")):
                self._is_trained = joblib.load(self._path("cluster_trained.pkl"))
            return self._is_trained
        except Exception:
            return False

    def _save(self):
        joblib.dump(self._model, self._path("cluster_model.pkl"))
        joblib.dump(self._scaler, self._path("cluster_scaler.pkl"))
        joblib.dump(self._pca, self._path("cluster_pca.pkl"))
        joblib.dump(self._is_trained, self._path("cluster_trained.pkl"))

    def train(self, X: np.ndarray) -> dict:
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._model = KMeans(
            n_clusters=self._n_clusters, random_state=42, n_init=10,
        )
        self._model.fit(X_scaled)

        self._pca = PCA(n_components=2, random_state=42)
        X_pca = self._pca.fit_transform(X_scaled)
        pca_variance = float(np.sum(self._pca.explained_variance_ratio_))

        labels = self._model.labels_
        sil = float(silhouette_score(X_scaled, labels))

        self._is_trained = True
        self._save()

        cluster_counts = {}
        for i in range(self._n_clusters):
            count = int(np.sum(labels == i))
            name = self._label_map.get(i, {}).get("name", f"Cluster {i}")
            cluster_counts[name] = count

        return {
            "silhouette_score": round(sil, 4),
            "pca_explained_variance": round(pca_variance, 4),
            "n_clusters": self._n_clusters,
            "cluster_distribution": cluster_counts,
            "n_samples": len(X),
        }

    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        if not self._is_trained:
            return {"cluster_id": -1, "cluster_name": "unknown"}
        X_scaled = self._scaler.transform(X.reshape(1, -1))
        label = int(self._model.predict(X_scaled)[0])
        info = self._label_map.get(label, {"name": f"Cluster {label}", "desc": ""})
        return {
            "cluster_id": label,
            "cluster_name": info["name"],
            "cluster_description": info["desc"],
        }

    def batch_predict(self, X: np.ndarray) -> List[Dict[str, Any]]:
        if not self._is_trained:
            return []
        X_scaled = self._scaler.transform(X)
        labels = self._model.predict(X_scaled)
        results = []
        for i, label in enumerate(labels):
            info = self._label_map.get(int(label), {"name": f"Cluster {int(label)}", "desc": ""})
            results.append({
                "index": i,
                "cluster_id": int(label),
                "cluster_name": info["name"],
                "cluster_description": info["desc"],
            })
        return results

    def get_pca_projection(self, X: np.ndarray) -> Dict[str, Any]:
        if self._pca is None:
            return {"pca1": [], "pca2": [], "labels": []}
        X_scaled = self._scaler.transform(X)
        X_pca = self._pca.transform(X_scaled)
        labels = self._model.predict(X_scaled)
        return {
            "pca1": [round(float(v), 4) for v in X_pca[:, 0]],
            "pca2": [round(float(v), 4) for v in X_pca[:, 1]],
            "labels": [int(l) for l in labels],
            "variance_ratio": [round(float(v), 4) for v in self._pca.explained_variance_ratio_],
        }

    def get_summary(self, X: np.ndarray) -> List[Dict[str, Any]]:
        batch = self.batch_predict(X)
        summary = {}
        for item in batch:
            cid = item["cluster_id"]
            if cid not in summary:
                summary[cid] = {
                    "cluster_id": cid,
                    "cluster_name": item["cluster_name"],
                    "description": item["cluster_description"],
                    "count": 0,
                }
            summary[cid]["count"] += 1
        return list(summary.values())
