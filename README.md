# CYCLE AI — Inteligência Comercial (Fase 1: Data Foundation)

Plataforma B2B SaaS de Customer Intelligence para distribuidoras e atacadistas, transformando dados comerciais e financeiros em decisões orientadas por dados e preditivas.

---

## 1. Status do Projeto

- [x] **Fase 1 — Data Foundation**: 100% Concluída e Validada.
- [x] **Fase 2 — Machine Learning**: 100% Concluída e Validada (3 modelos treinados e persistidos).
- [ ] **Fase 3 — Backend e Interface**: Próxima etapa (FastAPI + Streamlit).
- [ ] **Fase 4 — Qualidade e Apresentação**: Demonstração executiva.

---

## 2. Estrutura de Arquivos Implementada

```text
inteligencia_comercial/
├── data/
│   ├── generators/
│   │   ├── company.py          # Categorias (15), Filiais (5), Vendedores (30)
│   │   ├── products.py         # SKUs (1.500) com preços e margens realistas
│   │   ├── customers.py        # 10.000 clientes com 6 perfis comportamentais
│   │   ├── sales.py            # Fato Venda (36 meses, tendências e ruído)
│   │   └── payments.py         # Fato Pagamento (prazos, atrasos e inadimplência)
│   └── connectors/
│       └── erp_flex.py         # Conector ERP Flex Smart (REST API e Banco PostgreSQL)
├── database/
│   ├── schema.sql              # DDL oficial do PostgreSQL 16 com restrições e índices
│   └── connection.py           # Gerenciador de conexão SQLAlchemy e psycopg2
├── ml/
│   └── features/
│       ├── aggregations.py     # Agregações mensais (fato_cliente_mes)
│       └── snapshots.py        # Snapshots históricos (ml_cliente_snapshot) sem vazamento
├── scripts/
│   ├── generate_data.py        # Pipeline de geração e carga com seed fixa
│   ├── load_data.py            # Operações de carga em lote e limpeza idempotente
│   ├── import_erp_data.py      # Importação e mapeamento de dados reais do ERP
│   └── validate_data.py        # Bateria de testes de integridade e reconciliação
├── tests/
│   ├── test_generators.py      # Testes unitários dos geradores
│   └── test_data_consistency.py# Testes automatizados de consistência e reconciliação
├── docker-compose.yml          # Container PostgreSQL 16
├── requirements.txt            # Dependências Python fixadas
├── .env.example                # Template de configuração
├── .env                        # Configurações do ambiente local
├── context.md                  # Especificação oficial do produto
└── README.md                   # Documentação do projeto
```

---

## 3. Pré-requisitos e Ambiente

- **Python**: 3.12 ou 3.13 (ambiente virtual `.venv`).
- **PostgreSQL**: Versão 16 ativa (porta 5432) com banco `cycle_ai`.
- **Docker** (opcional): Disponível via `docker-compose.yml`.

---

## 4. Guia Rápido de Execução

### 4.1 Configurar o Ambiente Virtual e Dependências
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 4.2 Configurar o Banco de Dados
Copie `.env.example` para `.env` e confirme os dados de conexão do PostgreSQL:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cycle_ai
DB_USER=postgres
DB_PASSWORD=postgres
RANDOM_SEED=42
```

O schema é aplicado automaticamente ou via psql:
```powershell
psql -U postgres -h localhost -d cycle_ai -f database/schema.sql
```

### 4.3 Gerar Base Sintética e Snapshots de Machine Learning
Para testes rápidos (1.000 clientes, 300 produtos):
```powershell
.\.venv\Scripts\python scripts/generate_data.py --test-mode
```

Para geração em volume completo (10.000 clientes, 1.500 produtos, 36 meses):
```powershell
.\.venv\Scripts\python scripts/generate_data.py --n-customers 10000 --n-products 1500 --seed 42
```

### 4.4 Validar Consistência e Reconciliação dos Dados
```powershell
.\.venv\Scripts\python scripts/validate_data.py
```
Ou executar toda a suíte de testes do `pytest`:
```powershell
.\.venv\Scripts\pytest -v
```

### 4.5 Integração e Validação com Dados Reais do ERP Existente
Para testar a extração e mapeamento do ERP Flex Smart:
```powershell
.\.venv\Scripts\python scripts/import_erp_data.py --mode auto
```

### 4.6 Treinamento dos Modelos de Machine Learning (Fase 2)
Para treinar os 3 modelos de forma orquestrada com divisão temporal:
```powershell
.\.venv\Scripts\python scripts/train_all.py
```
Ou individualmente por modelo:
```powershell
.\.venv\Scripts\python ml/segmentation/train.py
.\.venv\Scripts\python ml/churn/train.py
.\.venv\Scripts\python ml/growth/train.py
```

---

## 5. Garantias de Qualidade e Critérios de Aceite Atendidos

1. **Reconciliação Financeira Estrita**:
   - `SUM(fato_venda.valor_liquido) == SUM(fato_cliente_mes.faturamento)` (diferença R$ 0,00).
   - `SUM(fato_venda.valor_liquido) == SUM(fato_pagamento.valor_titulo)` (diferença R$ 0,00).
2. **Integridade Referencial**: 100% das chaves estrangeiras válidas, 0 órfãos.
3. **Regras Temporais e Anti-Leakage**:
   - Features calculadas exclusivamente com histórico anterior ou igual à data de referência.
   - Labels futuros calculados exclusivamente na janela posterior de 90 dias.
   - Ponto de referência mais recente sem janela completa (ex: 31/10/2026) possui labels estritamente `NULL` para inferência sem vazamento temporal.
4. **Reprodutibilidade**: Geração baseada em seed fixa (`RANDOM_SEED=42`).

