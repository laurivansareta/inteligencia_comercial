"""
CYCLE AI - Ponte de Serviço de Machine Learning para a API REST:
Permite que o backend Node.js/TypeScript consulte previsões de Segmentação,
Churn (com explicabilidade SHAP) e Growth com máxima performance e confiabilidade.
"""

import sys
import os

# Garantir codificação UTF-8 padrão para I/O no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import argparse
import pandas as pd
from database.connection import get_engine
from ml.segmentation.predict import CustomerSegmenter
from ml.churn.predict import ChurnPredictor
from ml.growth.predict import GrowthPredictor


def load_latest_snapshots(customer_id: int = None) -> pd.DataFrame:
    """Carrega o snapshot mais recente dos clientes."""
    where_clause = "WHERE s.data_referencia = (SELECT MAX(data_referencia) FROM ml_cliente_snapshot)"
    if customer_id is not None:
        where_clause += f" AND s.id_cliente = {customer_id}"
        
    query = f"""
    SELECT 
        s.id_cliente,
        c.nome_fantasia,
        c.tipo_cliente,
        c.porte,
        c.uf,
        c.id_filial,
        f.descricao as filial_descricao,
        c.id_vendedor,
        v.descricao as vendedor_descricao,
        c.data_cadastro,
        c.fl_ativo,
        s.recency_days,
        s.frequency_30d,
        s.frequency_90d,
        s.frequency_180d,
        s.revenue_30d,
        s.revenue_90d,
        s.revenue_180d,
        s.revenue_365d,
        s.avg_ticket_90d,
        s.revenue_variation_90d,
        s.frequency_variation_90d,
        s.avg_days_between_orders,
        s.category_diversity,
        s.avg_payment_delay,
        s.late_payment_rate
    FROM ml_cliente_snapshot s
    JOIN dim_cliente c ON s.id_cliente = c.id_cliente
    JOIN dim_filial f ON c.id_filial = f.id_filial
    JOIN dim_vendedor v ON c.id_vendedor = v.id_vendedor
    {where_clause}
    ORDER BY s.id_cliente;
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def score_all_customers() -> list:
    """Aplica os três modelos a todos os clientes do último snapshot."""
    df = load_latest_snapshots()
    if df.empty:
        return []
        
    segmenter = CustomerSegmenter()
    churn_pred = ChurnPredictor()
    growth_pred = GrowthPredictor()
    
    df_seg = segmenter.predict(df)
    df_churn = churn_pred.predict(df_seg)
    df_final = growth_pred.predict(df_churn)
    
    # Converter para formato de dicionário
    records = df_final.to_dict(orient="records")
    return records


def explain_single_customer(customer_id: int) -> dict:
    """Gera previsões e explicabilidade SHAP detalhada para um cliente específico."""
    df = load_latest_snapshots(customer_id=customer_id)
    if df.empty:
        return {}
        
    cust_row = df.iloc[0]
    
    segmenter = CustomerSegmenter()
    churn_pred = ChurnPredictor()
    growth_pred = GrowthPredictor()
    
    df_scored = growth_pred.predict(churn_pred.predict(segmenter.predict(df))).iloc[0]
    shap_explanation = churn_pred.explain_customer(cust_row)
    
    return {
        "customer": {
            "id_cliente": int(cust_row["id_cliente"]),
            "nome_fantasia": str(cust_row["nome_fantasia"]),
            "tipo_cliente": str(cust_row["tipo_cliente"]),
            "porte": str(cust_row["porte"]),
            "uf": str(cust_row["uf"]),
            "id_filial": int(cust_row["id_filial"]),
            "filial_descricao": str(cust_row["filial_descricao"]),
            "id_vendedor": int(cust_row["id_vendedor"]),
            "vendedor_descricao": str(cust_row["vendedor_descricao"]),
            "data_cadastro": str(cust_row["data_cadastro"]),
            "fl_ativo": bool(cust_row["fl_ativo"]),
        },
        "segmentation": {
            "cluster_id": int(df_scored["cluster_id"]),
            "cluster_nome": str(df_scored["cluster_nome"]),
        },
        "churn": {
            "probabilidade": float(df_scored["churn_probabilidade"]),
            "faixa_risco": str(df_scored["faixa_risco"]),
            "fatores_aumento_risco": shap_explanation.get("fatores_elevaram_risco", []),
            "fatores_reducao_risco": shap_explanation.get("fatores_reduziram_risco", [])
        },
        "growth": {
            "faturamento_previsto_90d": float(df_scored["faturamento_previsto_90d"]),
            "potencial_absoluto": float(df_scored["potencial_absoluto"]),
            "variacao_estimada_pct": float(df_scored["variacao_estimada_pct"]),
            "fl_oportunidade_expansao": bool(df_scored["fl_oportunidade_expansao"])
        }
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["score_all", "explain_one"], default="score_all")
    parser.add_argument("--customer-id", type=int, default=None)
    args = parser.parse_args()
    
    if args.action == "score_all":
        res = score_all_customers()
        print(json.dumps(res, ensure_ascii=False, default=str))
    elif args.action == "explain_one":
        if args.customer_id is None:
            print(json.dumps({"error": "customer-id is required for explain_one"}))
            sys.exit(1)
        res = explain_single_customer(args.customer_id)
        print(json.dumps(res, ensure_ascii=False, default=str))
