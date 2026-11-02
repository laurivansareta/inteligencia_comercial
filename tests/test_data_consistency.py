import pytest
from database.connection import get_connection


def test_database_connection():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    res = cur.fetchone()
    conn.close()
    assert res[0] == 1


def test_schema_tables_exist():
    expected_tables = {
        "dim_categoria", "dim_filial", "dim_vendedor", "dim_produto",
        "dim_cliente", "fato_venda", "fato_pagamento", "fato_cliente_mes",
        "ml_cliente_snapshot"
    }
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    existing_tables = {row[0] for row in cur.fetchall()}
    conn.close()
    assert expected_tables.issubset(existing_tables)


def test_financial_reconciliation():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ROUND(SUM(valor_liquido), 2) FROM fato_venda;")
    tot_venda = cur.fetchone()[0] or 0.00
    
    cur.execute("SELECT ROUND(SUM(faturamento), 2) FROM fato_cliente_mes;")
    tot_mes = cur.fetchone()[0] or 0.00
    
    cur.execute("SELECT ROUND(SUM(valor_titulo), 2) FROM fato_pagamento;")
    tot_pag = cur.fetchone()[0] or 0.00
    conn.close()
    
    assert abs(float(tot_venda) - float(tot_mes)) < 0.05
    assert abs(float(tot_venda) - float(tot_pag)) < 0.05


def test_zero_foreign_key_orphans():
    conn = get_connection()
    cur = conn.cursor()
    queries = [
        "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_cliente c ON v.id_cliente = c.id_cliente WHERE c.id_cliente IS NULL",
        "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_produto p ON v.id_produto = p.id_produto WHERE p.id_produto IS NULL",
        "SELECT COUNT(*) FROM fato_pagamento p LEFT JOIN fato_venda v ON p.id_venda = v.id_venda WHERE v.id_venda IS NULL"
    ]
    for q in queries:
        cur.execute(q)
        assert cur.fetchone()[0] == 0
    conn.close()


def test_no_temporal_leakage_in_latest_snapshot():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM ml_cliente_snapshot 
        WHERE data_referencia = (SELECT MAX(data_referencia) FROM ml_cliente_snapshot)
          AND churn_label_90d IS NOT NULL;
    """)
    leakage = cur.fetchone()[0]
    conn.close()
    assert leakage == 0

