"""
Script mestre de treinamento e avaliação de Machine Learning do CYCLE AI (Fase 2):
Executa o ciclo completo de aprendizado:
1. Customer Segmentation (K-Means com seleção ótima de K e perfis comerciais)
2. Churn Prediction (Supervisionado com validação temporal, comparação de 3 modelos e SHAP)
3. Growth Prediction (Regressão temporal, comparação de 3 modelos e cálculo de potencial)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
from ml.segmentation.train import train_segmentation
from ml.churn.train import train_churn_models
from ml.growth.train import train_growth_models


def run_all_trainings():
    print("=" * 75)
    print("CYCLE AI - Pipeline Completo de Machine Learning (Fase 2)")
    print("=" * 75)
    
    t0 = time.time()
    
    # 1. Segmentação
    print("\n>>> ETAPA 1/3: Customer Segmentation (K-Means) <<<")
    seg_meta = train_segmentation(k_range=(3, 7), seed=42)
    
    # 2. Churn
    print("\n>>> ETAPA 2/3: Churn Prediction (Classificação Supervisionada) <<<")
    churn_meta = train_churn_models(seed=42)
    
    # 3. Growth
    print("\n>>> ETAPA 3/3: Growth Prediction (Regressão Supervisionada) <<<")
    growth_meta = train_growth_models(seed=42)
    
    total_time = time.time() - t0
    
    # Sumário Executivo
    print("\n" + "=" * 75)
    print("CYCLE AI - SUMÁRIO EXECUTIVO DE MODELAGEM (FASE 2)")
    print("=" * 75)
    print(f"1. Segmentação de Clientes:")
    print(f"   - Modelo: K-Means (K={seg_meta['best_k']} clusters)")
    print(f"   - Silhouette Score: {seg_meta['silhouette_score']:.4f}")
    print(f"   - Segmentos definidos: {list(seg_meta['cluster_names'].values())}")
    
    print(f"\n2. Predição de Churn (90 dias):")
    print(f"   - Modelo Campeão: {churn_meta['model_type']}")
    test_churn = churn_meta["final_test_metrics"]
    print(f"   - Métrica F1-Score (Teste Temporal): {test_churn['f1_score']:.4f}")
    print(f"   - PR-AUC: {test_churn['pr_auc']:.4f} | ROC-AUC: {test_churn['roc_auc']:.4f}")
    print(f"   - Recall: {test_churn['recall']:.4f} | Precision: {test_churn['precision']:.4f}")
    print(f"   - Explicabilidade: SHAP TreeExplainer calibrado")
    
    print(f"\n3. Predição de Growth (Faturamento 90 dias):")
    print(f"   - Modelo Campeão: {growth_meta['model_type']}")
    test_growth = growth_meta["final_test_metrics"]
    print(f"   - MAE (Teste Temporal): R$ {test_growth['mae']:,.2f}")
    print(f"   - WAPE: {test_growth['wape']:.4f} | R²: {test_growth['r2_score']:.4f}")
    
    print("\n" + "=" * 75)
    print(f"Fase 2 concluída com sucesso em {total_time:.2f} segundos!")
    print("=" * 75)


if __name__ == "__main__":
    run_all_trainings()

