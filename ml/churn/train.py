"""
Treinamento do Modelo de Predição de Churn (90 dias) - CYCLE AI:
- Divisão temporal estrita (Treino: 2024 e início 2025; Validação: final 2025; Teste: meados 2026)
- Compara LogisticRegression (baseline), RandomForestClassifier e XGBClassifier
- Avalia métricas de negócio (PR-AUC, ROC-AUC, F1-Score, Matriz de Confusão)
- Gera explainer SHAP para explicabilidade individual de risco
- Salva os melhores artefatos em models/churn/
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from database.connection import get_engine
from ml.evaluation.metrics import evaluate_classification

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "churn")
os.makedirs(MODEL_DIR, exist_ok=True)

CHURN_FEATURES = [
    "recency_days",
    "frequency_30d",
    "frequency_90d",
    "frequency_180d",
    "revenue_30d",
    "revenue_90d",
    "revenue_180d",
    "revenue_365d",
    "avg_ticket_90d",
    "revenue_variation_90d",
    "frequency_variation_90d",
    "avg_days_between_orders",
    "category_diversity",
    "avg_payment_delay",
    "late_payment_rate"
]


def load_churn_data() -> pd.DataFrame:
    """Carrega todos os snapshots históricos que possuem label de churn definido."""
    query = f"""
    SELECT 
        id_cliente,
        data_referencia,
        {", ".join(CHURN_FEATURES)},
        churn_label_90d
    FROM ml_cliente_snapshot
    WHERE churn_label_90d IS NOT NULL
    ORDER BY data_referencia, id_cliente;
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def train_churn_models(seed=42) -> dict:
    print("=" * 60)
    print("CYCLE AI - Treinamento de Churn Prediction (90 dias)")
    print("=" * 60)
    
    df = load_churn_data()
    dates = sorted(df["data_referencia"].unique())
    print(f"-> Snapshots carregados: {len(df)} registros em {len(dates)} datas:")
    for d in dates:
        n_d = len(df[df["data_referencia"] == d])
        ch = df[df["data_referencia"] == d]["churn_label_90d"].sum()
        print(f"   {d}: {n_d} clientes | {ch} churns ({ch/n_d*100:.1f}%)")
        
    # Divisão Cronológica Estrita:
    # Treino: 2 primeiras datas
    # Validação: 3ª data
    # Teste: 4ª data
    train_dates = dates[:2]
    val_date = dates[2]
    test_date = dates[3]
    
    df_train = df[df["data_referencia"].isin(train_dates)].copy()
    df_val = df[df["data_referencia"] == val_date].copy()
    df_test = df[df["data_referencia"] == test_date].copy()
    
    print(f"\n-> Divisão Temporal:")
    print(f"   Treino: {len(df_train)} amostras ({train_dates})")
    print(f"   Validação: {len(df_val)} amostras ({val_date})")
    print(f"   Teste: {len(df_test)} amostras ({test_date})")
    
    X_train_raw = df_train[CHURN_FEATURES].fillna(0.0)
    y_train = df_train["churn_label_90d"].to_numpy().astype(int)
    
    X_val_raw = df_val[CHURN_FEATURES].fillna(0.0)
    y_val = df_val["churn_label_90d"].to_numpy().astype(int)
    
    X_test_raw = df_test[CHURN_FEATURES].fillna(0.0)
    y_test = df_test["churn_label_90d"].to_numpy().astype(int)
    
    # Ajustar scaler estritamente no treino
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_val_scaled = scaler.transform(X_val_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    
    # Modelos candidatos
    # Calcular class weight para classes desbalanceadas
    neg_count = np.sum(y_train == 0)
    pos_count = np.max([1, np.sum(y_train == 1)])
    scale_pos = neg_count / pos_count
    
    candidates = {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=seed
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=6,
            class_weight="balanced",
            random_state=seed,
            n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.05,
            scale_pos_weight=scale_pos,
            random_state=seed,
            eval_metric="logloss",
            n_jobs=-1
        )
    }
    
    results = {}
    best_name = None
    best_f1 = -1.0
    best_model = None
    
    print("\n-> Avaliação na base de validação temporal:")
    for name, model in candidates.items():
        # Regressão Logística usa dados escalados; Árvores usam os dados escalados uniformemente
        model.fit(X_train_scaled, y_train)
        
        y_val_prob = model.predict_proba(X_val_scaled)[:, 1]
        # Limiar de corte calibrado pelo equilíbrio entre precision e recall (default 0.5 ou adaptativo)
        y_val_pred = (y_val_prob >= 0.50).astype(int)
        
        metrics = evaluate_classification(y_val, y_val_pred, y_val_prob)
        results[name] = {"validation_metrics": metrics}
        
        print(f"   {name:<20} | F1: {metrics['f1_score']:.4f} | PR-AUC: {metrics['pr_auc']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} | Recall: {metrics['recall']:.4f} | Precision: {metrics['precision']:.4f}")
        
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_name = name
            best_model = model
            
    print(f"\n-> Modelo Campeão selecionado: {best_name} (F1 Validação = {best_f1:.4f})")
    
    # Avaliação no conjunto de Teste Out-of-Time
    y_test_prob = best_model.predict_proba(X_test_scaled)[:, 1]
    y_test_pred = (y_test_prob >= 0.50).astype(int)
    test_metrics = evaluate_classification(y_test, y_test_pred, y_test_prob)
    results[best_name]["test_metrics"] = test_metrics
    
    print(f"-> Performance no Teste Temporal ({test_date}):")
    print(f"   F1-Score: {test_metrics['f1_score']:.4f} | PR-AUC: {test_metrics['pr_auc']:.4f} | ROC-AUC: {test_metrics['roc_auc']:.4f}")
    print(f"   Recall: {test_metrics['recall']:.4f} | Precision: {test_metrics['precision']:.4f}")
    print(f"   Matriz de Confusão: {test_metrics['confusion_matrix']}")
    
    # Criar Explainer SHAP para o modelo campeão
    print("\n-> Inicializando explicabilidade SHAP...")
    if best_name in ["RandomForest", "XGBoost"]:
        explainer = shap.TreeExplainer(best_model)
    else:
        # Para linear/logística
        explainer = shap.LinearExplainer(best_model, X_train_scaled)
        
    # Salvar modelo campeão, scaler, explainer e métricas
    joblib.dump(best_model, os.path.join(MODEL_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    joblib.dump(explainer, os.path.join(MODEL_DIR, "shap_explainer.joblib"))
    
    metadata = {
        "model_type": best_name,
        "features": CHURN_FEATURES,
        "train_dates": [str(d) for d in train_dates],
        "validation_date": str(val_date),
        "test_date": str(test_date),
        "comparison_results": results,
        "final_test_metrics": test_metrics,
        "feature_importances": dict(zip(
            CHURN_FEATURES,
            [round(float(v), 4) for v in getattr(best_model, "feature_importances_", np.abs(getattr(best_model, "coef_", [np.zeros(len(CHURN_FEATURES))])[0]))]
        ))
    }
    
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"-> Artefatos e SHAP salvos com sucesso em: {MODEL_DIR}")
    return metadata


if __name__ == "__main__":
    train_churn_models()
