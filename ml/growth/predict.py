"""
Módulo de inferência e cálculo de potencial de crescimento (Growth) - CYCLE AI:
- Carrega o modelo de regressão treinado e o scaler
- Prevê o faturamento futuro do cliente para os próximos 90 dias
- Compara com a referência histórica para calcular o potencial e variação estimada
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "growth")


class GrowthPredictor:
    """Preditor de Faturamento Futuro e Oportunidades de Expansão."""
    
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_path = os.path.join(model_dir, "best_model.joblib")
        self.scaler_path = os.path.join(model_dir, "scaler.joblib")
        self.meta_path = os.path.join(model_dir, "metrics.json")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Artefatos de Growth não encontrados em {model_dir}. Treine o modelo primeiro.")
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        self.features = self.metadata["features"]
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula previsões de faturamento futuro e potencial de crescimento."""
        X_raw = df[self.features].copy().fillna(0.0)
        X_scaled = self.scaler.transform(X_raw)
        
        raw_preds = self.model.predict(X_scaled)
        pred_rev = np.maximum(0.0, np.round(raw_preds, 2))
        
        df_out = df.copy()
        df_out["faturamento_previsto_90d"] = pred_rev
        
        # Comparação com o histórico recente (revenue_90d)
        rev_hist = df_out.get("revenue_90d", pd.Series(0.0, index=df_out.index)).fillna(0.0)
        
        delta_abs = pred_rev - rev_hist
        pct_growth = np.where(rev_hist > 0, (delta_abs / rev_hist) * 100.0, 0.0)
        
        df_out["potencial_absoluto"] = np.round(np.maximum(0.0, delta_abs), 2)
        df_out["variacao_estimada_pct"] = np.round(pct_growth, 2)
        df_out["fl_oportunidade_expansao"] = (delta_abs > 500.0) & (pct_growth >= 10.0)
        
        return df_out

