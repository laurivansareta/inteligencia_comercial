"""
Conector para ERP Existente (Flex Smart):
Permite extrair dados reais do ERP tanto via REST API quanto via conexão
direta ao banco de dados do ERP (ex: PostgreSQL local 'postgres'/'flexsmart'),
transformando e mapeando para o schema padrão do CYCLE AI para fins de validação.
"""

import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class FlexSmartERPConnector:
    """Conector para integração e extração de dados do ERP Flex Smart."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        db_host: Optional[str] = None,
        db_port: Optional[str] = None,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None
    ):
        self.api_url = (api_url or os.getenv("ERP_API_URL", "https://apihomolog.impartsautomotiva.com.br:9190")).rstrip("/")
        self.username = username or os.getenv("ERP_API_USERNAME", "alisson")
        self.password = password or os.getenv("ERP_API_PASSWORD", "123456")
        self.token = token or os.getenv("ERP_API_TOKEN", "")
        
        # Parâmetros de conexão direta com o banco do ERP (se disponível)
        self.db_host = db_host or os.getenv("DB_HOST", "localhost")
        self.db_port = db_port or os.getenv("DB_PORT", "5432")
        self.db_name = db_name or "postgres"  # Banco onde residem tabelas pedidos/produtos do ERP
        self.db_user = db_user or os.getenv("DB_USER", "postgres")
        self.db_password = db_password or os.getenv("DB_PASSWORD", "postgres")
        
    def authenticate_api(self) -> bool:
        """Autentica na API REST do ERP Flex Smart e obtém o token de acesso."""
        if self.token:
            return True
            
        endpoint = f"{self.api_url}/api/auth/login"
        payload = {
            "usuario": self.username,
            "senha": self.password
        }
        
        try:
            resp = requests.post(endpoint, json=payload, timeout=10, verify=False)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token") or data.get("token") or ""
                return bool(self.token)
            else:
                # Tenta formato alternativo de login
                alt_endpoint = f"{self.api_url}/login"
                alt_resp = requests.post(alt_endpoint, json={"username": self.username, "password": self.password}, timeout=10, verify=False)
                if alt_resp.status_code == 200:
                    data = alt_resp.json()
                    self.token = data.get("access_token") or data.get("token") or ""
                    return bool(self.token)
        except Exception as e:
            print(f"[Aviso] Falha ao conectar na API REST ({self.api_url}): {e}")
            
        return False
        
    def fetch_from_database(self) -> Dict[str, pd.DataFrame]:
        """
        Extrai clientes, produtos e pedidos diretamente das tabelas do ERP existentes
        no PostgreSQL (ex: pedidos, pedido_itens, produtos).
        """
        from sqlalchemy import create_engine
        try:
            db_uri = f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            engine = create_engine(db_uri)
            
            # 1. Carregar produtos
            df_prods = pd.read_sql("SELECT * FROM produtos", engine)
            
            # 2. Carregar pedidos
            df_pedidos = pd.read_sql("SELECT * FROM pedidos", engine)
            
            # 3. Carregar itens dos pedidos
            df_itens = pd.read_sql("SELECT * FROM pedido_itens", engine)
            
            engine.dispose()
            
            return {
                "produtos": df_prods,
                "pedidos": df_pedidos,
                "itens": df_itens
            }
        except Exception as e:
            print(f"[Aviso] Não foi possível carregar diretamente do banco '{self.db_name}': {e}")
            return {}
            
    def map_to_cycle_ai(self, erp_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Mapeia os dados extraídos do ERP para o formato canônico de dimensões e fatos do CYCLE AI:
        - dim_categoria
        - dim_produto
        - dim_cliente
        - fato_venda
        - fato_pagamento
        """
        df_erp_prods = erp_data.get("produtos", pd.DataFrame())
        df_erp_pedidos = erp_data.get("pedidos", pd.DataFrame())
        df_erp_itens = erp_data.get("itens", pd.DataFrame())
        
        # Mapeamento de categorias únicas
        if not df_erp_prods.empty and "categoria" in df_erp_prods.columns:
            cat_names = df_erp_prods["categoria"].dropna().unique().tolist()
            dim_cat = pd.DataFrame([
                {"id_categoria": idx + 1, "descricao": cat}
                for idx, cat in enumerate(cat_names)
            ])
            cat_map = dict(zip(dim_cat["descricao"], dim_cat["id_categoria"]))
        else:
            dim_cat = pd.DataFrame([{"id_categoria": 1, "descricao": "Geral"}])
            cat_map = {}
            
        # Mapeamento de produtos
        mapped_prods = []
        if not df_erp_prods.empty:
            for _, row in df_erp_prods.iterrows():
                p_id = int(row.get("id", 1))
                desc = str(row.get("nome") or row.get("codigo") or f"Produto {p_id}")
                cat = row.get("categoria", "")
                cat_id = cat_map.get(cat, 1)
                preco = float(row.get("preco", 10.0))
                mapped_prods.append({
                    "id_produto": p_id,
                    "descricao": desc,
                    "id_categoria": cat_id,
                    "preco_lista": round(preco, 2),
                    "margem_referencia": 0.2500
                })
        dim_prod = pd.DataFrame(mapped_prods)
        
        # Mapeamento de clientes a partir de pedidos
        mapped_clientes = []
        cliente_map = {}
        if not df_erp_pedidos.empty and "cliente_nome" in df_erp_pedidos.columns:
            unique_clientes = df_erp_pedidos["cliente_nome"].dropna().unique()
            for idx, c_nome in enumerate(unique_clientes, 1):
                cliente_map[c_nome] = idx
                mapped_clientes.append({
                    "id_cliente": idx,
                    "nome_fantasia": c_nome,
                    "tipo_cliente": "Oficina Mecânica",
                    "porte": "Médio",
                    "uf": "SP",
                    "id_filial": 1,
                    "id_vendedor": 1,
                    "data_cadastro": date(2024, 1, 1),
                    "fl_ativo": True
                })
        dim_cli = pd.DataFrame(mapped_clientes)
        
        # Mapeamento de vendas e pagamentos
        mapped_vendas = []
        mapped_pagamentos = []
        
        if not df_erp_pedidos.empty and not df_erp_itens.empty:
            merged = df_erp_itens.merge(df_erp_pedidos, left_on="pedido_id", right_on="id", suffixes=("_item", "_ped"))
            for idx, row in merged.iterrows():
                v_id = int(row.get("id_item", idx + 1))
                c_nome = row.get("cliente_nome", "")
                c_id = cliente_map.get(c_nome, 1)
                p_id = int(row.get("produto_id", 1))
                qtd = float(row.get("quantidade", 1))
                preco_un = float(row.get("preco_unitario", 10.0))
                val_liq = round(float(row.get("subtotal", qtd * preco_un)), 2)
                val_bruto = val_liq
                val_desc = 0.00
                margem_val = round(val_liq * 0.25, 2)
                
                dt_raw = row.get("criado_em")
                if isinstance(dt_raw, (datetime, pd.Timestamp)):
                    dt_venda = dt_raw.date()
                else:
                    dt_venda = date.today()
                    
                mapped_vendas.append({
                    "id_venda": v_id,
                    "id_cliente": c_id,
                    "id_produto": p_id,
                    "id_vendedor": 1,
                    "id_filial": 1,
                    "data_venda": dt_venda,
                    "quantidade": qtd,
                    "valor_bruto": val_bruto,
                    "valor_desconto": val_desc,
                    "valor_liquido": val_liq,
                    "margem_valor": margem_val
                })
                
                mapped_pagamentos.append({
                    "id_pagamento": v_id,
                    "id_cliente": c_id,
                    "id_venda": v_id,
                    "data_emissao": dt_venda,
                    "data_vencimento": dt_venda,
                    "data_pagamento": dt_venda,
                    "valor_titulo": val_liq,
                    "valor_pago": val_liq,
                    "dias_atraso": 0,
                    "fl_pago": True
                })
                
        df_vendas = pd.DataFrame(mapped_vendas)
        df_pagamentos = pd.DataFrame(mapped_pagamentos)
        
        return {
            "dim_categoria": dim_cat,
            "dim_produto": dim_prod,
            "dim_cliente": dim_cli,
            "fato_venda": df_vendas,
            "fato_pagamento": df_pagamentos
        }
