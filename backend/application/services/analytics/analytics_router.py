import asyncio
import numpy as np
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status

from application.services.ml.orchestrator import MLOrchestrator
from application.services.analytics.metrics_service import MetricsService
from infrastructure.adapters.output.mongo.weekly_metrics_repository import WeeklyMetricsRepository
from infrastructure.adapters.output.mongo.ml_predictions_repository import MLPredictionsRepository


analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

_metrics_service = MetricsService()
_weekly_repo = WeeklyMetricsRepository()
_ml_repo = MLPredictionsRepository()


def get_orchestrator() -> MLOrchestrator:
    from app.main import ml_orchestrator
    return ml_orchestrator


async def _require_auth(request: Request):
    from app.main import verify_token
    return await verify_token(request)


async def _require_teacher(request: Request):
    from app.main import verify_token
    from app.main import user_repository
    from domain.entities.user import UserRole
    token_data = await verify_token(request)
    user = await user_repository.get_by_id(token_data.user_id)
    if not user or user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires teacher privileges")
    return token_data


@analytics_router.get("/student/{student_id}")
async def get_student_analytics(
    student_id: int,
    token_data=Depends(_require_auth),
):
    """Full student analytics: metrics + predictions + history + recommendations.
    Teachers/admins can view any student. Students can only view their own data."""
    from domain.entities.user import UserRole
    from app.main import user_repository
    user = await user_repository.get_by_id(token_data.user_id)
    is_teacher = user and user.role in (UserRole.TEACHER, UserRole.ADMIN)
    if not is_teacher and token_data.user_id != student_id:
        raise HTTPException(status_code=403, detail="Only teachers can view other students' analytics")
    orch = get_orchestrator()
    predictions = await asyncio.to_thread(orch.predict_student, student_id)

    metrics = await _metrics_service.get_student_metrics(student_id)

    weekly_history = await _weekly_repo.get_student_history(student_id, limit=16)
    ml_history = await _ml_repo.get_history(student_id, limit=16)

    return {
        "success": True,
        "student_id": student_id,
        "metrics": metrics,
        "predictions": predictions.get("predictions", {}),
        "cluster": predictions.get("cluster", {}),
        "anomaly": predictions.get("anomaly", {}),
        "recommendations": predictions.get("recommendations", []),
        "weekly_history": [w.to_dict() for w in weekly_history],
        "predictions_history": [m.to_dict() for m in ml_history],
        "has_historical_data": predictions.get("has_historical_data", False),
    }


