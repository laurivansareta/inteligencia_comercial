"""
Suíte central de métricas de avaliação de Machine Learning do CYCLE AI:
- Classificação binária (Churn): Precision, Recall, F1, ROC-AUC, PR-AUC, Matriz de Confusão
- Regressão (Growth): MAE, RMSE, R², WAPE (Weighted Absolute Percentage Error)
- Clusterização (Segmentação): Silhouette Score, Davies-Bouldin, Distribuição de Clusters
"""

import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    precision_recall_curve, auc, confusion_matrix, brier_score_loss,
    mean_absolute_error, root_mean_squared_error, r2_score,
    silhouette_score, davies_bouldin_score
)
from typing import Dict, Any


def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """Calcula conjunto abrangente de métricas para classificação binária de Churn."""
    # PR-AUC (Precision-Recall AUC)
    precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recalls, precisions)
    
    # Matriz de confusão
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    return {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc": round(float(pr_auc), 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob)), 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    }


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Calcula conjunto de métricas para regressão de Growth (Faturamento Futuro)."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # WAPE (Weighted Absolute Percentage Error) - lida perfeitamente com valores zero
    denom = np.sum(np.abs(y_true))
    wape = float(np.sum(np.abs(y_true - y_pred)) / denom) if denom > 0 else 0.0
    
    return {
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "r2_score": round(float(r2), 4),
        "wape": round(float(wape), 4)
    }


def evaluate_clustering(X_scaled: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
    """Calcula métricas de qualidade de agrupamento K-Means."""
    sil = silhouette_score(X_scaled, labels)
    db = davies_bouldin_score(X_scaled, labels)
    unique, counts = np.unique(labels, return_counts=True)
    cluster_distribution = {int(k): int(v) for k, v in zip(unique, counts)}
    
    return {
        "silhouette_score": round(float(sil), 4),
        "davies_bouldin_score": round(float(db), 4),
        "cluster_distribution": cluster_distribution
    }

