"""
Treinamento do Modelo de Segmentação de Clientes (K-Means) - CYCLE AI:
- Seleciona features observáveis de RFM, diversidade, regularidade e pagamento
- Aplica transformação logarítmica em variáveis assimétricas e StandardScaler
- Avalia múltiplos valores de K pelo Silhouette Score
- Perfila os clusters com métricas de negócio reais e nomes interpretáveis
- Salva artefatos e metadados em models/segmentation/
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from database.connection import get_engine
from ml.evaluation.metrics import evaluate_clustering

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "segmentation")
os.makedirs(MODEL_DIR, exist_ok=True)

SEGMENTATION_FEATURES = [
    "recency_days",
    "frequency_90d",
    "revenue_90d",
    "avg_ticket_90d",
    "category_diversity",
    "avg_days_between_orders",
    "late_payment_rate"
]

LOG_TRANSFORM_COLS = ["revenue_90d", "avg_ticket_90d", "frequency_90d"]


def load_segmentation_data() -> pd.DataFrame:
    """Carrega o snapshot mais recente dos clientes para segmentação."""
    query = """
    SELECT 
        s.id_cliente,
        s.recency_days,
        s.frequency_90d,
        s.revenue_90d,
        s.avg_ticket_90d,
        s.category_diversity,
        s.avg_days_between_orders,
        s.late_payment_rate
    FROM ml_cliente_snapshot s
    WHERE s.data_referencia = (SELECT MAX(data_referencia) FROM ml_cliente_snapshot);
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def preprocess_features(df: pd.DataFrame, scaler: StandardScaler = None, fit_scaler: bool = True):
    """Aplica log1p nas variáveis de cauda longa e padronização."""
    X = df[SEGMENTATION_FEATURES].copy()
    
    # Preencher nulos por segurança
    X = X.fillna(0.0)
    
    # Log transform
    for col in LOG_TRANSFORM_COLS:
        X[col] = np.log1p(np.maximum(0.0, X[col].astype(float)))
        
    if fit_scaler:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        if scaler is None:
            raise ValueError("Scaler deve ser fornecido quando fit_scaler=False")
        X_scaled = scaler.transform(X)
        
    return X_scaled, scaler


def assign_cluster_business_names(df_profile: pd.DataFrame) -> dict[int, str]:
    """
    Analisa os centróides do cluster e atribui um nome comercial compreensível.
    Critérios:
    - Maior faturamento + alta diversidade => 'Campeões / Alto Valor'
    - Boa frequência + recência baixa + faturamento médio => 'Fiéis Recorrentes'
    - Recência intermediária + faturamento crescente/médio => 'Potencial de Expansão'
    - Alta recência + baixa frequência => 'Em Risco de Abandono'
    - Faturamento muito baixo + ticket baixo => 'Transacionais / Baixo Ticket'
    """
    ranked_by_rev = df_profile.sort_values(by="revenue_90d", ascending=False)
    cluster_names = {}
    
    assigned = set()
    # Campeão: maior receita
    top_cluster = int(ranked_by_rev.index[0])
    cluster_names[top_cluster] = "Campeões (Alto Faturamento & Frequência)"
    assigned.add(top_cluster)
    
    # Pior em receita e alta recência
    bottom_cluster = int(ranked_by_rev.index[-1])
    cluster_names[bottom_cluster] = "Inativos ou Baixo Engajamento"
    assigned.add(bottom_cluster)
    
    # Restantes classificados por frequência e recência
    for c_id in df_profile.index:
        c_id = int(c_id)
        if c_id in assigned:
            continue
        row = df_profile.loc[c_id]
        if row["recency_days"] > 45:
            cluster_names[c_id] = "Clientes em Alerta / Desacelerando"
        elif row["frequency_90d"] >= df_profile["frequency_90d"].median():
            cluster_names[c_id] = "Recorrentes Estáveis"
        else:
            cluster_names[c_id] = "Promissores com Potencial de Crescimento"
        assigned.add(c_id)
        
    return cluster_names


def train_segmentation(k_range=(3, 7), seed=42) -> dict:
    """Executa o pipeline completo de seleção de K, treino e persistência."""
    print("=" * 60)
    print("CYCLE AI - Treinamento de Customer Segmentation (K-Means)")
    print("=" * 60)
    
    df_raw = load_segmentation_data()
    print(f"-> Dados carregados: {len(df_raw)} clientes.")
    
    X_scaled, scaler = preprocess_features(df_raw, fit_scaler=True)
    
    # Avaliar range de K
    best_k = 4
    best_sil = -1.0
    k_evals = {}
    
    for k in range(k_range[0], k_range[1]):
        km = KMeans(n_clusters=k, random_state=seed, n_init=10)
        labels = km.fit_predict(X_scaled)
        metrics = evaluate_clustering(X_scaled, labels)
        sil = metrics["silhouette_score"]
        k_evals[k] = metrics
        print(f"   K={k} -> Silhouette Score: {sil:.4f} | Davies-Bouldin: {metrics['davies_bouldin_score']:.4f}")
        
        # Critério: melhor silhouette garantindo cluster mínimo > 5% do total
        min_cluster_pct = min(metrics["cluster_distribution"].values()) / len(df_raw)
        if sil > best_sil and min_cluster_pct >= 0.05:
            best_sil = sil
            best_k = k
            
    print(f"\n-> K selecionado como ótimo: {best_k} (Silhouette = {best_sil:.4f})")
    
    # Treinar modelo final com melhor K
    final_kmeans = KMeans(n_clusters=best_k, random_state=seed, n_init=20)
    final_labels = final_kmeans.fit_predict(X_scaled)
    
    # Calcular perfil médio dos clusters nas escalas originais
    df_with_clusters = df_raw.copy()
    df_with_clusters["cluster"] = final_labels
    cluster_profiles = df_with_clusters.groupby("cluster")[SEGMENTATION_FEATURES].mean().round(2)
    
    # Atribuir nomes comerciais
    business_names = assign_cluster_business_names(cluster_profiles)
    
    # Salvar modelo e scaler
    joblib.dump(final_kmeans, os.path.join(MODEL_DIR, "kmeans_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    
    # Salvar metadados e perfis em JSON
    metadata = {
        "model_type": "KMeans",
        "best_k": best_k,
        "features": SEGMENTATION_FEATURES,
        "log_transform_features": LOG_TRANSFORM_COLS,
        "silhouette_score": best_sil,
        "evaluations_by_k": k_evals,
        "cluster_names": business_names,
        "cluster_profiles": cluster_profiles.to_dict(orient="index"),
        "cluster_distribution": {int(k): int(v) for k, v in zip(*np.unique(final_labels, return_counts=True))}
    }
    
    with open(os.path.join(MODEL_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"-> Artefatos salvos com sucesso em: {MODEL_DIR}")
    print("\nPerfil dos Segmentos Identificados:")
    for c_id, name in business_names.items():
        prof = metadata["cluster_profiles"][c_id]
        print(f"   Cluster {c_id}: {name}")
        print(f"      Recência: {prof['recency_days']}d | Faturamento 90d: R$ {prof['revenue_90d']:,.2f} | Freq: {prof['frequency_90d']}")
        
    return metadata


if __name__ == "__main__":
    train_segmentation()