@analytics_router.get("/class/predictions")
async def get_class_predictions(
    days: int = 30,
    module_id: Optional[int] = None,
    token_data=Depends(_require_teacher),
):
    """Get predictions for all students in the teacher's classes"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        if module_id:
            cursor.execute("""
                SELECT DISTINCT e.student_id FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                WHERE m.teacher_id = %s AND e.module_id = %s
                  AND e.status IN ('active', 'completed')
            """, (token_data.user_id, module_id))
        else:
            cursor.execute("""
                SELECT DISTINCT student_id FROM (
                    SELECT e.student_id FROM enrollments e
                    JOIN modules m ON e.module_id = m.id
                    WHERE m.teacher_id = %s AND e.status IN ('active', 'completed')
                    UNION
                    SELECT ce.student_id FROM class_enrollments ce
                    JOIN classes c ON ce.class_id = c.id
                    WHERE c.teacher_id = %s AND ce.status = 'approved'
                ) AS all_students
            """, (token_data.user_id, token_data.user_id))
        student_rows = cursor.fetchall()

    if not student_rows:
        return {"success": True, "students": [], "summary": {}}

    student_ids = [r[0] for r in student_rows]
    orch = get_orchestrator()
    orch_results = await asyncio.to_thread(orch.predict_batch, student_ids)

    results = []
    for sid in student_ids:
        r = orch_results.get(sid, {})
        preds = r.get("predictions", {})
        drop = preds.get("dropout_risk", {})
        perf = preds.get("performance_projected", {})
        eng = preds.get("engagement_projected", {})
        frust = preds.get("frustration_projected", {})
        results.append({
            "student_id": sid,
            "dropout_risk": drop.get("probability", 0),
            "dropout_risk_label": drop.get("label", "low"),
            "performance_score": perf.get("value", 0),
            "performance_label": perf.get("label", "unknown"),
            "engagement_score": eng.get("value", 0),
            "frustration_level": frust.get("class", 0),
            "frustration_label": frust.get("label", "baja"),
            "cluster": r.get("cluster", {}),
            "anomaly": r.get("anomaly", {}),
        })

    at_risk_count = sum(1 for r in results if r["dropout_risk_label"] == "alto")
    avg_dropout = sum(r["dropout_risk"] for r in results) / len(results) if results else 0
    avg_performance = sum(r["performance_score"] for r in results) / len(results) if results else 0
    avg_engagement = sum(r["engagement_score"] for r in results) / len(results) if results else 0

    return {
        "success": True,
        "students": results,
        "summary": {
            "total_students": len(results),
            "avg_dropout_risk": round(avg_dropout, 4),
            "avg_performance": round(avg_performance, 4),
            "avg_engagement": round(avg_engagement, 4),
            "at_risk_count": at_risk_count,
        },
    }


@analytics_router.get("/class/{class_id}")
async def get_class_analytics(
    class_id: int,
    token_data=Depends(_require_teacher),
):
    """Class-level aggregated analytics"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(
            "SELECT student_id FROM class_enrollments WHERE class_id = %s AND status = 'approved'",
            (class_id,),
        )
        rows = cursor.fetchall()

    if not rows:
        return {"success": True, "class_id": class_id, "total_students": 0, "students": [], "summary": {}}

    student_ids = [r[0] for r in rows]
    orch = get_orchestrator()

    try:
        batch_results = await asyncio.wait_for(
            asyncio.to_thread(orch.predict_batch, student_ids),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        return {
            "success": True,
            "class_id": class_id,
            "total_students": len(student_ids),
            "students": [],
            "summary": {},
            "processing": True,
            "message": "Predicciones en proceso. Vuelve a intentar en unos segundos."
        }
    student_results = list(batch_results.values())

    cluster_counts = {}
    at_risk = []
    high_frustration = []
    eng_vals = []
    perf_vals = []

    for s in student_results:
        preds = s.get("predictions", {})
        cname = s.get("cluster", {}).get("cluster_name", "unknown")
        cluster_counts[cname] = cluster_counts.get(cname, 0) + 1
        eng = preds.get("engagement_projected", {}).get("value", 0)
        perf = preds.get("performance_projected", {}).get("value", 0)
        eng_vals.append(eng)
        perf_vals.append(perf)
        if preds.get("dropout_risk", {}).get("label") == "alto":
            at_risk.append(s["student_id"])
        if preds.get("frustration_projected", {}).get("class", 0) >= 2:
            high_frustration.append(s["student_id"])

    cluster_list = [
        {"cluster_name": k, "count": v}
        for k, v in sorted(cluster_counts.items(), key=lambda x: -x[1])
    ]

    avg_eng = round(float(np.mean(eng_vals)), 4) if eng_vals else 0
    avg_perf = round(float(np.mean(perf_vals)), 4) if perf_vals else 0

    insights = orch.recommender.generate_teacher_insights(
        cluster_summary=cluster_list,
        at_risk_count=len(at_risk),
        high_frustration_count=len(high_frustration),
        avg_engagement=avg_eng,
        avg_performance=avg_perf,
    )

    weekly_trends = await _weekly_repo.get_class_trends(student_ids, weeks=8)

    return {
        "success": True,
        "class_id": class_id,
        "total_students": len(student_ids),
        "students": student_results,
        "summary": {
            "total_students": len(student_ids),
            "avg_engagement": avg_eng,
            "avg_performance": avg_perf,
            "at_risk_count": len(at_risk),
            "high_frustration_count": len(high_frustration),
        },
        "cluster_distribution": cluster_list,
        "at_risk_students": at_risk,
        "high_frustration_students": high_frustration,
        "insights": insights,
        "weekly_trends": [w.to_dict() for w in weekly_trends],
    }


@analytics_router.get("/risk-students")
async def get_risk_students(
    min_dropout_risk: float = 0.5,
    token_data=Depends(_require_teacher),
):
    """Students at risk (dropout risk > threshold)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT e.student_id FROM enrollments e
            WHERE e.status IN ('active', 'completed')
            UNION
            SELECT DISTINCT ce.student_id FROM class_enrollments ce
            WHERE ce.status = 'approved'
        """)
        rows = cursor.fetchall()

    if not rows:
        return {"success": True, "risk_students": [], "total_count": 0}

    orch = get_orchestrator()
    student_ids = [r[0] for r in rows]
    try:
        batch_results = await asyncio.wait_for(
            asyncio.to_thread(orch.predict_batch, student_ids),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return {
            "success": True,
            "risk_students": [],
            "total_count": 0,
            "processing": True,
            "message": "Las predicciones se están procesando. Intenta de nuevo en unos segundos."
        }

    risk_students = []
    for sid, result in batch_results.items():
        preds = result.get("predictions", {})
        dropout = preds.get("dropout_risk", {})
        frustration = preds.get("frustration_projected", {})
        engagement = preds.get("engagement_projected", {})
        dropout_prob = dropout.get("probability", 0)
        frustration_class = frustration.get("class", 0)
        engagement_val = engagement.get("value", 0.5)
        if dropout_prob >= min_dropout_risk or frustration_class >= 2 or engagement_val < 0.4:
            risk_students.append({
                "student_id": sid,
                "dropout_risk": dropout_prob,
                "dropout_label": dropout.get("label", "bajo"),
                "frustration_level": frustration_class,
                "frustration_label": frustration.get("label", "baja"),
                "engagement": engagement_val,
                "engagement_label": engagement.get("label", "medio"),
                "performance": preds.get("performance_projected", {}).get("value", 0.5),
                "cluster": result.get("cluster", {}).get("cluster_name", "unknown"),
                "anomaly": result.get("anomaly", {}),
            })

    risk_students.sort(key=lambda x: -x["dropout_risk"])

    return {
        "success": True,
        "risk_students": risk_students,
        "total_count": len(risk_students),
    }


@analytics_router.get("/clusters")
async def get_clusters(token_data=Depends(_require_teacher)):
    """Learning clusters distribution with PCA projection"""
    orch = get_orchestrator()
    try:
        pca = await asyncio.wait_for(
            asyncio.to_thread(orch.get_clustering_pca),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return {
            "success": True,
            "pca_projection": [],
            "cluster_info": None,
            "processing": True,
            "message": "Los clusters se están calculando. Intenta de nuevo en unos segundos."
        }

    return {
        "success": True,
        "pca_projection": pca,
        "cluster_info": {
            "n_clusters": 4,
            "labels": ["Principiante", "Regular", "Avanzado", "En Riesgo"],
        },
    }


@analytics_router.get("/anomalies")
async def get_anomalies(
    min_score: float = 0.0,
    token_data=Depends(_require_teacher),
):
    """Detected behavioral anomalies"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT e.student_id FROM enrollments e
            WHERE e.status IN ('active', 'completed')
            UNION
            SELECT DISTINCT ce.student_id FROM class_enrollments ce
            WHERE ce.status = 'approved'
        """)
        rows = cursor.fetchall()

    if not rows:
        return {"success": True, "anomalies": [], "total_count": 0}

    orch = get_orchestrator()
    student_ids = [r[0] for r in rows]
    try:
        batch_results = await asyncio.wait_for(
            asyncio.to_thread(orch.predict_batch, student_ids),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return {
            "success": True,
            "anomalies": [],
            "total_count": 0,
            "processing": True,
            "message": "Las predicciones se están procesando. Intenta de nuevo en unos segundos."
        }

    anomalies = []
    for sid, result in batch_results.items():
        anomaly = result.get("anomaly", {})
        if anomaly.get("is_anomaly", False) and anomaly.get("anomaly_score", 0) >= min_score:
            anomalies.append({
                "student_id": sid,
                "anomaly_score": anomaly.get("anomaly_score", 0),
                "risk": anomaly.get("risk", "unknown"),
                "cluster": result.get("cluster", {}).get("cluster_name", "unknown"),
            })
    anomalies.sort(key=lambda x: -x["anomaly_score"])

    return {
        "success": True,
        "anomalies": anomalies,
        "total_count": len(anomalies),
    }
