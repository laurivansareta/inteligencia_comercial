"""
Gerador de fato_pagamento:
- Gera títulos a receber correspondentes às vendas
- Define prazos de pagamento realistas (30, 45 ou 60 dias)
- Simula pagamentos em dia, antecipados, com atraso e inadimplência
- Garante todas as regras de integridade:
  * data_vencimento >= data_emissao
  * data_pagamento IS NULL OR data_pagamento >= data_emissao
  * valor_titulo e valor_pago >= 0
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta


def generate_payments_from_sales(
    sales_df: pd.DataFrame,
    profiles_df: pd.DataFrame = None,
    current_date: date = date(2026, 10, 31),
    seed: int = 42
) -> pd.DataFrame:
    """
    Gera fato_pagamento a partir de um lote de fato_venda.
    """
    if sales_df.empty:
        return pd.DataFrame()
        
    rng = np.random.default_rng(seed)
    n_vendas = len(sales_df)
    
    # Mapear perfil do cliente se disponível
    perfil_map = {}
    if profiles_df is not None:
        perfil_map = dict(zip(profiles_df["id_cliente"], profiles_df["perfil_comportamental"]))
        
    payments = []
    
    # Agrupar vendas por cliente e data para simular pedidos ou faturamento por item
    # Cada linha de fato_venda pode ter seu título ou compor um título
    # Conforme o schema: id_venda é FK direta na fato_pagamento (1:1 com fato_venda)
    
    for idx, row in sales_df.iterrows():
        venda_id = int(row["id_venda"])
        cliente_id = int(row["id_cliente"])
        dt_venda = row["data_venda"]
        if isinstance(dt_venda, str):
            dt_venda = date.fromisoformat(dt_venda)
        elif hasattr(dt_venda, "date"):
            dt_venda = dt_venda.date()
            
        valor_liq = float(row["valor_liquido"])
        perfil = perfil_map.get(cliente_id, "recorrente")
        
        data_emissao = dt_venda
        # Prazos comerciais comuns: 30 dias (70%), 45 dias (20%), 60 dias (10%)
        prazo_dias = int(rng.choice([30, 45, 60], p=[0.70, 0.20, 0.10]))
        data_vencimento = data_emissao + timedelta(days=prazo_dias)
        
        # Probabilidade de atraso e inadimplência segundo perfil
        if perfil == "estrategico":
            p_atraso = 0.05
            p_inadimplente = 0.005
        elif perfil == "recorrente":
            p_atraso = 0.12
            p_inadimplente = 0.015
        elif perfil == "em_crescimento":
            p_atraso = 0.15
            p_inadimplente = 0.02
        elif perfil == "sazonal":
            p_atraso = 0.20
            p_inadimplente = 0.03
        elif perfil == "em_retracao":
            p_atraso = 0.45
            p_inadimplente = 0.12
        elif perfil == "baixo_engajamento":
            p_atraso = 0.35
            p_inadimplente = 0.08
        else:
            p_atraso = 0.15
            p_inadimplente = 0.02
            
        # Determinar status com base na data_vencimento em relação a current_date
        if data_vencimento > current_date:
            # Título ainda não venceu
            # Pequena chance de antecipação (~10%)
            if rng.random() < 0.10:
                dias_antecipados = int(rng.integers(1, 10))
                data_pagamento = max(data_emissao, data_vencimento - timedelta(days=dias_antecipados))
                fl_pago = True
                valor_pago = valor_liq
                dias_atraso = 0
            else:
                data_pagamento = None
                fl_pago = False
                valor_pago = 0.00
                dias_atraso = 0
        else:
            # Título já venceu
            if rng.random() < p_inadimplente:
                # Inadimplente: não pago até a data de corte
                data_pagamento = None
                fl_pago = False
                valor_pago = 0.00
                dias_atraso = max(1, (current_date - data_vencimento).days)
            else:
                # Foi pago
                fl_pago = True
                valor_pago = valor_liq
                if rng.random() < p_atraso:
                    # Pagamento com atraso
                    atraso = int(np.clip(rng.exponential(scale=14.0) + 1, 1, 90))
                    data_pagamento = data_vencimento + timedelta(days=atraso)
                    dias_atraso = atraso
                else:
                    # Pago em dia ou antecipado (0 a 3 dias antes)
                    antecip = int(rng.choice([0, 0, 0, 1, 2, 3]))
                    data_pagamento = max(data_emissao, data_vencimento - timedelta(days=antecip))
                    dias_atraso = 0
                    
        payments.append({
            "id_pagamento": venda_id,  # 1 título por venda
            "id_cliente": cliente_id,
            "id_venda": venda_id,
            "data_emissao": data_emissao,
            "data_vencimento": data_vencimento,
            "data_pagamento": data_pagamento,
            "valor_titulo": valor_liq,
            "valor_pago": valor_pago,
            "dias_atraso": dias_atraso,
            "fl_pago": fl_pago
        })
        
    return pd.DataFrame(payments)

