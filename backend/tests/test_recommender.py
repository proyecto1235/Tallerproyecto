import pytest


class TestRecommender:
    @pytest.fixture
    def r(self):
        from application.services.ml.recommender import Recommender
        return Recommender()

    def test_recommendations_empty(self, r):
        result = r.generate_student_recommendations()
        assert len(result) == 1
        assert "estable" in result[0]

    def test_recommendations_high_dropout(self, r):
        result = r.generate_student_recommendations(dropout_prob=0.7)
        assert any("Riesgo de abandono alto" in rec for rec in result)

    def test_recommendations_moderate_dropout(self, r):
        result = r.generate_student_recommendations(dropout_prob=0.4)
        assert any("Riesgo de abandono moderado" in rec for rec in result)

    def test_recommendations_high_frustration(self, r):
        result = r.generate_student_recommendations(frustration=2)
        assert any("Frustración alta" in rec for rec in result)

    def test_recommendations_medium_frustration(self, r):
        result = r.generate_student_recommendations(frustration=1)
        assert any("frustración media" in rec for rec in result)

    def test_recommendations_low_engagement(self, r):
        result = r.generate_student_recommendations(engagement=0.2)
        assert any("críticamente bajo" in rec for rec in result)

    def test_recommendations_below_avg_engagement(self, r):
        result = r.generate_student_recommendations(engagement=0.4)
        assert any("por debajo del promedio" in rec for rec in result)

    def test_recommendations_high_engagement(self, r):
        result = r.generate_student_recommendations(engagement=0.9)
        assert any("Engagement alto" in rec for rec in result)

    def test_recommendations_low_performance(self, r):
        result = r.generate_student_recommendations(performance=0.2)
        assert any("Rendimiento bajo" in rec for rec in result)

    def test_recommendations_high_performance(self, r):
        result = r.generate_student_recommendations(performance=0.9)
        assert any("Rendimiento sobresaliente" in rec for rec in result)

    def test_recommendations_at_risk_cluster(self, r):
        result = r.generate_student_recommendations(cluster_name="En Riesgo")
        assert any("cluster 'En Riesgo'" in rec for rec in result)

    def test_recommendations_beginner_cluster(self, r):
        result = r.generate_student_recommendations(cluster_name="Principiante")
        assert any("guía de inicio rápido" in rec for rec in result)

    def test_recommendations_anomaly(self, r):
        result = r.generate_student_recommendations(anomaly={"is_anomaly": True})
        assert any("Comportamiento atípico" in rec for rec in result)

    def test_recommendations_combined(self, r):
        result = r.generate_student_recommendations(
            engagement=0.6, performance=0.7, dropout_prob=0.5,
            frustration=0, cluster_name="Principiante",
        )
        assert len(result) >= 2

    def test_teacher_insights_empty_clusters(self, r):
        result = r.generate_teacher_insights([], 0, 0, 0.5, 0.5)
        assert result == []

    def test_teacher_insights_at_risk_cluster_high(self, r):
        clusters = [{"cluster_name": "En Riesgo", "count": 30}]
        result = r.generate_teacher_insights(clusters, 5, 2, 0.3, 0.5)
        types = [ins["type"] for ins in result]
        assert "warning" in types

    def test_teacher_insights_at_risk_students_critical(self, r):
        clusters = [{"cluster_name": "Activo", "count": 20}]
        result = r.generate_teacher_insights(clusters, 5, 0, 0.5, 0.5)
        assert any(ins["type"] == "critical" for ins in result)

    def test_teacher_insights_high_frustration(self, r):
        clusters = [{"cluster_name": "Activo", "count": 20}]
        result = r.generate_teacher_insights(clusters, 0, 3, 0.5, 0.5)
        assert any("frustración" in ins["message"] for ins in result)

    def test_teacher_insights_low_engagement(self, r):
        clusters = [{"cluster_name": "Activo", "count": 20}]
        result = r.generate_teacher_insights(clusters, 0, 0, 0.3, 0.6)
        assert any("engagement" in ins["message"].lower() for ins in result)

    def test_teacher_insights_low_performance(self, r):
        clusters = [{"cluster_name": "Activo", "count": 20}]
        result = r.generate_teacher_insights(clusters, 0, 0, 0.6, 0.3)
        assert any("Rendimiento promedio bajo" in ins["message"] for ins in result)
