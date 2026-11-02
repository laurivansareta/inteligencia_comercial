import os
import pytest
import pandas as pd
import numpy as np
from ml.segmentation.predict import CustomerSegmenter
from ml.churn.predict import ChurnPredictor
from ml.growth.predict import GrowthPredictor


@pytest.fixture
def sample_customer_features():
    return pd.DataFrame([
        {
            "id_cliente": 1,
            "recency_days": 12,
            "frequency_30d": 3,
            "frequency_90d": 8,
            "frequency_180d": 15,
            "revenue_30d": 4500.00,
            "revenue_90d": 12800.00,
            "revenue_180d": 24000.00,
            "revenue_365d": 48000.00,
            "avg_ticket_90d": 1600.00,
            "revenue_variation_90d": 0.15,
            "frequency_variation_90d": 0.10,
            "avg_days_between_orders": 11.2,
            "category_diversity": 7,
            "avg_payment_delay": 1.2,
            "late_payment_rate": 0.05
        },
        {
            "id_cliente": 2,
            "recency_days": 110,
            "frequency_30d": 0,
            "frequency_90d": 0,
            "frequency_180d": 1,
            "revenue_30d": 0.00,
            "revenue_90d": 0.00,
            "revenue_180d": 850.00,
            "revenue_365d": 2100.00,
            "avg_ticket_90d": 0.00,
            "revenue_variation_90d": -1.0,
            "frequency_variation_90d": -1.0,
            "avg_days_between_orders": 110.0,
            "category_diversity": 1,
            "avg_payment_delay": 35.0,
            "late_payment_rate": 0.80
        }
    ])


def test_artifacts_exist():
    expected_files = [
        "models/segmentation/kmeans_model.joblib",
        "models/segmentation/scaler.joblib",
        "models/segmentation/metadata.json",
        "models/churn/best_model.joblib",
        "models/churn/scaler.joblib",
        "models/churn/metrics.json",
        "models/churn/shap_explainer.joblib",
        "models/growth/best_model.joblib",
        "models/growth/scaler.joblib",
        "models/growth/metrics.json"
    ]
    for path in expected_files:
        assert os.path.exists(path), f"Arquivo de modelo ausente: {path}"


def test_segmenter_inference(sample_customer_features):
    segmenter = CustomerSegmenter()
    preds = segmenter.predict(sample_customer_features)
    
    assert "cluster_id" in preds.columns
    assert "cluster_nome" in preds.columns
    assert len(preds) == len(sample_customer_features)
    assert preds["cluster_id"].nunique() >= 1


def test_churn_predictor_and_explanation(sample_customer_features):
    churn_pred = ChurnPredictor()
    preds = churn_pred.predict(sample_customer_features)
    
    assert "churn_probabilidade" in preds.columns
    assert "faixa_risco" in preds.columns
    assert (preds["churn_probabilidade"] >= 0.0).all()
    assert (preds["churn_probabilidade"] <= 1.0).all()
    assert set(preds["faixa_risco"].unique()).issubset({"Baixo Risco", "Médio Risco", "Alto Risco"})
    
    # Cliente 2 (alta recência, sem compras há 110 dias) deve ter risco maior que Cliente 1
    assert preds.loc[1, "churn_probabilidade"] > preds.loc[0, "churn_probabilidade"]
    
    # Testar explicação SHAP
    explanation = churn_pred.explain_customer(sample_customer_features.iloc[1])
    assert "churn_probabilidade" in explanation
    assert "fatores_elevaram_risco" in explanation
    assert "fatores_reduziram_risco" in explanation
    assert len(explanation["fatores_elevaram_risco"]) > 0


def test_growth_predictor(sample_customer_features):
    growth_pred = GrowthPredictor()
    preds = growth_pred.predict(sample_customer_features)
    
    assert "faturamento_previsto_90d" in preds.columns
    assert "potencial_absoluto" in preds.columns
    assert "variacao_estimada_pct" in preds.columns
    assert (preds["faturamento_previsto_90d"] >= 0.0).all()
    assert (preds["potencial_absoluto"] >= 0.0).all()

