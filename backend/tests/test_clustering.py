import pytest
import numpy as np


class TestLearningClustering:
    def test_train_and_silhouette(self, clustering, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_clustering
        X = []
        for sid in synthetic_dataset["student_id"].unique():
            feats = extract_features_for_clustering(synthetic_dataset, sid)
            if feats is not None:
                X.append(feats)
        if len(X) < 5:
            pytest.skip("Not enough samples")
        X_arr = np.array(X)
        result = clustering.train(X_arr)
        assert result["silhouette_score"] > -1.0
        assert result["silhouette_score"] < 1.0
        assert result["n_clusters"] == 4

    def test_predict(self, clustering, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_clustering
        sids = synthetic_dataset["student_id"].unique()[:5]
        for sid in sids:
            feats = extract_features_for_clustering(synthetic_dataset, sid)
            if feats is not None:
                pred = clustering.predict(feats)
                assert "cluster_id" in pred
                assert "cluster_name" in pred
                break

    def test_pca_projection(self, clustering, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_clustering
        X = []
        for sid in synthetic_dataset["student_id"].unique()[:50]:
            feats = extract_features_for_clustering(synthetic_dataset, sid)
            if feats is not None:
                X.append(feats)
        if len(X) < 5:
            pytest.skip("Not enough samples")
        X_arr = np.array(X)
        clustering.train(X_arr)
        pca = clustering.get_pca_projection(X_arr)
        assert "pca1" in pca
        assert "pca2" in pca
        assert "labels" in pca
        assert len(pca["pca1"]) == len(X_arr)
        assert len(pca["labels"]) == len(X_arr)

    def test_summary(self, clustering, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_clustering
        X = []
        for sid in synthetic_dataset["student_id"].unique()[:30]:
            feats = extract_features_for_clustering(synthetic_dataset, sid)
            if feats is not None:
                X.append(feats)
        if len(X) < 5:
            pytest.skip("Not enough samples")
        X_arr = np.array(X)
        clustering.train(X_arr)
        summary = clustering.get_summary(X_arr)
        assert len(summary) > 0
        total = sum(c["count"] for c in summary)
        assert total == len(X_arr)
