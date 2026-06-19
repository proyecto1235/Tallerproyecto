import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MLOrchestrator:
    def __init__(self):
        from .engagement_predictor import EngagementPredictor
        from .performance_predictor import PerformancePredictor
        from .dropout_predictor import DropoutPredictor
        from .frustration_predictor import FrustrationPredictor
        from .clustering import LearningClustering
        from .anomaly_detector import AnomalyDetector
        from .recommender import Recommender
        from .feature_extractor import FeatureExtractor
        self.engagement = EngagementPredictor()
        self.performance = PerformancePredictor()
        self.dropout = DropoutPredictor()
        self.frustration = FrustrationPredictor()
        self.clustering = LearningClustering()
        self.anomaly = AnomalyDetector()
        self.recommender = Recommender()
        self._extractor = FeatureExtractor()
        self._synthetic_df = None
        self._prediction_cache: Dict[int, Dict[str, Any]] = {}

        models_loaded = all(m.load() for m in [
            self.engagement, self.performance, self.dropout, self.frustration,
        ])
        if not models_loaded or not self.clustering._is_trained or not self.anomaly._is_trained:
            logger.warning("Algunos modelos no encontrados. Ejecute ml_pipeline/run_all.py primero.")

        logger.info("Usando datos reales de MongoDB para predicciones (fallback: synthetic dataset)")

    def reload_models(self) -> Dict[str, bool]:
        status = {}
        for name, predictor in [
            ("engagement", self.engagement),
            ("performance", self.performance),
            ("dropout", self.dropout),
            ("frustration", self.frustration),
        ]:
            loaded = predictor.load()
            status[name] = loaded
            logger.info(f"Modelo recargado {name}: {'OK' if loaded else 'FAILED'}")

        status["clustering"] = self.clustering._load()
        status["anomaly"] = self.anomaly._load()
        return status

    def train_all(self) -> Dict[str, Any]:
        return {
            "success": False,
            "message": (
                "Model training has been moved to ml_pipeline. "
                "Execute ml_pipeline/run_all.py and then call POST /api/ml/reload-models."
            ),
        }

    def _get_synthetic_features(self, student_id: int) -> Optional[Dict[str, Any]]:
        from .synthetic_dataset import generate_dataset, extract_for_student
        if self._synthetic_df is None:
            self._synthetic_df = generate_dataset()
            logger.info(f"Fallback synthetic dataset: {len(self._synthetic_df)} rows, "
                  f"{self._synthetic_df['student_id'].nunique()} students")
        student_df = self._synthetic_df[self._synthetic_df["student_id"] == student_id]
        if len(student_df) == 0:
            return None
        return extract_for_student(student_df)

    def _predict_from_features(
        self, student_id: int, feats: Optional[Dict]
    ) -> Dict[str, Any]:
        if feats is None:
            return self._default_prediction(student_id)

        has_history = feats["engagement"] is not None

        eng_feat = feats["engagement"]
        perf_feat = feats["performance"]
        drop_feat = feats["dropout"]
        fr_feat = feats["frustration"]
        cluster_feat = feats["clustering"]
        anomaly_deltas = feats["anomaly"]

        if not has_history:
            eng_feat = perf_feat = drop_feat = fr_feat = None

        engagement_pred = self.engagement.predict(eng_feat) if eng_feat is not None else 0.5
        performance_pred = self.performance.predict(perf_feat) if perf_feat is not None else 0.5
        dropout_prob = self.dropout.predict_proba(drop_feat) if drop_feat is not None else 0.5
        dropout_class = self.dropout.predict(drop_feat) if drop_feat is not None else 0
        frustration_class = self.frustration.predict(fr_feat) if fr_feat is not None else 0
        frustration_proba = self.frustration.predict_proba(fr_feat) if fr_feat is not None else [0.5, 0.3, 0.2]

        cluster_result = self.clustering.predict(cluster_feat) if cluster_feat is not None else {"cluster_name": "unknown", "cluster_id": -1}

        anomaly_result = self.anomaly.predict(anomaly_deltas) if anomaly_deltas is not None else {"is_anomaly": False, "anomaly_score": 0.0, "risk": "unknown"}

        recommendations = self.recommender.generate_student_recommendations(
            engagement=engagement_pred,
            performance=performance_pred,
            dropout_prob=dropout_prob,
            frustration=frustration_class,
            cluster_name=cluster_result.get("cluster_name"),
            anomaly=anomaly_result,
        )

        frustration_labels = {0: "baja", 1: "media", 2: "alta"}

        return {
            "student_id": student_id,
            "predictions": {
                "engagement_projected": {
                    "value": round(engagement_pred, 4),
                    "label": "alto" if engagement_pred > 0.7 else ("medio" if engagement_pred > 0.4 else "bajo"),
                },
                "performance_projected": {
                    "value": round(performance_pred, 4),
                    "label": "excelente" if performance_pred > 0.8 else ("bueno" if performance_pred > 0.6 else ("promedio" if performance_pred > 0.4 else "bajo")),
                },
                "frustration_projected": {
                    "class": frustration_class,
                    "label": frustration_labels.get(frustration_class, "desconocido"),
                    "probabilities": frustration_proba,
                },
                "dropout_risk": {
                    "probability": round(dropout_prob, 4),
                    "class": int(dropout_class),
                    "label": "alto" if dropout_prob > 0.6 else ("medio" if dropout_prob > 0.3 else "bajo"),
                },
            },
            "cluster": cluster_result,
            "anomaly": anomaly_result,
            "recommendations": recommendations,
            "has_historical_data": has_history,
        }

    def _default_prediction(self, student_id: int) -> Dict[str, Any]:
        return {
            "student_id": student_id,
            "predictions": {
                "engagement_projected": {"value": 0.5, "label": "medio"},
                "performance_projected": {"value": 0.5, "label": "promedio"},
                "frustration_projected": {"class": 0, "label": "baja", "probabilities": [0.5, 0.3, 0.2]},
                "dropout_risk": {"probability": 0.5, "class": 0, "label": "medio"},
            },
            "cluster": {"cluster_name": "unknown", "cluster_id": -1},
            "anomaly": {"is_anomaly": False, "anomaly_score": 0.0, "risk": "unknown"},
            "recommendations": [],
            "has_historical_data": False,
        }

    def predict_student(
        self, student_id: int, profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        if student_id in self._prediction_cache:
            return self._prediction_cache[student_id]

        # Try real features from MongoDB first
        feats = self._extractor.get_student_features(student_id)

        # Fallback to synthetic dataset
        if feats is None:
            feats = self._get_synthetic_features(student_id)

        if feats is None:
            result = self._default_prediction(student_id)
        else:
            result = self._predict_from_features(student_id, feats)
        self._prediction_cache[student_id] = result
        return result

    def predict_batch(self, student_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        import numpy as np
        if len(student_ids) == 0:
            return {}

        uncached = [sid for sid in student_ids if sid not in self._prediction_cache]
        if not uncached:
            return {sid: self._prediction_cache[sid] for sid in student_ids}

        # Batch extract real features from MongoDB
        feats_map = self._extractor.get_features_batch(uncached)

        # Fallback to synthetic for those without real data
        for sid in uncached:
            if feats_map.get(sid) is None:
                syn_feats = self._get_synthetic_features(sid)
                if syn_feats is not None:
                    feats_map[sid] = syn_feats

        # Extract all features
        cached_now = {}
        eng_list, perf_list, drop_list, fr_list = [], [], [], []
        eng_sids, perf_sids, drop_sids, fr_sids = [], [], [], []
        cluster_list, anomaly_list = [], []
        cluster_sids, anomaly_sids = [], []

        for sid in uncached:
            feats = feats_map.get(sid)
            if feats is None:
                cached_now[sid] = self._default_prediction(sid)
                continue

            has_history = feats["engagement"] is not None
            if has_history:
                eng_list.append(feats["engagement"]); eng_sids.append(sid)
                perf_list.append(feats["performance"]); perf_sids.append(sid)
                drop_list.append(feats["dropout"]); drop_sids.append(sid)
                fr_list.append(feats["frustration"]); fr_sids.append(sid)

            if feats["clustering"] is not None:
                cluster_list.append(feats["clustering"]); cluster_sids.append(sid)
            if feats["anomaly"] is not None:
                anomaly_list.append(feats["anomaly"]); anomaly_sids.append(sid)

        # Batch predictions via numpy
        def _pred_map(sids, vals, default=None):
            return dict(zip(sids, vals)) if default is None else {s: v for s, v in zip(sids, vals)}

        # Engagement (regressor)
        if eng_list:
            X_eng = np.stack(eng_list, axis=0)
            eng_preds = self.engagement.predict_batch(X_eng)
            eng_map = _pred_map(eng_sids, eng_preds)
        else:
            eng_map = {}

        # Performance (regressor)
        if perf_list:
            X_perf = np.stack(perf_list, axis=0)
            perf_preds = self.performance.predict_batch(X_perf)
            perf_map = _pred_map(perf_sids, perf_preds)
        else:
            perf_map = {}

        # Dropout (classifier)
        if drop_list:
            X_drop = np.stack(drop_list, axis=0)
            drop_preds = self.dropout.predict_batch(X_drop)
            drop_probas = self.dropout.predict_proba_batch(X_drop)
            drop_map = {s: (int(c), float(p)) for s, c, p in zip(drop_sids, drop_preds, drop_probas[:, 1])}
        else:
            drop_map = {}

        # Frustration (classifier)
        if fr_list:
            X_fr = np.stack(fr_list, axis=0)
            fr_preds = self.frustration.predict_batch(X_fr)
            fr_probas = self.frustration.predict_proba_batch(X_fr)
            fr_map = {s: (int(c), p.tolist()) for s, c, p in zip(fr_sids, fr_preds, fr_probas)}
        else:
            fr_map = {}

        # Clustering
        if cluster_list:
            X_cluster = np.stack(cluster_list, axis=0)
            cluster_batch = self.clustering.batch_predict(X_cluster)
            cluster_map = {s: r for s, r in zip(cluster_sids, cluster_batch)}
        else:
            cluster_map = {}

        # Anomaly
        if anomaly_list:
            X_anomaly = np.stack(anomaly_list, axis=0)
            anomaly_batch = self.anomaly.batch_predict(X_anomaly)
            anomaly_map = {s: r for s, r in zip(anomaly_sids, anomaly_batch)}
        else:
            anomaly_map = {}

        frustration_labels = {0: "baja", 1: "media", 2: "alta"}

        # Build results from batch outputs
        for sid in uncached:
            eng_v = eng_map.get(sid, 0.5)
            perf_v = perf_map.get(sid, 0.5)
            drop_cls, drop_prob = drop_map.get(sid, (0, 0.5))
            fr_cls, fr_proba = fr_map.get(sid, (0, [0.5, 0.3, 0.2]))
            cluster_res = cluster_map.get(sid, {"cluster_name": "unknown", "cluster_id": -1})
            anomaly_res = anomaly_map.get(sid, {"is_anomaly": False, "anomaly_score": 0.0, "risk": "unknown"})

            recommendations = self.recommender.generate_student_recommendations(
                engagement=eng_v, performance=perf_v, dropout_prob=drop_prob,
                frustration=fr_cls, cluster_name=cluster_res.get("cluster_name"),
                anomaly=anomaly_res,
            )

            cached_now[sid] = {
                "student_id": sid,
                "predictions": {
                    "engagement_projected": {
                        "value": round(eng_v, 4),
                        "label": "alto" if eng_v > 0.7 else ("medio" if eng_v > 0.4 else "bajo"),
                    },
                    "performance_projected": {
                        "value": round(perf_v, 4),
                        "label": "excelente" if perf_v > 0.8 else ("bueno" if perf_v > 0.6 else ("promedio" if perf_v > 0.4 else "bajo")),
                    },
                    "frustration_projected": {
                        "class": fr_cls, "label": frustration_labels.get(fr_cls, "desconocido"),
                        "probabilities": fr_proba,
                    },
                    "dropout_risk": {
                        "probability": round(drop_prob, 4), "class": drop_cls,
                        "label": "alto" if drop_prob > 0.6 else ("medio" if drop_prob > 0.3 else "bajo"),
                    },
                },
                "cluster": cluster_res,
                "anomaly": anomaly_res,
                "recommendations": recommendations,
                "has_historical_data": sid in eng_map,
            }

        self._prediction_cache.update(cached_now)
        return {sid: self._prediction_cache[sid] for sid in student_ids}

    def clear_cache(self):
        self._prediction_cache.clear()

    def cache_status(self) -> Dict[str, Any]:
        return {
            "cached": len(self._prediction_cache),
            "student_ids": sorted(self._prediction_cache.keys()),
        }

    def predict_class(
        self, profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        import numpy as np
        students = []
        for p in profiles:
            sid = p.get("user_id", p.get("student_id"))
            result = self.predict_student(sid, p)
            students.append(result)

        cluster_summary = {}
        for s in students:
            cname = s.get("cluster", {}).get("cluster_name", "unknown")
            if cname not in cluster_summary:
                cluster_summary[cname] = 0
            cluster_summary[cname] += 1

        at_risk = [s for s in students if s["predictions"]["dropout_risk"]["label"] == "alto"]
        high_frustration = [s for s in students if s["predictions"]["frustration_projected"]["class"] >= 2]
        avg_eng = np.mean([s["predictions"]["engagement_projected"]["value"] for s in students]) if students else 0
        avg_perf = np.mean([s["predictions"]["performance_projected"]["value"] for s in students]) if students else 0

        cluster_list = [
            {"cluster_name": k, "count": v}
            for k, v in sorted(cluster_summary.items(), key=lambda x: -x[1])
        ]

        insights = self.recommender.generate_teacher_insights(
            cluster_summary=cluster_list,
            at_risk_count=len(at_risk),
            high_frustration_count=len(high_frustration),
            avg_engagement=avg_eng,
            avg_performance=avg_perf,
        )

        return {
            "total_students": len(students),
            "cluster_distribution": cluster_list,
            "at_risk": {
                "count": len(at_risk),
                "students": [s["student_id"] for s in at_risk],
            },
            "high_frustration": {
                "count": len(high_frustration),
                "students": [s["student_id"] for s in high_frustration],
            },
            "averages": {
                "engagement": round(float(avg_eng), 4),
                "performance": round(float(avg_perf), 4),
            },
            "insights": insights,
            "students": students,
        }

    def get_feature_importances(self) -> Dict[str, List]:
        return {
            "engagement": self.engagement.get_feature_importances(),
            "performance": self.performance.get_feature_importances(),
            "dropout": self.dropout.get_feature_importances(),
            "frustration": self.frustration.get_feature_importances(),
        }

    def get_clustering_pca(self) -> Dict:
        import numpy as np
        if self._synthetic_df is None:
            self._synthetic_df = generate_dataset()
        X = np.array([
            extract_features_for_clustering(self._synthetic_df, sid)
            for sid in self._synthetic_df["student_id"].unique()
            if extract_features_for_clustering(self._synthetic_df, sid) is not None
        ])
        return self.clustering.get_pca_projection(X)
