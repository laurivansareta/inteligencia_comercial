"""
Gerador de fato_venda:
- Simula 36 meses de transações comerciais realistas
- Respeita os 6 perfis comportamentais com ruído estatístico e sobreposição
- Garante integridade referencial com dim_cliente, dim_produto, dim_vendedor e dim_filial
- Calcula quantidade, valor_bruto, valor_desconto, valor_liquido e margem_valor com precisão
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Generator


def generate_sales_chunks(
    customers_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    products_df: pd.DataFrame,
    salespeople_df: pd.DataFrame,
    start_date: date = date(2023, 11, 1),
    end_date: date = date(2026, 10, 31),
    seed: int = 42,
    chunk_size_customers: int = 2000
) -> Generator[pd.DataFrame, None, None]:
    """
    Gera as vendas em chunks de clientes para permitir alta performance
    e baixo consumo de memória, gerando 36 meses completos.
    """
    rng = np.random.default_rng(seed)
    
    # Preparar dicionários de consulta rápida de produtos
    prod_ids = products_df["id_produto"].to_numpy()
    prod_prices = products_df["preco_lista"].to_numpy()
    prod_margins = products_df["margem_referencia"].to_numpy()
    prod_categories = products_df["id_categoria"].to_numpy()
    n_prods = len(prod_ids)
    
    # Mapear produtos por categoria
    cat_to_prods = {}
    for cat_id in np.unique(prod_categories):
        cat_to_prods[cat_id] = np.where(prod_categories == cat_id)[0]
        
    # Unir clientes e perfis
    cust_full = customers_df.merge(profiles_df, on="id_cliente")
    total_customers = len(cust_full)
    
    # Gerar meses do intervalo
    # Cria uma lista de (ano, mes, primeiro_dia, ultimo_dia, indice_mes_0_to_35)
    months = []
    curr = date(start_date.year, start_date.month, 1)
    month_idx = 0
    while curr <= end_date:
        next_month = date(curr.year + (curr.month // 12), (curr.month % 12) + 1, 1)
        last_day = next_month - timedelta(days=1)
        if last_day > end_date:
            last_day = end_date
        months.append((curr, last_day, month_idx))
        month_idx += 1
        curr = next_month
        
    total_months = len(months)
    global_venda_id = 1
    
    for start_idx in range(0, total_customers, chunk_size_customers):
        chunk_custs = cust_full.iloc[start_idx:start_idx + chunk_size_customers]
        sales_records = []
        
        for _, cust in chunk_custs.iterrows():
            cid = cust["id_cliente"]
            c_filial = cust["id_filial"]
            c_vendedor = cust["id_vendedor"]
            c_cadastro = cust["data_cadastro"]
            perfil = cust["perfil_comportamental"]
            porte = cust["porte"]
            
            # Fator de escala por porte
            scale_porte = 1.0 if porte == "Pequeno" else (2.4 if porte == "Médio" else 5.5)
            
            for m_start, m_end, m_idx in months:
                # Se o cliente foi cadastrado depois deste mês, não compra
                if c_cadastro > m_end:
                    continue
                    
                # Definir probabilidade e frequência esperada conforme perfil
                # 0: Nov 2023 ... 35: Out 2026
                p_compra = 0.85
                base_pedidos = 2.0
                
                if perfil == "estrategico":
                    p_compra = 0.98
                    base_pedidos = 3.5 * scale_porte
                elif perfil == "recorrente":
                    p_compra = 0.90
                    base_pedidos = 2.0 * scale_porte
                elif perfil == "em_crescimento":
                    # Cresce de 0.5 a 3.0 ao longo dos 36 meses
                    prog = m_idx / max(1, total_months - 1)
                    p_compra = 0.50 + 0.45 * prog
                    base_pedidos = (1.0 + 3.0 * prog) * scale_porte
                elif perfil == "sazonal":
                    # Pico nos meses 6, 7 (Julho) e 10, 11, 12 (Nov/Dez/Jan)
                    m_num = m_start.month
                    if m_num in [6, 7, 11, 12, 1]:
                        p_compra = 0.92
                        base_pedidos = 3.0 * scale_porte
                    else:
                        p_compra = 0.40
                        base_pedidos = 1.0 * scale_porte
                elif perfil == "em_retracao":
                    # Decai ao longo dos 36 meses, acentuando nos últimos 12 meses
                    prog = m_idx / max(1, total_months - 1)
                    p_compra = max(0.05, 0.95 - 0.85 * (prog ** 1.5))
                    base_pedidos = max(0.5, (3.0 - 2.5 * prog)) * scale_porte
                elif perfil == "baixo_engajamento":
                    p_compra = 0.28
                    base_pedidos = 1.0 * (0.8 * scale_porte)
                    
                # Ruído estocástico na decisão de compra do mês
                if rng.random() > p_compra:
                    continue
                    
                n_pedidos = int(np.clip(rng.poisson(base_pedidos), 1, 15))
                days_in_month = (m_end - m_start).days + 1
                
                for _ in range(n_pedidos):
                    day_offset = int(rng.integers(0, days_in_month))
                    venda_date = m_start + timedelta(days=day_offset)
                    if venda_date < c_cadastro:
                        venda_date = c_cadastro
                    if venda_date > end_date:
                        venda_date = end_date
                        
                    # Quantos itens no pedido (1 a 6 produtos diferentes)
                    if perfil == "estrategico":
                        n_items = int(rng.integers(3, 8))
                    elif perfil in ["recorrente", "em_crescimento"]:
                        n_items = int(rng.integers(2, 5))
                    else:
                        n_items = int(rng.integers(1, 4))
                        
                    chosen_prod_indices = rng.choice(n_prods, size=n_items, replace=False)
                    
                    for p_idx in chosen_prod_indices:
                        prod_id = int(prod_ids[p_idx])
                        preco = float(prod_prices[p_idx])
                        margem_ref = float(prod_margins[p_idx])
                        
                        # Quantidade vendida
                        if porte == "Grande":
                            qtd = float(rng.integers(2, 25))
                        elif porte == "Médio":
                            qtd = float(rng.integers(1, 10))
                        else:
                            qtd = float(rng.integers(1, 5))
                            
                        valor_bruto = round(qtd * preco, 2)
                        
                        # Desconto entre 0% e 12% (ruído)
                        desc_pct = float(rng.choice([0.0, 0.03, 0.05, 0.08, 0.10], p=[0.4, 0.25, 0.2, 0.1, 0.05]))
                        valor_desconto = round(valor_bruto * desc_pct, 2)
                        valor_liquido = round(valor_bruto - valor_desconto, 2)
                        
                        # Margem com pequena flutuação
                        margem_efetiva = float(np.clip(margem_ref - (desc_pct * 0.5) + rng.uniform(-0.02, 0.02), 0.08, 0.50))
                        margem_valor = round(valor_liquido * margem_efetiva, 2)
                        
                        sales_records.append({
                            "id_venda": global_venda_id,
                            "id_cliente": cid,
                            "id_produto": prod_id,
                            "id_vendedor": c_vendedor,
                            "id_filial": c_filial,
                            "data_venda": venda_date,
                            "quantidade": qtd,
                            "valor_bruto": valor_bruto,
                            "valor_desconto": valor_desconto,
                            "valor_liquido": valor_liquido,
                            "margem_valor": margem_valor
                        })
                        global_venda_id += 1
                        
        df_chunk = pd.DataFrame(sales_records)
        if not df_chunk.empty:
            yield df_chunk

