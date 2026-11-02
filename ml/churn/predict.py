"""
Módulo de inferência e explicabilidade de Churn - CYCLE AI:
- Carrega o modelo campeão, scaler e SHAP explainer
- Gera probabilidade estimada e faixa de risco comercial
- Fornece os principais fatores que aumentam e reduzem o risco individual
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "churn")

FEATURE_LABELS_BR = {
    "recency_days": "Dias sem comprar (Recência)",
    "frequency_30d": "Pedidos nos últimos 30 dias",
    "frequency_90d": "Pedidos nos últimos 90 dias",
    "frequency_180d": "Pedidos nos últimos 180 dias",
    "revenue_30d": "Faturamento 30 dias",
    "revenue_90d": "Faturamento 90 dias",
    "revenue_180d": "Faturamento 180 dias",
    "revenue_365d": "Faturamento 365 dias",
    "avg_ticket_90d": "Ticket Médio (90 dias)",
    "revenue_variation_90d": "Variação do Faturamento (90d vs anterior)",
    "frequency_variation_90d": "Variação de Frequência (90d vs anterior)",
    "avg_days_between_orders": "Intervalo Médio entre Compras",
    "category_diversity": "Diversidade de Categorias Compradas",
    "avg_payment_delay": "Média de Dias de Atraso em Títulos",
    "late_payment_rate": "Taxa de Títulos com Atraso"
}


class ChurnPredictor:
    """Preditor e Explicador de Churn com SHAP."""
    
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_path = os.path.join(model_dir, "best_model.joblib")
        self.scaler_path = os.path.join(model_dir, "scaler.joblib")
        self.explainer_path = os.path.join(model_dir, "shap_explainer.joblib")
        self.meta_path = os.path.join(model_dir, "metrics.json")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Artefatos de Churn não encontrados em {model_dir}. Treine o modelo primeiro.")
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.explainer = joblib.load(self.explainer_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        self.features = self.metadata["features"]
        
    def classify_risk_tier(self, prob: float) -> str:
        """Classifica a probabilidade em faixas de risco comercial."""
        if prob >= 0.60:
            return "Alto Risco"
        elif prob >= 0.25:
            return "Médio Risco"
        else:
            return "Baixo Risco"
            
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula probabilidades de churn e faixas de risco."""
        X_raw = df[self.features].copy().fillna(0.0)
        X_scaled = self.scaler.transform(X_raw)
        
        probs = self.model.predict_proba(X_scaled)[:, 1]
        
        df_out = df.copy()
        df_out["churn_probabilidade"] = np.round(probs, 4)
        df_out["faixa_risco"] = [self.classify_risk_tier(p) for p in probs]
        df_out["modelo_versao"] = self.metadata["model_type"]
        
        return df_out
        
    def explain_customer(self, customer_features: pd.Series, top_n: int = 3) -> dict:
        """
        Gera explicação individual baseada em SHAP para um cliente:
        - Fatores que aumentaram o risco (SHAP positivo)
        - Fatores que reduziram o risco (SHAP negativo)
        """
        X_raw = pd.DataFrame([customer_features])[self.features].fillna(0.0)
        X_scaled = self.scaler.transform(X_raw)
        
        prob = float(self.model.predict_proba(X_scaled)[0, 1])
        shap_values = self.explainer(X_scaled)
        
        # Obter valores de SHAP para a classe positiva (churn = 1)
        if len(shap_values.shape) == 3:  # (amostras, features, classes)
            vals = shap_values.values[0, :, 1]
        else:
            vals = shap_values.values[0]
            
        feat_impacts = []
        for feat, shap_val in zip(self.features, vals):
            raw_val = customer_features.get(feat, 0.0)
            feat_impacts.append({
                "feature": feat,
                "label": FEATURE_LABELS_BR.get(feat, feat),
                "impact": float(shap_val),
                "valor_observado": float(raw_val)
            })
            
        # Fatores de aumento de risco (impacto > 0)
        risk_increasing = sorted(
            [f for f in feat_impacts if f["impact"] > 0],
            key=lambda x: x["impact"],
            reverse=True
        )[:top_n]
        
        # Fatores de proteção/redução de risco (impacto < 0)
        risk_decreasing = sorted(
            [f for f in feat_impacts if f["impact"] < 0],
            key=lambda x: x["impact"]
        )[:top_n]
        
        return {
            "churn_probabilidade": round(prob, 4),
            "faixa_risco": self.classify_risk_tier(prob),
            "fatores_elevaram_risco": risk_increasing,
            "fatores_reduziram_risco": risk_decreasing
        }

