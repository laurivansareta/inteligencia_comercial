"""
Script de validação e reconciliação dos dados (CYCLE AI - Fase 1):
Executa uma bateria rigorosa de checagens de integridade referencial,
reconciliação financeira, coerência temporal e ausência de vazamento de dados.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database.connection import get_connection


def run_validations() -> bool:
    print("=" * 70)
    print("CYCLE AI - Suíte de Validação e Reconciliação dos Dados (Fase 1)")
    print("=" * 70)
    
    conn = get_connection()
    all_passed = True
    
    try:
        cur = conn.cursor()
        
        # ---------------------------------------------------------------------
        # 1. Contagens de Registros
        # ---------------------------------------------------------------------
        print("\n[1] Contagens das Tabelas:")
        tabelas = [
            "dim_categoria", "dim_filial", "dim_vendedor", "dim_produto",
            "dim_cliente", "fato_venda", "fato_pagamento", "fato_cliente_mes",
            "ml_cliente_snapshot"
        ]
        counts = {}
        for t in tabelas:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            c = cur.fetchone()[0]
            counts[t] = c
            print(f"    - {t:<22}: {c:>10,d} registros")
            
        if counts["fato_venda"] == 0:
            print("  [ERRO CRITICO] Tabela fato_venda está vazia!")
            return False
            
        # ---------------------------------------------------------------------
        # 2. Reconciliação Financeira
        # ---------------------------------------------------------------------
        print("\n[2] Reconciliação Financeira:")
        
        # 2.1 fato_venda vs fato_cliente_mes
        cur.execute("SELECT ROUND(SUM(valor_liquido), 2) FROM fato_venda;")
        total_venda = cur.fetchone()[0] or 0.00
        
        cur.execute("SELECT ROUND(SUM(faturamento), 2) FROM fato_cliente_mes;")
        total_mes = cur.fetchone()[0] or 0.00
        
        diff_mes = abs(float(total_venda) - float(total_mes))
        if diff_mes < 0.05:
            print(f"    [OK] Reconciliação fato_venda vs fato_cliente_mes: EXATA (R$ {total_venda:,.2f} vs R$ {total_mes:,.2f})")
        else:
            print(f"    [X] DIVERGÊNCIA: fato_venda (R$ {total_venda:,.2f}) != fato_cliente_mes (R$ {total_mes:,.2f})! Dif: R$ {diff_mes:.2f}")
            all_passed = False
            
        # 2.2 fato_venda vs fato_pagamento
        cur.execute("SELECT ROUND(SUM(valor_titulo), 2) FROM fato_pagamento;")
        total_titulo = cur.fetchone()[0] or 0.00
        
        diff_pag = abs(float(total_venda) - float(total_titulo))
        if diff_pag < 0.05:
            print(f"    [OK] Reconciliação fato_venda vs fato_pagamento: EXATA (R$ {total_venda:,.2f} vs R$ {total_titulo:,.2f})")
        else:
            print(f"    [X] DIVERGÊNCIA: fato_venda (R$ {total_venda:,.2f}) != fato_pagamento (R$ {total_titulo:,.2f})! Dif: R$ {diff_pag:.2f}")
            all_passed = False
            
        # ---------------------------------------------------------------------
        # 3. Integridade Referencial (Chaves Estrangeiras Órfãs)
        # ---------------------------------------------------------------------
        print("\n[3] Integridade Referencial:")
        check_fks = [
            ("Vendas com cliente inválido", "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_cliente c ON v.id_cliente = c.id_cliente WHERE c.id_cliente IS NULL"),
            ("Vendas com produto inválido", "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_produto p ON v.id_produto = p.id_produto WHERE p.id_produto IS NULL"),
            ("Vendas com vendedor inválido", "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_vendedor vd ON v.id_vendedor = vd.id_vendedor WHERE vd.id_vendedor IS NULL"),
            ("Vendas com filial inválida", "SELECT COUNT(*) FROM fato_venda v LEFT JOIN dim_filial f ON v.id_filial = f.id_filial WHERE f.id_filial IS NULL"),
            ("Pagamentos sem venda correspondente", "SELECT COUNT(*) FROM fato_pagamento p LEFT JOIN fato_venda v ON p.id_venda = v.id_venda WHERE v.id_venda IS NULL"),
            ("Produtos com categoria inválida", "SELECT COUNT(*) FROM dim_produto p LEFT JOIN dim_categoria c ON p.id_categoria = c.id_categoria WHERE c.id_categoria IS NULL"),
            ("Clientes com filial inválida", "SELECT COUNT(*) FROM dim_cliente c LEFT JOIN dim_filial f ON c.id_filial = f.id_filial WHERE f.id_filial IS NULL")
        ]
        
        for desc, sql in check_fks:
            cur.execute(sql)
            err_count = cur.fetchone()[0]
            if err_count == 0:
                print(f"    [OK] {desc}: 0 órfãos")
            else:
                print(f"    [X] {desc}: {err_count} registros órfãos encontrados!")
                all_passed = False
                
        # ---------------------------------------------------------------------
        # 4. Regras de Negócio e Coerência de Datas
        # ---------------------------------------------------------------------
        print("\n[4] Coerência de Regras de Negócio e Datas:")
        check_rules = [
            ("Vencimento anterior à emissão", "SELECT COUNT(*) FROM fato_pagamento WHERE data_vencimento < data_emissao"),
            ("Data de pagamento anterior à emissão", "SELECT COUNT(*) FROM fato_pagamento WHERE data_pagamento IS NOT NULL AND data_pagamento < data_emissao"),
            ("Título pago sem data de pagamento", "SELECT COUNT(*) FROM fato_pagamento WHERE fl_pago = TRUE AND data_pagamento IS NULL"),
            ("Título não pago com valor pago > 0", "SELECT COUNT(*) FROM fato_pagamento WHERE fl_pago = FALSE AND valor_pago > 0"),
            ("Vendas com valor líquido negativo", "SELECT COUNT(*) FROM fato_venda WHERE valor_liquido < 0"),
            ("Vendas com valor líquido > valor bruto", "SELECT COUNT(*) FROM fato_venda WHERE valor_liquido > valor_bruto"),
            ("Vendas com quantidade <= 0", "SELECT COUNT(*) FROM fato_venda WHERE quantidade <= 0")
        ]
        
        for desc, sql in check_rules:
            cur.execute(sql)
            err_count = cur.fetchone()[0]
            if err_count == 0:
                print(f"    [OK] {desc}: OK (0 inconsistências)")
            else:
                print(f"    [X] {desc}: {err_count} violações encontradas!")
                all_passed = False
                
        # ---------------------------------------------------------------------
        # 5. Cobertura Histórica Temporal (36 meses)
        # ---------------------------------------------------------------------
        print("\n[5] Cobertura Temporal:")
        cur.execute("SELECT MIN(data_venda), MAX(data_venda), COUNT(DISTINCT DATE_TRUNC('month', data_venda)) FROM fato_venda;")
        min_dt, max_dt, n_meses = cur.fetchone()
        print(f"    - Período coberto: {min_dt.strftime('%d/%m/%Y')} até {max_dt.strftime('%d/%m/%Y')}")
        print(f"    - Quantidade de meses distintos: {n_meses} meses")
        if n_meses >= 36:
            print(f"    [OK] Cobertura de 36 meses atendida.")
        else:
            print(f"    [AVISO] Quantidade de meses observada ({n_meses}) é inferior a 36 meses.")
            
        # ---------------------------------------------------------------------
        # 6. Validação dos Snapshots de Machine Learning e Vazamento Temporal
        # ---------------------------------------------------------------------
        print("\n[6] Snapshots de ML e Prevenção de Vazamento Temporal:")
        cur.execute("""
            SELECT 
                data_referencia,
                COUNT(*) AS total_snapshots,
                COUNT(churn_label_90d) AS labels_preenchidos,
                COUNT(*) - COUNT(churn_label_90d) AS labels_nulos,
                ROUND(AVG(recency_days), 1) AS media_recencia,
                ROUND(AVG(frequency_90d), 1) AS media_freq_90d,
                ROUND(AVG(revenue_90d), 2) AS media_rev_90d
            FROM ml_cliente_snapshot
            GROUP BY data_referencia
            ORDER BY data_referencia;
        """)
        snapshots_res = cur.fetchall()
        for row in snapshots_res:
            dt_ref, tot, lbl_fill, lbl_null, rec, freq, rev = row
            status_label = "Treino/Validação (com labels)" if lbl_fill > 0 else "Ponto Atual / Inferência (labels NULL)"
            print(f"    - Data {dt_ref.strftime('%d/%m/%Y')}: {tot:,d} snapshots | {status_label}")
            print(f"      Recência Média: {rec}d | Freq 90d: {freq} | Faturamento 90d: R$ {rev:,.2f}")
            
        # Verificar regra estrita: ponto atual (sem 90d futuros) DEVE ter labels nulos
        cur.execute("""
            SELECT COUNT(*) 
            FROM ml_cliente_snapshot 
            WHERE data_referencia = (SELECT MAX(data_referencia) FROM ml_cliente_snapshot)
              AND churn_label_90d IS NOT NULL;
        """)
        leakage_count = cur.fetchone()[0]
        if leakage_count == 0:
            print("    [OK] Sem vazamento temporal: último snapshot possui labels futuros estritamente NULL.")
        else:
            print(f"    [X] ALERTA DE VAZAMENTO: {leakage_count} snapshots recentes contêm labels futuros sem janela completa!")
            all_passed = False
            
        print("\n" + "=" * 70)
        if all_passed:
            print(" RESULTADO FINAL: TODOS OS CRITÉRIOS DE ACEITE DA FASE 1 FORAM ATENDIDOS!")
        else:
            print(" RESULTADO FINAL: FALHAS IDENTIFICADAS NA CONSISTÊNCIA DOS DADOS.")
        print("=" * 70)
        
        return all_passed
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_validations()
    sys.exit(0 if success else 1)
