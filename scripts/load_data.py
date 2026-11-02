"""
Módulo de carga de dados em lote no PostgreSQL:
Utiliza psycopg2.extras.execute_values para máxima velocidade e transações atômicas.
"""

import pandas as pd
from psycopg2.extras import execute_values
from database.connection import get_connection


def bulk_insert_dataframe(table_name: str, df: pd.DataFrame, batch_size: int = 5000):
    """
    Insere um DataFrame em lote no PostgreSQL de forma eficiente.
    """
    if df.empty:
        return 0
        
    columns = list(df.columns)
    cols_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table_name} ({cols_str}) VALUES %s ON CONFLICT DO NOTHING;"
    
    # Converter registros para lista de tuplas tratando valores nulos e NaNs
    records = df.where(pd.notnull(df), None).values.tolist()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records, page_size=batch_size)
        conn.commit()
        return len(records)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def clean_tables(cascade: bool = True):
    """
    Limpa as tabelas da base de dados de forma segura e idempotente.
    """
    tables = [
        "ml_cliente_snapshot",
        "fato_cliente_mes",
        "fato_pagamento",
        "fato_venda",
        "dim_produto",
        "dim_cliente",
        "dim_vendedor",
        "dim_filial",
        "dim_categoria"
    ]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for t in tables:
                cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
        conn.commit()
        print("Tabelas limpas com sucesso.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

