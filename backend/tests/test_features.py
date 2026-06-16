import pytest


class TestFeatureImportances:
    def test_engagement_has_importances(self, orchestrator):
        imps = orchestrator.engagement.get_feature_importances()
        assert len(imps) > 0

    def test_performance_has_importances(self, orchestrator):
        imps = orchestrator.performance.get_feature_importances()
        assert len(imps) > 0

    def test_dropout_has_importances(self, orchestrator):
        imps = orchestrator.dropout.get_feature_importances()
        assert len(imps) > 0

    def test_frustration_has_importances(self, orchestrator):
        imps = orchestrator.frustration.get_feature_importances()
        assert len(imps) > 0

    def test_top_features_filled(self, orchestrator):
        top = orchestrator.engagement.get_top_features(5)
        assert len(top) == 5
        assert all(isinstance(f, str) for f in top)

    def test_orchestrator_get_all(self, orchestrator):
        all_imps = orchestrator.get_feature_importances()
        for key in ["engagement", "performance", "dropout", "frustration"]:
            assert key in all_imps
            assert len(all_imps[key]) > 0
