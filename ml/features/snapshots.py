"""
Geração de Snapshots Históricos para Machine Learning (ml_cliente_snapshot):
Garante rigor temporal absoluto:
- Features utilizam ESTRITAMENTE dados ocorridos até a data_referencia (T).
- Labels utilizam ESTRITAMENTE a janela futura (T, T + 90 dias].
- Snapshots sem janela futura completa recebem labels NULL (destinados à inferência/produção).
- Zero data leakage entre passado e futuro.
"""

from datetime import date
from typing import List, Optional
from database.connection import get_connection


def build_snapshot_for_date(reference_date: date, feature_version: str = "v1.0") -> int:
    """
    Gera o snapshot para todos os clientes ativos em uma data de referência específica.
    """
    # Consulta SQL com janelas temporais estritas
    query = """
    WITH 
    -- 1. Clientes elegíveis (cadastrados até a data de referência)
    clientes_elegiveis AS (
        SELECT id_cliente, data_cadastro
        FROM dim_cliente
        WHERE data_cadastro <= %(ref_date)s
    ),
    
    -- 2. Vendas passadas (data_venda <= ref_date)
    vendas_passadas AS (
        SELECT 
            v.id_cliente,
            v.data_venda,
            v.valor_liquido,
            p.id_categoria
        FROM fato_venda v
        JOIN dim_produto p ON v.id_produto = p.id_produto
        WHERE v.data_venda <= %(ref_date)s
    ),
    
    -- 3. Métricas de Vendas Passadas
    metricas_vendas AS (
        SELECT 
            ce.id_cliente,
            COALESCE((%(ref_date)s - MAX(vp.data_venda)), 999) AS recency_days,
            
            -- Frequências (pedidos distintos por dia)
            COUNT(DISTINCT CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '30 days') THEN vp.data_venda END) AS frequency_30d,
            COUNT(DISTINCT CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '90 days') THEN vp.data_venda END) AS frequency_90d,
            COUNT(DISTINCT CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '180 days') THEN vp.data_venda END) AS frequency_180d,
            COUNT(DISTINCT CASE WHEN vp.data_venda < (%(ref_date)s - INTERVAL '90 days') 
                                 AND vp.data_venda >= (%(ref_date)s - INTERVAL '180 days') THEN vp.data_venda END) AS frequency_prev_90d,
            
            -- Faturamentos
            COALESCE(SUM(CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '30 days') THEN vp.valor_liquido END), 0.00) AS revenue_30d,
            COALESCE(SUM(CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '90 days') THEN vp.valor_liquido END), 0.00) AS revenue_90d,
            COALESCE(SUM(CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '180 days') THEN vp.valor_liquido END), 0.00) AS revenue_180d,
            COALESCE(SUM(CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '365 days') THEN vp.valor_liquido END), 0.00) AS revenue_365d,
            COALESCE(SUM(CASE WHEN vp.data_venda < (%(ref_date)s - INTERVAL '90 days') 
                               AND vp.data_venda >= (%(ref_date)s - INTERVAL '180 days') THEN vp.valor_liquido END), 0.00) AS revenue_prev_90d,
                               
            -- Diversidade de categorias nos últimos 180 dias
            COUNT(DISTINCT CASE WHEN vp.data_venda >= (%(ref_date)s - INTERVAL '180 days') THEN vp.id_categoria END) AS category_diversity
        FROM clientes_elegiveis ce
        LEFT JOIN vendas_passadas vp ON ce.id_cliente = vp.id_cliente
        GROUP BY ce.id_cliente
    ),
    
    -- 4. Métricas de Pagamentos Passados
    metricas_pagamentos AS (
        SELECT 
            ce.id_cliente,
            COALESCE(AVG(p.dias_atraso), 0.0) AS avg_payment_delay,
            COALESCE(
                COUNT(CASE WHEN p.dias_atraso > 0 THEN 1 END)::NUMERIC / 
                NULLIF(COUNT(p.id_pagamento), 0), 0.0
            ) AS late_payment_rate
        FROM clientes_elegiveis ce
        LEFT JOIN fato_pagamento p ON ce.id_cliente = p.id_cliente AND p.data_emissao <= %(ref_date)s
        GROUP BY ce.id_cliente
    ),
    
    -- 5. Labels Futuros (janela estrita: ref_date < data_venda <= ref_date + 90 dias)
    -- Apenas se a janela de 90 dias já tiver sido completamente observada no banco
    max_data_global AS (
        SELECT MAX(data_venda) AS max_venda FROM fato_venda
    ),
    
    vendas_futuras AS (
        SELECT 
            v.id_cliente,
            COUNT(DISTINCT v.data_venda) AS future_orders_90d,
            SUM(v.valor_liquido) AS future_revenue_90d
        FROM fato_venda v
        WHERE v.data_venda > %(ref_date)s 
          AND v.data_venda <= (%(ref_date)s + INTERVAL '90 days')
        GROUP BY v.id_cliente
    )
    
    INSERT INTO ml_cliente_snapshot (
        id_cliente,
        data_referencia,
        recency_days,
        frequency_30d,
        frequency_90d,
        frequency_180d,
        revenue_30d,
        revenue_90d,
        revenue_180d,
        revenue_365d,
        avg_ticket_90d,
        revenue_variation_90d,
        frequency_variation_90d,
        avg_days_between_orders,
        category_diversity,
        avg_payment_delay,
        late_payment_rate,
        returns_rate,
        churn_label_90d,
        future_revenue_90d,
        feature_version
    )
    SELECT 
        ce.id_cliente,
        %(ref_date)s AS data_referencia,
        mv.recency_days,
        mv.frequency_30d,
        mv.frequency_90d,
        mv.frequency_180d,
        mv.revenue_30d,
        mv.revenue_90d,
        mv.revenue_180d,
        mv.revenue_365d,
        ROUND(COALESCE(mv.revenue_90d / NULLIF(mv.frequency_90d, 0), 0.00), 2) AS avg_ticket_90d,
        
        -- Variação de receita (90d vs 90d anteriores)
        ROUND(
            COALESCE((mv.revenue_90d - mv.revenue_prev_90d) / NULLIF(mv.revenue_prev_90d, 0), 0.0),
            4
        ) AS revenue_variation_90d,
        
        -- Variação de frequência
        ROUND(
            COALESCE((mv.frequency_90d - mv.frequency_prev_90d)::NUMERIC / NULLIF(mv.frequency_prev_90d, 0), 0.0),
            4
        ) AS frequency_variation_90d,
        
        -- Intervalo médio entre pedidos nos últimos 180 dias
        ROUND(
            CASE 
                WHEN mv.frequency_180d > 1 THEN 180.0 / mv.frequency_180d 
                ELSE COALESCE(mv.recency_days, 180.0) 
            END,
            2
        ) AS avg_days_between_orders,
        
        mv.category_diversity,
        ROUND(mp.avg_payment_delay, 2) AS avg_payment_delay,
        ROUND(mp.late_payment_rate, 4) AS late_payment_rate,
        0.0000 AS returns_rate,
        
        -- Label Churn 90d (1 se NÃO comprou nos próximos 90 dias, 0 se comprou)
        -- Se a janela futura de 90 dias não terminou no banco, label fica NULL
        CASE 
            WHEN (%(ref_date)s + INTERVAL '90 days') > mg.max_venda THEN NULL
            WHEN COALESCE(vf.future_orders_90d, 0) = 0 THEN 1 
            ELSE 0 
        END AS churn_label_90d,
        
        -- Label Faturamento Futuro 90d
        CASE 
            WHEN (%(ref_date)s + INTERVAL '90 days') > mg.max_venda THEN NULL
            ELSE ROUND(COALESCE(vf.future_revenue_90d, 0.00), 2)
        END AS future_revenue_90d,
        
        %(feature_version)s AS feature_version
    FROM clientes_elegiveis ce
    JOIN metricas_vendas mv ON ce.id_cliente = mv.id_cliente
    JOIN metricas_pagamentos mp ON ce.id_cliente = mp.id_cliente
    CROSS JOIN max_data_global mg
    LEFT JOIN vendas_futuras vf ON ce.id_cliente = vf.id_cliente
    ON CONFLICT (id_cliente, data_referencia) DO UPDATE SET
        recency_days = EXCLUDED.recency_days,
        frequency_30d = EXCLUDED.frequency_30d,
        frequency_90d = EXCLUDED.frequency_90d,
        frequency_180d = EXCLUDED.frequency_180d,
        revenue_30d = EXCLUDED.revenue_30d,
        revenue_90d = EXCLUDED.revenue_90d,
        revenue_180d = EXCLUDED.revenue_180d,
        revenue_365d = EXCLUDED.revenue_365d,
        avg_ticket_90d = EXCLUDED.avg_ticket_90d,
        revenue_variation_90d = EXCLUDED.revenue_variation_90d,
        frequency_variation_90d = EXCLUDED.frequency_variation_90d,
        avg_days_between_orders = EXCLUDED.avg_days_between_orders,
        category_diversity = EXCLUDED.category_diversity,
        avg_payment_delay = EXCLUDED.avg_payment_delay,
        late_payment_rate = EXCLUDED.late_payment_rate,
        returns_rate = EXCLUDED.returns_rate,
        churn_label_90d = EXCLUDED.churn_label_90d,
        future_revenue_90d = EXCLUDED.future_revenue_90d,
        feature_version = EXCLUDED.feature_version;
    """
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, {"ref_date": reference_date, "feature_version": feature_version})
            count = cur.rowcount
        conn.commit()
        return count
    finally:
        conn.close()


def generate_all_snapshots(
    reference_dates: Optional[List[date]] = None,
    feature_version: str = "v1.0"
) -> dict[str, int]:
    """
    Gera snapshots históricos em múltiplas datas de corte cronológicas para treino,
    validação e teste/produção.
    """
    if reference_dates is None:
        # Datas de corte recomendadas cobrindo os 36 meses
        reference_dates = [
            date(2024, 12, 31),  # Treino histórico 1
            date(2025, 6, 30),   # Treino histórico 2
            date(2025, 12, 31),  # Validação temporal
            date(2026, 6, 30),   # Teste temporal (com 90 dias de label até out/2026)
            date(2026, 10, 31)   # Ponto atual / Produção (sem janela futura => labels NULL)
        ]
        
    results = {}
    for dt in reference_dates:
        print(f"-> Gerando snapshot para data de referência: {dt.strftime('%d/%m/%Y')}...")
        count = build_snapshot_for_date(dt, feature_version)
        results[dt.isoformat()] = count
        print(f"   Concluído: {count} snapshots registrados.")
        
    return results
