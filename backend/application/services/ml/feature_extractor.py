import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from config.settings import settings

FEATURE_NAMES = [
    "session_days", "total_sessions", "total_time_minutes",
    "exercise_attempts", "passed_exercises", "error_rate",
    "forum_interactions", "content_views",
]


def _compute_error_rate(attempted: int, passed: int) -> float:
    if attempted <= 0:
        return 0.0
    rate = 1.0 - (passed / attempted)
    return max(0.0, min(1.0, rate))


class FeatureExtractor:
    """Extracts ML feature vectors from real MongoDB + PostgreSQL data.
    Falls back to synthetic data when no real data exists."""

    def __init__(self):
        self._mongo_client: Optional[MongoClient] = None
        self._mongo_db = None
        self._postgres_conn = None

    def _get_mongo(self):
        if self._mongo_db is None:
            self._mongo_client = MongoClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
            )
            self._mongo_db = self._mongo_client[settings.mongodb_db]
        return self._mongo_db

    def get_student_features(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Extract full feature set for a student from real data.
        Returns same dict format as synthetic_dataset.extract_for_student()."""
        db = self._get_mongo()

        # 1. Try weekly_student_metrics (up to 16 weeks, need at least 4)
        weekly = list(
            db.weekly_student_metrics.find({"user_id": student_id})
            .sort("week_start", -1)
            .limit(16)
        )
        if len(weekly) >= 4:
            return self._build_from_weekly(weekly)

        # 2. No real data — return None (caller falls back to synthetic)
        return None

    def get_features_batch(
        self, student_ids: List[int]
    ) -> Dict[int, Optional[Dict[str, Any]]]:
        """Extract features for multiple students in batch."""
        db = self._get_mongo()
        result = {}

        # Batch query all weekly data
        cursor = db.weekly_student_metrics.find(
            {"user_id": {"$in": student_ids}},
        ).sort("week_start", -1)

        # Group by user_id
        user_weekly: Dict[int, list] = {}
        for doc in cursor:
            uid = doc["user_id"]
            if uid not in user_weekly:
                user_weekly[uid] = []
            if len(user_weekly[uid]) < 16:
                user_weekly[uid].append(doc)

        for sid in student_ids:
            weekly = user_weekly.get(sid, [])
            if len(weekly) >= 4:
                result[sid] = self._build_from_weekly(weekly)
            else:
                result[sid] = None

        return result

    def _build_from_weekly(self, weekly: List[Dict]) -> Dict[str, Any]:
        """Build ML feature dict from weekly_student_metrics documents."""
        weekly.sort(key=lambda d: d["week_start"])

        def get_val(doc, field):
            """Get value from document, handling field name differences."""
            return float(doc.get(field, 0))

        def weekly_row(doc):
            """Map a MongoDB weekly doc to the 8 FEATURE_NAMES values."""
            attempted = get_val(doc, "exercises_attempted")
            passed = get_val(doc, "exercises_passed")
            return [
                get_val(doc, "session_days"),
                get_val(doc, "total_sessions"),
                get_val(doc, "total_time_minutes"),
                attempted,
                passed,
                _compute_error_rate(int(attempted), int(passed)),
                0.0,  # forum_interactions — not tracked in seed
                0.0,  # content_views — computed separately below
            ]

        # Compute content_views from behavioral_events per week range
        db = self._get_mongo()
        uid = weekly[0]["user_id"]
        for w in weekly:
            ws = w["week_start"]
            we = w.get("week_end", ws + timedelta(days=7))
            cv_count = db.behavioral_events.count_documents({
                "user_id": uid,
                "action": "view_content",
                "timestamp": {"$gte": ws, "$lt": we},
            })
            # Index 7 is content_views in FEATURE_NAMES
            w["_content_views"] = float(cv_count)

        window = weekly[-4:]  # Last 4 weeks
        all_weeks = weekly  # All available weeks for clustering

        # --- 32-dim feature vector (engagement, performance) ---
        flattened = []
        for w in window:
            row = weekly_row(w)
            # Override content_views with counted value
            row[7] = float(w.get("_content_views", 0))
            flattened.extend(row)
        eng_feat = np.array(flattened, dtype=np.float64)
        perf_feat = np.array(flattened, dtype=np.float64)

        # --- 8-dim mean features (dropout, frustration) ---
        means = []
        for i in range(8):
            vals = []
            for w in window:
                row = weekly_row(w)
                row[7] = float(w.get("_content_views", 0))
                vals.append(row[i])
            means.append(np.mean(vals))
        drop_feat = np.array(means, dtype=np.float64)
        fr_feat = np.array(means, dtype=np.float64)

        # --- 8-dim all-time mean (clustering) ---
        all_means = []
        for i in range(8):
            vals = []
            for w in all_weeks:
                row = weekly_row(w)
                row[7] = float(w.get("_content_views", 0))
                vals.append(row[i])
            all_means.append(np.mean(vals))
        cluster_feat = np.array(all_means, dtype=np.float64)

        # --- 32-dim delta features (anomaly) ---
        recent = all_weeks[-5:] if len(all_weeks) >= 5 else all_weeks
        if len(recent) >= 2:
            deltas = []
            for i in range(1, len(recent)):
                prev_row = weekly_row(recent[i - 1])
                prev_row[7] = float(recent[i - 1].get("_content_views", 0))
                curr_row = weekly_row(recent[i])
                curr_row[7] = float(recent[i].get("_content_views", 0))
                delta = [curr_row[j] - prev_row[j] for j in range(8)]
                deltas.extend(delta)
            # Pad or truncate to 32
            if len(deltas) < 32:
                deltas.extend([0.0] * (32 - len(deltas)))
            else:
                deltas = deltas[:32]
            anomaly_feat = np.array(deltas, dtype=np.float64)
        else:
            anomaly_feat = None

        return {
            "engagement": eng_feat,
            "performance": perf_feat,
            "dropout": drop_feat,
            "frustration": fr_feat,
            "clustering": cluster_feat,
            "anomaly": anomaly_feat,
        }

    def close(self):
        if self._mongo_client:
            self._mongo_client.close()
            self._mongo_client = None
            self._mongo_db = None
