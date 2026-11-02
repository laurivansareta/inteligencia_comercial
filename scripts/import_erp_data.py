"""
Script de importação e validação de dados reais do ERP Flex Smart para o CYCLE AI:
- Conecta ao ERP via REST API ou via banco PostgreSQL existente ('postgres' / 'flexsmart')
- Mapeia as entidades do ERP para o schema canônico do CYCLE AI
- Valida consistência e opcionalmente carrega na base de validação
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
from data.connectors.erp_flex import FlexSmartERPConnector
from scripts.load_data import bulk_insert_dataframe


def run_erp_import(mode: str = "database", load_to_db: bool = False):
    print("=" * 70)
    print("CYCLE AI - Conector e Validador de Dados do ERP Flex Smart")
    print(f"Modo: {mode} | Carregar no Banco: {load_to_db}")
    print("=" * 70)
    
    connector = FlexSmartERPConnector()
    
    erp_data = {}
    if mode in ["database", "auto"]:
        print("\n1. Tentando extração direta das tabelas do ERP no PostgreSQL...")
        erp_data = connector.fetch_from_database()
        if erp_data and not erp_data.get("produtos", None) is None:
            n_p = len(erp_data.get("produtos", []))
            n_ped = len(erp_data.get("pedidos", []))
            n_it = len(erp_data.get("itens", []))
            print(f"   [OK] Encontrados no ERP: {n_p} produtos, {n_ped} pedidos, {n_it} itens.")
            
    if (not erp_data or erp_data.get("produtos", None) is None or erp_data["produtos"].empty) and mode in ["api", "auto"]:
        print("\n2. Tentando autenticação e consulta via API REST do ERP Flex Smart...")
        auth_ok = connector.authenticate_api()
        if auth_ok:
            print("   [OK] Autenticação na API REST concluída com sucesso.")
        else:
            print("   [AVISO] API REST indisponível ou credenciais inválidas.")
            
    if not erp_data or (erp_data.get("produtos", None) is not None and erp_data["produtos"].empty):
        print("\n[Status] Nenhuma tabela ou registro ativo encontrado no ERP para importação imediata.")
        print("         O conector está pronto para consumo quando houver dados transacionais na base do ERP.")
        return
        
    print("\n3. Mapeando dados do ERP para o modelo relacional do CYCLE AI...")
    mapped = connector.map_to_cycle_ai(erp_data)
    
    for table_name, df in mapped.items():
        print(f"   - {table_name}: {len(df)} registros preparados.")
        
    if load_to_db:
        print("\n4. Carregando dados mapeados no banco cycle_ai...")
        for table_name, df in mapped.items():
            if not df.empty:
                n = bulk_insert_dataframe(table_name, df)
                print(f"   [OK] Inseridos em {table_name}: {n} registros.")
        print("\nCarga de validação do ERP concluída com sucesso!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importação e validação de dados do ERP Flex Smart")
    parser.add_argument("--mode", choices=["database", "api", "auto"], default="database", help="Fonte de extração")
    parser.add_argument("--load", action="store_true", help="Carrega os dados mapeados na base cycle_ai")
    args = parser.parse_args()
    
    run_erp_import(mode=args.mode, load_to_db=args.load)
