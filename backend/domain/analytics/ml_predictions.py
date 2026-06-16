from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class MLPrediction:
    student_id: int
    week_number: int
    predicted_engagement: float = 0.0
    predicted_performance: float = 0.0
    predicted_dropout_prob: float = 0.0
    predicted_frustration_level: int = 0
    cluster_id: int = -1
    cluster_name: str = "unknown"
    anomaly_score: float = 0.0
    is_anomaly: bool = False
    feature_importances: Optional[Dict[str, List[Dict[str, Any]]]] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "week_number": self.week_number,
            "predicted_engagement": round(self.predicted_engagement, 4),
            "predicted_performance": round(self.predicted_performance, 4),
            "predicted_dropout_prob": round(self.predicted_dropout_prob, 4),
            "predicted_frustration_level": self.predicted_frustration_level,
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name,
            "anomaly_score": round(self.anomaly_score, 4),
            "is_anomaly": self.is_anomaly,
            "feature_importances": self.feature_importances,
            "created_at": (self.created_at or datetime.now(timezone.utc)).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MLPrediction":
        return cls(
            student_id=data.get("student_id", 0),
            week_number=data.get("week_number", 0),
            predicted_engagement=float(data.get("predicted_engagement", 0)),
            predicted_performance=float(data.get("predicted_performance", 0)),
            predicted_dropout_prob=float(data.get("predicted_dropout_prob", 0)),
            predicted_frustration_level=data.get("predicted_frustration_level", 0),
            cluster_id=data.get("cluster_id", -1),
            cluster_name=data.get("cluster_name", "unknown"),
            anomaly_score=float(data.get("anomaly_score", 0)),
            is_anomaly=data.get("is_anomaly", False),
            feature_importances=data.get("feature_importances"),
            created_at=data.get("created_at"),
        )
