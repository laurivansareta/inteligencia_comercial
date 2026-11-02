"""
Treinamento do Modelo de Predição de Crescimento / Growth (Faturamento Futuro 90d) - CYCLE AI:
- Divisão temporal cronológica
- Compara Ridge Regression (baseline), RandomForestRegressor e XGBRegressor
- Avalia métricas de regressão (MAE, RMSE, R², WAPE)
- Salva o modelo campeão e métricas em models/growth/
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from database.connection import get_engine
from ml.evaluation.metrics import evaluate_regression

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "growth")
os.makedirs(MODEL_DIR, exist_ok=True)

GROWTH_FEATURES = [
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


def load_growth_data() -> pd.DataFrame:
    """Carrega todos os snapshots históricos que possuem o faturamento futuro de 90d observado."""
    query = f"""
    SELECT 
        id_cliente,
        data_referencia,
        {", ".join(GROWTH_FEATURES)},
        future_revenue_90d
    FROM ml_cliente_snapshot
    WHERE future_revenue_90d IS NOT NULL
    ORDER BY data_referencia, id_cliente;
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def train_growth_models(seed=42) -> dict:
    print("=" * 60)
    print("CYCLE AI - Treinamento de Growth Prediction (Faturamento Futuro 90d)")
    print("=" * 60)
    
    df = load_growth_data()
    dates = sorted(df["data_referencia"].unique())
    print(f"-> Snapshots carregados: {len(df)} registros em {len(dates)} datas:")
    for d in dates:
        n_d = len(df[df["data_referencia"] == d])
        avg_rev = df[df["data_referencia"] == d]["future_revenue_90d"].mean()
        print(f"   {d}: {n_d} clientes | Média Faturamento Futuro 90d: R$ {avg_rev:,.2f}")
        
    # Divisão Cronológica
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
    
    X_train_raw = df_train[GROWTH_FEATURES].fillna(0.0)
    y_train = df_train["future_revenue_90d"].to_numpy().astype(float)
    
    X_val_raw = df_val[GROWTH_FEATURES].fillna(0.0)
    y_val = df_val["future_revenue_90d"].to_numpy().astype(float)
    
    X_test_raw = df_test[GROWTH_FEATURES].fillna(0.0)
    y_test = df_test["future_revenue_90d"].to_numpy().astype(float)
    
    # Ajustar scaler exclusivamente no treino
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_val_scaled = scaler.transform(X_val_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    
    candidates = {
        "RidgeRegression": Ridge(alpha=10.0, random_state=seed),
        "RandomForest": RandomForestRegressor(n_estimators=150, max_depth=8, random_state=seed, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=120, max_depth=5, learning_rate=0.06, random_state=seed, n_jobs=-1)
    }
    
    results = {}
    best_name = None
    best_wape = float("inf")
    best_model = None
    
    print("\n-> Avaliação na base de validação temporal:")
    for name, model in candidates.items():
        model.fit(X_train_scaled, y_train)
        
        y_val_pred = np.maximum(0.0, model.predict(X_val_scaled))
        metrics = evaluate_regression(y_val, y_val_pred)
        results[name] = {"validation_metrics": metrics}
        
        print(f"   {name:<20} | MAE: R$ {metrics['mae']:>9,.2f} | RMSE: R$ {metrics['rmse']:>9,.2f} | WAPE: {metrics['wape']:.4f} | R²: {metrics['r2_score']:.4f}")
        
        if metrics["wape"] < best_wape:
            best_wape = metrics["wape"]
            best_name = name
            best_model = model
            
    print(f"\n-> Modelo Campeão selecionado: {best_name} (WAPE Validação = {best_wape:.4f})")
    
    # Avaliação no Teste Out-of-Time
    y_test_pred = np.maximum(0.0, best_model.predict(X_test_scaled))
    test_metrics = evaluate_regression(y_test, y_test_pred)
    results[best_name]["test_metrics"] = test_metrics
    
    print(f"-> Performance no Teste Temporal ({test_date}):")
    print(f"   MAE: R$ {test_metrics['mae']:,.2f} | RMSE: R$ {test_metrics['rmse']:,.2f}")
    print(f"   WAPE: {test_metrics['wape']:.4f} | R² Score: {test_metrics['r2_score']:.4f}")
    
    # Salvar artefatos
    joblib.dump(best_model, os.path.join(MODEL_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    
    metadata = {
        "model_type": best_name,
        "features": GROWTH_FEATURES,
        "train_dates": [str(d) for d in train_dates],
        "validation_date": str(val_date),
        "test_date": str(test_date),
        "comparison_results": results,
        "final_test_metrics": test_metrics,
        "feature_importances": dict(zip(
            GROWTH_FEATURES,
            [round(float(v), 4) for v in getattr(best_model, "feature_importances_", np.abs(getattr(best_model, "coef_", np.zeros(len(GROWTH_FEATURES)))))]
        ))
    }
    
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"-> Artefatos salvos com sucesso em: {MODEL_DIR}")
    return metadata


if __name__ == "__main__":
    train_growth_models()
