"""
Script principal de geração e carga de dados sintéticos do CYCLE AI:
- Parametrizável por linha de comando
- Seed fixa configurável para 100% de reprodutibilidade
- Executa a carga das dimensões, fatos, agregações mensais e snapshots históricos
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
import time
from datetime import date
from data.generators.company import generate_categories, generate_branches, generate_salespeople
from data.generators.products import generate_products
from data.generators.customers import generate_customers
from data.generators.sales import generate_sales_chunks
from data.generators.payments import generate_payments_from_sales
from scripts.load_data import bulk_insert_dataframe, clean_tables
from ml.features.aggregations import build_monthly_aggregations
from ml.features.snapshots import generate_all_snapshots


def run_pipeline(
    n_customers: int = 10000,
    n_products: int = 1500,
    seed: int = 42,
    clean: bool = True,
    generate_snapshots: bool = True
):
    print("=" * 70)
    print("CYCLE AI - Pipeline de Geração e Carga de Dados Sintéticos (Fase 1)")
    print(f"Parâmetros: {n_customers} clientes | {n_products} produtos | seed={seed}")
    print("=" * 70)
    
    t0 = time.time()
    
    if clean:
        print("\n1. Limpando tabelas existentes...")
        clean_tables()
        
    print("\n2. Gerando dimensões organizacionais (categorias, filiais, vendedores)...")
    df_cat = generate_categories()
    bulk_insert_dataframe("dim_categoria", df_cat)
    print(f"   [OK] dim_categoria: {len(df_cat)} registros.")
    
    df_fil = generate_branches()
    bulk_insert_dataframe("dim_filial", df_fil)
    print(f"   [OK] dim_filial: {len(df_fil)} registros.")
    
    df_vend = generate_salespeople(seed=seed)
    bulk_insert_dataframe("dim_vendedor", df_vend)
    print(f"   [OK] dim_vendedor: {len(df_vend)} registros.")
    
    print("\n3. Gerando dim_produto...")
    df_prod = generate_products(n_products=n_products, seed=seed)
    bulk_insert_dataframe("dim_produto", df_prod)
    print(f"   [OK] dim_produto: {len(df_prod)} registros.")
    
    print("\n4. Gerando dim_cliente e perfis comportamentais...")
    df_cli, df_perfis = generate_customers(
        n_customers=n_customers,
        salespeople_df=df_vend,
        seed=seed,
        base_date=date(2026, 10, 31)
    )
    bulk_insert_dataframe("dim_cliente", df_cli)
    print(f"   [OK] dim_cliente: {len(df_cli)} registros.")
    
    print("\n5. Gerando histórico transacional (36 meses) para fato_venda e fato_pagamento...")
    total_vendas = 0
    total_pagamentos = 0
    
    chunk_generator = generate_sales_chunks(
        customers_df=df_cli,
        profiles_df=df_perfis,
        products_df=df_prod,
        salespeople_df=df_vend,
        start_date=date(2023, 11, 1),
        end_date=date(2026, 10, 31),
        seed=seed,
        chunk_size_customers=1000
    )
    
    chunk_num = 1
    for sales_chunk in chunk_generator:
        # Inserir vendas
        n_v = bulk_insert_dataframe("fato_venda", sales_chunk, batch_size=5000)
        total_vendas += n_v
        
        # Gerar e inserir pagamentos correspondentes
        payments_chunk = generate_payments_from_sales(
            sales_df=sales_chunk,
            profiles_df=df_perfis,
            current_date=date(2026, 10, 31),
            seed=seed + chunk_num
        )
        n_p = bulk_insert_dataframe("fato_pagamento", payments_chunk, batch_size=5000)
        total_pagamentos += n_p
        
        print(f"   Lote {chunk_num}: +{n_v} vendas e +{n_p} pagamentos inseridos.")
        chunk_num += 1
        
    print(f"   [OK] Total em fato_venda: {total_vendas} registros.")
    print(f"   [OK] Total em fato_pagamento: {total_pagamentos} registros.")
    
    print("\n6. Calculando agregações mensais (fato_cliente_mes)...")
    n_mes = build_monthly_aggregations()
    print(f"   [OK] fato_cliente_mes: {n_mes} registros agregados.")
    
    if generate_snapshots:
        print("\n7. Gerando snapshots históricos para Machine Learning (ml_cliente_snapshot)...")
        results = generate_all_snapshots()
        total_snapshots = sum(results.values())
        print(f"   [OK] Total de snapshots gerados: {total_snapshots} registros.")
        
    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"Pipeline concluído com sucesso em {elapsed:.2f} segundos!")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Geração de Dados Sintéticos - CYCLE AI")
    parser.add_argument("--n-customers", type=int, default=10000, help="Quantidade de clientes")
    parser.add_argument("--n-products", type=int, default=1500, help="Quantidade de produtos")
    parser.add_argument("--seed", type=int, default=42, help="Seed para reprodução")
    parser.add_argument("--test-mode", action="store_true", help="Executa com volume reduzido para testes rápidos")
    parser.add_argument("--no-clean", action="store_true", help="Não limpa o banco antes de inserir")
    parser.add_argument("--skip-snapshots", action="store_true", help="Não gera os snapshots de ML")
    
    args = parser.parse_args()
    
    if args.test_mode:
        n_cust = 1000
        n_prod = 300
    else:
        n_cust = args.n_customers
        n_prod = args.n_products
        
    run_pipeline(
        n_customers=n_cust,
        n_products=n_prod,
        seed=args.seed,
        clean=not args.no_clean,
        generate_snapshots=not args.skip_snapshots
    )
