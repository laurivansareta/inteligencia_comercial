"""
Gerador de dados organizacionais e cadastrais da empresa fictícia de autopeças:
- Categorias (15)
- Filiais (5)
- Vendedores (30)
"""

import pandas as pd
import numpy as np

CATEGORIAS = [
    (1, "Sistemas de Freio"),
    (2, "Suspensão e Amortecedores"),
    (3, "Motor e Componentes Internos"),
    (4, "Transmissão e Embreagem"),
    (5, "Sistema Elétrico e Baterias"),
    (6, "Iluminação e Faróis"),
    (7, "Arrefecimento e Climatização"),
    (8, "Injeção Eletrônica e Sensores"),
    (9, "Lubrificantes, Fluidos e Filtros"),
    (10, "Escapamento e Catalisadores"),
    (11, "Direção Mecânica e Hidráulica"),
    (12, "Filtros de Ar, Óleo e Combustível"),
    (13, "Rolamentos e Retentores"),
    (14, "Ignição e Velas"),
    (15, "Acessórios e Carroceria")
]

FILIAIS = [
    (1, "Matriz São Paulo", "SP"),
    (2, "Filial Curitiba", "PR"),
    (3, "Filial Belo Horizonte", "MG"),
    (4, "Filial Goiânia", "GO"),
    (5, "Filial Recife", "PE")
]

PRIMEIROS_NOMES = [
    "Carlos", "Ana", "Roberto", "Juliana", "Fernando", "Mariana", "Lucas",
    "Patricia", "Marcos", "Fernanda", "Rodrigo", "Camila", "Eduardo", "Beatriz",
    "Gabriel", "Larissa", "Alexandre", "Bruna", "Marcelo", "Renata", "Thiago",
    "Vanessa", "Felipe", "Aline", "Gustavo", "Carolina", "Diego", "Amanda",
    "Leonardo", "Priscila"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha",
    "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado",
    "Mendes", "Freitas"
]


def generate_categories() -> pd.DataFrame:
    """Gera o DataFrame de dim_categoria."""
    return pd.DataFrame(CATEGORIAS, columns=["id_categoria", "descricao"])


def generate_branches() -> pd.DataFrame:
    """Gera o DataFrame de dim_filial."""
    return pd.DataFrame(FILIAIS, columns=["id_filial", "descricao", "uf"])


def generate_salespeople(seed: int = 42) -> pd.DataFrame:
    """Gera o DataFrame de dim_vendedor com 30 vendedores alocados nas 5 filiais."""
    rng = np.random.default_rng(seed)
    vendedores = []
    
    # 30 vendedores distribuídos (ex: 6 por filial)
    for i in range(1, 31):
        nome = f"{PRIMEIROS_NOMES[(i - 1) % len(PRIMEIROS_NOMES)]} {SOBRENOMES[(i * 3) % len(SOBRENOMES)]}"
        # Distribui equilibradamente entre as filiais (1 a 5)
        id_filial = ((i - 1) % len(FILIAIS)) + 1
        vendedores.append({
            "id_vendedor": i,
            "descricao": f"Vendedor {nome}",
            "id_filial": id_filial
        })
        
    return pd.DataFrame(vendedores)

