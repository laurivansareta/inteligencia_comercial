"""
Gerador de dim_cliente:
- Clientes com nomes claramente fictícios ("Cliente Demonstração XXXXX")
- Tipos de clientes B2B, portes e filiais
- Associação a vendedores locais
- Associação a perfil comportamental interno (NÃO gravado no banco nem exposto aos modelos)
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta

TIPOS_CLIENTE = [
    "Oficina Mecânica",
    "Autopeças Varejo",
    "Centro Automotivo",
    "Frotista",
    "Concessionária"
]
PESOS_TIPOS = [0.42, 0.30, 0.15, 0.08, 0.05]

PORTES = ["Pequeno", "Médio", "Grande"]
PESOS_PORTES = [0.55, 0.35, 0.10]

UFS_POR_FILIAL = {
    1: ["SP", "SP", "SP", "RJ", "ES"],
    2: ["PR", "PR", "SC", "RS"],
    3: ["MG", "MG", "MG", "ES", "RJ"],
    4: ["GO", "GO", "DF", "MT", "MS"],
    5: ["PE", "PE", "PB", "AL", "RN", "CE", "BA"]
}

# Perfis comportamentais para geração sintética (conforme Seção 4)
PERFIS_COMPORTAMENTAIS = [
    "estrategico",
    "recorrente",
    "em_crescimento",
    "sazonal",
    "em_retracao",
    "baixo_engajamento"
]
PESOS_PERFIS = [0.10, 0.35, 0.15, 0.15, 0.15, 0.10]


def generate_customers(
    n_customers: int = 10000,
    salespeople_df: pd.DataFrame = None,
    seed: int = 42,
    base_date: date = date(2026, 10, 31)
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Gera dim_cliente e um DataFrame auxiliar com metadados de simulação
    (perfil comportamental que NÃO deve ser salvo no banco como feature de ML).
    """
    rng = np.random.default_rng(seed)
    
    # Mapeia vendedores por filial
    vendedores_por_filial = {}
    if salespeople_df is not None:
        for f_id, grp in salespeople_df.groupby("id_filial"):
            vendedores_por_filial[f_id] = grp["id_vendedor"].tolist()
    else:
        for f_id in range(1, 6):
            vendedores_por_filial[f_id] = list(range((f_id - 1) * 6 + 1, f_id * 6 + 1))
            
    clientes = []
    perfis_internos = []
    
    # Início do período histórico de 36 meses: base_date - ~36 meses (ex: Nov/2023)
    start_history = base_date - timedelta(days=36 * 30.5)
    # Cadastro pode ser até 2 anos antes do início do histórico ou durante os primeiros meses
    min_cadastro = start_history - timedelta(days=730)
    
    for i in range(1, n_customers + 1):
        nome_fantasia = f"Cliente Demonstração {i:05d}"
        tipo = rng.choice(TIPOS_CLIENTE, p=PESOS_TIPOS)
        
        # Correlação sutil entre tipo e porte
        if tipo in ["Concessionária", "Frotista"]:
            porte = rng.choice(PORTES, p=[0.20, 0.50, 0.30])
        elif tipo == "Autopeças Varejo":
            porte = rng.choice(PORTES, p=[0.40, 0.45, 0.15])
        else:
            porte = rng.choice(PORTES, p=PESOS_PORTES)
            
        # Filial (1 a 5)
        id_filial = int(rng.choice([1, 2, 3, 4, 5], p=[0.35, 0.20, 0.20, 0.15, 0.10]))
        uf = rng.choice(UFS_POR_FILIAL[id_filial])
        
        # Vendedor responsável na filial
        vendedores_filial = vendedores_por_filial.get(id_filial, [1])
        id_vendedor = int(rng.choice(vendedores_filial))
        
        # Data de cadastro (a grande maioria já era cliente antes do início dos 36m, ~15% cadastrados durante o período)
        dias_offset = int(rng.integers(0, 730 + 365))
        data_cadastro = min_cadastro + timedelta(days=dias_offset)
        if data_cadastro > base_date:
            data_cadastro = base_date - timedelta(days=30)
            
        # Perfil comportamental interno
        perfil = rng.choice(PERFIS_COMPORTAMENTAIS, p=PESOS_PERFIS)
        
        # Clientes ativos: a grande maioria está cadastrada como ativa
        fl_ativo = True
        
        clientes.append({
            "id_cliente": i,
            "nome_fantasia": nome_fantasia,
            "tipo_cliente": tipo,
            "porte": porte,
            "uf": uf,
            "id_filial": id_filial,
            "id_vendedor": id_vendedor,
            "data_cadastro": data_cadastro,
            "fl_ativo": fl_ativo
        })
        
        perfis_internos.append({
            "id_cliente": i,
            "perfil_comportamental": perfil
        })
        
    df_clientes = pd.DataFrame(clientes)
    df_perfis = pd.DataFrame(perfis_internos)
    
    return df_clientes, df_perfis
