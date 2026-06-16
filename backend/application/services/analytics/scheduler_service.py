from datetime import datetime, timezone
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from infrastructure.adapters.output.mongo.student_metrics_repository import StudentMetricsRepository
from infrastructure.adapters.output.mongo.weekly_metrics_repository import WeeklyMetricsRepository
from infrastructure.adapters.output.mongo.ml_predictions_repository import MLPredictionsRepository
from domain.analytics.weekly_metrics import WeeklyStudentMetrics
from domain.analytics.ml_predictions import MLPrediction


class AnalyticsScheduler:
    def __init__(self, orchestrator=None):
        self._scheduler = AsyncIOScheduler()
        self._student_metrics_repo = StudentMetricsRepository()
        self._weekly_repo = WeeklyMetricsRepository()
        self._ml_repo = MLPredictionsRepository()
        self._orchestrator = orchestrator

    def start(self):
        if not self._scheduler.running:
            self._scheduler.add_job(
                self._generate_weekly_snapshot,
                CronTrigger(day_of_week="sun", hour=23, minute=59),
                id="weekly_snapshot",
                replace_existing=True,
                name="Weekly metrics snapshot + ML predictions",
            )
            self._scheduler.add_job(
                self._generate_daily_snapshot,
                CronTrigger(hour=23, minute=0),
                id="daily_snapshot",
                replace_existing=True,
                name="Daily metrics snapshot",
            )
            self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    async def _generate_weekly_snapshot(self):
        print("[AnalyticsScheduler] Generating weekly snapshot...")
        now = datetime.now(timezone.utc)
        week_number = now.isocalendar()[1]
        year = now.year

        all_metrics = await self._student_metrics_repo.get_all_metrics()
        if not all_metrics:
            print("[AnalyticsScheduler] No student metrics found.")
            return

        for sm in all_metrics:
            try:
                wm = WeeklyStudentMetrics(
                    student_id=sm.student_id,
                    week_number=week_number,
                    year=year,
                    avg_session_days=float(sm.session_days),
                    avg_total_sessions=float(sm.total_sessions),
                    avg_total_time_minutes=sm.total_time_minutes,
                    avg_exercise_attempts=float(sm.exercise_attempts),
                    avg_passed_exercises=float(sm.passed_exercises),
                    avg_error_rate=sm.error_rate,
                    avg_forum_interactions=float(sm.forum_interactions),
                    avg_content_views=float(sm.content_views),
                )
                await self._weekly_repo.save_snapshot(wm)

                if self._orchestrator:
                    try:
                        result = self._orchestrator.predict_student(sm.student_id)
                        preds = result.get("predictions", {})
                        cluster = result.get("cluster", {})
                        anomaly = result.get("anomaly", {})

                        mlp = MLPrediction(
                            student_id=sm.student_id,
                            week_number=week_number,
                            predicted_engagement=preds.get("engagement_projected", {}).get("value", 0.5),
                            predicted_performance=preds.get("performance_projected", {}).get("value", 0.5),
                            predicted_dropout_prob=preds.get("dropout_risk", {}).get("probability", 0),
                            predicted_frustration_level=preds.get("frustration_projected", {}).get("class", 0),
                            cluster_id=cluster.get("cluster_id", -1),
                            cluster_name=cluster.get("cluster_name", "unknown"),
                            anomaly_score=anomaly.get("anomaly_score", 0),
                            is_anomaly=anomaly.get("is_anomaly", False),
                            feature_importances=self._orchestrator.get_feature_importances(),
                        )
                        await self._ml_repo.save_predictions(mlp)
                    except Exception as e:
                        print(f"[AnalyticsScheduler] ML prediction error for student {sm.student_id}: {e}")
            except Exception as e:
                print(f"[AnalyticsScheduler] Error processing student {sm.student_id}: {e}")

        print(f"[AnalyticsScheduler] Weekly snapshot complete: {len(all_metrics)} students")

    async def _generate_daily_snapshot(self):
        print("[AnalyticsScheduler] Daily metrics check...")
        all_metrics = await self._student_metrics_repo.get_all_metrics()
        if all_metrics:
            print(f"[AnalyticsScheduler] {len(all_metrics)} active students tracked")

    async def trigger_weekly_now(self):
        await self._generate_weekly_snapshot()
