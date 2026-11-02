"""
Módulo de inferência de Segmentação de Clientes - CYCLE AI:
Carrega o modelo K-Means treinado e atribui clusters e rótulos comerciais.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "segmentation")


class CustomerSegmenter:
    """Classe de inferência de segmentação de clientes."""
    
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_path = os.path.join(model_dir, "kmeans_model.joblib")
        self.scaler_path = os.path.join(model_dir, "scaler.joblib")
        self.meta_path = os.path.join(model_dir, "metadata.json")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo não encontrado em {self.model_path}. Execute o treinamento primeiro.")
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        self.features = self.metadata["features"]
        self.log_cols = self.metadata["log_transform_features"]
        self.cluster_names = {int(k): v for k, v in self.metadata["cluster_names"].items()}
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Atribui cluster_id e cluster_name ao DataFrame fornecido.
        """
        X = df[self.features].copy().fillna(0.0)
        
        for col in self.log_cols:
            X[col] = np.log1p(np.maximum(0.0, X[col].astype(float)))
            
        X_scaled = self.scaler.transform(X)
        cluster_ids = self.model.predict(X_scaled)
        
        df_out = df.copy()
        df_out["cluster_id"] = cluster_ids
        df_out["cluster_nome"] = [self.cluster_names.get(int(cid), f"Cluster {cid}") for cid in cluster_ids]
        
        return df_out

