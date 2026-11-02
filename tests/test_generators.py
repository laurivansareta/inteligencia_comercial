import pytest
import pandas as pd
from datetime import date
from data.generators.company import generate_categories, generate_branches, generate_salespeople
from data.generators.products import generate_products
from data.generators.customers import generate_customers
from data.generators.sales import generate_sales_chunks
from data.generators.payments import generate_payments_from_sales


def test_generate_categories():
    df = generate_categories()
    assert len(df) == 15
    assert set(df.columns) == {"id_categoria", "descricao"}
    assert df["id_categoria"].is_unique


def test_generate_branches():
    df = generate_branches()
    assert len(df) == 5
    assert set(df.columns) == {"id_filial", "descricao", "uf"}
    assert df["id_filial"].is_unique


def test_generate_salespeople():
    df = generate_salespeople(seed=42)
    assert len(df) == 30
    assert set(df["id_filial"].unique()).issubset({1, 2, 3, 4, 5})
    # Determinismo
    df2 = generate_salespeople(seed=42)
    pd.testing.assert_frame_equal(df, df2)


def test_generate_products():
    n_prods = 100
    df = generate_products(n_products=n_prods, seed=42)
    assert len(df) == n_prods
    assert (df["preco_lista"] > 0).all()
    assert (df["margem_referencia"] >= 0.15).all()
    assert (df["margem_referencia"] <= 0.45).all()
    assert df["id_categoria"].between(1, 15).all()


def test_generate_customers():
    df_vend = generate_salespeople(seed=42)
    df_cli, df_perfis = generate_customers(n_customers=50, salespeople_df=df_vend, seed=42)
    
    assert len(df_cli) == 50
    assert len(df_perfis) == 50
    # Validação de nomes fictícios
    assert all("Cliente Demonstração" in nome for nome in df_cli["nome_fantasia"])
    # Nenhuma feature de perfil vazada para dim_cliente
    assert "perfil_comportamental" not in df_cli.columns
    assert set(df_cli["id_filial"].unique()).issubset({1, 2, 3, 4, 5})
    assert set(df_cli["id_vendedor"].unique()).issubset(set(df_vend["id_vendedor"]))


def test_generate_payments_rules():
    sales_mock = pd.DataFrame([
        {
            "id_venda": 1,
            "id_cliente": 10,
            "data_venda": date(2025, 1, 15),
            "valor_liquido": 450.00
        },
        {
            "id_venda": 2,
            "id_cliente": 11,
            "data_venda": date(2026, 10, 20),
            "valor_liquido": 1200.50
        }
    ])
    
    df_pag = generate_payments_from_sales(sales_mock, current_date=date(2026, 10, 31), seed=42)
    assert len(df_pag) == 2
    for _, row in df_pag.iterrows():
        assert row["data_vencimento"] >= row["data_emissao"]
        if row["data_pagamento"] is not None:
            assert row["data_pagamento"] >= row["data_emissao"]
            assert row["valor_pago"] >= 0
        else:
            assert row["fl_pago"] is False
            assert row["valor_pago"] == 0.00

