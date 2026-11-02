"""
Gerador de dim_produto:
- 1.500 SKUs distribuídos pelas 15 categorias
- Preços e margens de referência realistas
"""

import pandas as pd
import numpy as np

PREFIXOS_PRODUTOS = {
    1: ["Pastilha de Freio", "Disco de Freio", "Sapata de Freio", "Cilindro Mestre", "Pinça de Freio"],
    2: ["Amortecedor Dianteiro", "Amortecedor Traseiro", "Mola Helicoidal", "Bieleta de Suspensão", "Bucha da Bandeja"],
    3: ["Pistão com Anéis", "Biela Forjada", "Junta do Cabeçote", "Correia Dentada", "Bomba de Óleo"],
    4: ["Kit de Embreagem", "Platô e Disco", "Atuador Hidráulico", "Homocinética Externa", "Semieixo Completo"],
    5: ["Bateria Automotiva 60Ah", "Alternador 12V", "Motor de Partida", "Chicote Principal", "Módulo de Relés"],
    6: ["Farol Principal Máscara Negra", "Lanterna Traseira LED", "Lâmpada H7 Super Branca", "Farol de Milha", "Comutador de Farol"],
    7: ["Radiador de Água", "Bomba d'Água", "Válvula Termostática", "Eletroventilador", "Condensador do Ar"],
    8: ["Bico Injetor Multiponto", "Sensor de Oxigênio (Lambda)", "Sensor MAP", "Corpo de Borboleta (TBI)", "Sensor de Fase"],
    9: ["Óleo Sintético 5W30 1L", "Óleo Semi-sintético 10W40 1L", "Fluido de Freio DOT 4", "Aditivo Radiador Orgânico", "Óleo de Câmbio 75W90"],
    10: ["Silencioso Traseiro", "Tubo Intermediário", "Catalisador Homologado", "Abraçadeira de Escape", "Coletor de Escape"],
    11: ["Caixa de Direção Hidráulica", "Bomba de Direção", "Terminal de Direção", "Barra Axial", "Coluna de Direção"],
    12: ["Filtro de Óleo Blindado", "Filtro de Ar Motor", "Filtro de Combustível Injeção", "Filtro de Cabine Ar-Condicionado", "Filtro Sedimentador"],
    13: ["Rolamento de Roda Dianteiro", "Rolamento de Roda Traseiro", "Retentor de Virabrequim", "Rolamento Tensor", "Cubo de Roda com Rolamento"],
    14: ["Jogo de Velas de Ignição Iridium", "Bobina de Ignição Individual", "Cabo de Vela Resistivo", "Distribuidor de Ignição", "Módulo de Ignição"],
    15: ["Palheta Limpador Parabrisa", "Retrovisor Elétrico", "Maçaneta Externa", "Para-choque Dianteiro Primer", "Grade Dianteira Cromada"]
}


def generate_products(n_products: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Gera o DataFrame de dim_produto parametrizável."""
    rng = np.random.default_rng(seed)
    
    produtos = []
    # 15 categorias
    categorias = list(range(1, 16))
    
    for i in range(1, n_products + 1):
        # Distribui produtos pelas categorias com pesos relativamente equilibrados
        cat_id = categorias[(i - 1) % len(categorias)]
        prefixo = rng.choice(PREFIXOS_PRODUTOS[cat_id])
        codigo_mod = f"SKU-{cat_id:02d}-{i:04d}"
        descricao = f"{prefixo} {codigo_mod}"
        
        # Preço de lista com distribuição log-normal (de ~R$ 18 a R$ 2.500)
        # Media logaritmo ~4.2 (R$ 66), com cauda longa para itens caros como baterias, módulos e cabeçotes
        preco_base = float(rng.lognormal(mean=4.2, sigma=0.85))
        preco_lista = round(np.clip(preco_base, 15.00, 3200.00), 2)
        
        # Margem de referência entre 0.1500 e 0.4500 (15% a 45%)
        margem = round(float(rng.uniform(0.18, 0.42)), 4)
        
        produtos.append({
            "id_produto": i,
            "descricao": descricao,
            "id_categoria": cat_id,
            "preco_lista": preco_lista,
            "margem_referencia": margem
        })
        
    return pd.DataFrame(produtos)

