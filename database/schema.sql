-- =============================================================================
-- CYCLE AI - Data Foundation Schema (PostgreSQL 16)
-- Especificação oficial conforme context.md
-- =============================================================================

-- Habilitar extensões úteis se disponíveis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. Dimensões Organizacionais e Cadastrais
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_categoria (
    id_categoria INTEGER PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_filial (
    id_filial INTEGER PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_vendedor (
    id_vendedor INTEGER PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL,
    id_filial INTEGER NOT NULL REFERENCES dim_filial(id_filial)
);

CREATE TABLE IF NOT EXISTS dim_cliente (
    id_cliente BIGINT PRIMARY KEY,
    nome_fantasia VARCHAR(150) NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL,
    porte VARCHAR(50) NOT NULL,
    uf CHAR(2) NOT NULL,
    id_filial INTEGER NOT NULL REFERENCES dim_filial(id_filial),
    id_vendedor INTEGER NOT NULL REFERENCES dim_vendedor(id_vendedor),
    data_cadastro DATE NOT NULL,
    fl_ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_produto (
    id_produto BIGINT PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    id_categoria INTEGER NOT NULL REFERENCES dim_categoria(id_categoria),
    preco_lista NUMERIC(14,2) NOT NULL CHECK (preco_lista >= 0),
    margem_referencia NUMERIC(8,4) NOT NULL CHECK (margem_referencia >= 0 AND margem_referencia <= 1)
);

-- -----------------------------------------------------------------------------
-- 2. Fatos Transacionais (Vendas e Pagamentos)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fato_venda (
    id_venda BIGINT PRIMARY KEY,
    id_cliente BIGINT NOT NULL REFERENCES dim_cliente(id_cliente),
    id_produto BIGINT NOT NULL REFERENCES dim_produto(id_produto),
    id_vendedor INTEGER NOT NULL REFERENCES dim_vendedor(id_vendedor),
    id_filial INTEGER NOT NULL REFERENCES dim_filial(id_filial),
    data_venda DATE NOT NULL,
    quantidade NUMERIC(14,3) NOT NULL CHECK (quantidade > 0),
    valor_bruto NUMERIC(14,2) NOT NULL CHECK (valor_bruto >= 0),
    valor_desconto NUMERIC(14,2) NOT NULL DEFAULT 0.00 CHECK (valor_desconto >= 0),
    valor_liquido NUMERIC(14,2) NOT NULL CHECK (valor_liquido >= 0),
    margem_valor NUMERIC(14,2) NOT NULL,
    CONSTRAINT chk_fato_venda_liquido CHECK (valor_liquido <= valor_bruto)
);

CREATE INDEX IF NOT EXISTS idx_fato_venda_cliente_data ON fato_venda (id_cliente, data_venda);
CREATE INDEX IF NOT EXISTS idx_fato_venda_data ON fato_venda (data_venda);
CREATE INDEX IF NOT EXISTS idx_fato_venda_produto ON fato_venda (id_produto);
CREATE INDEX IF NOT EXISTS idx_fato_venda_vendedor ON fato_venda (id_vendedor);

CREATE TABLE IF NOT EXISTS fato_pagamento (
    id_pagamento BIGINT PRIMARY KEY,
    id_cliente BIGINT NOT NULL REFERENCES dim_cliente(id_cliente),
    id_venda BIGINT NOT NULL REFERENCES fato_venda(id_venda),
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE NULL,
    valor_titulo NUMERIC(14,2) NOT NULL CHECK (valor_titulo >= 0),
    valor_pago NUMERIC(14,2) NOT NULL DEFAULT 0.00 CHECK (valor_pago >= 0),
    dias_atraso INTEGER NOT NULL DEFAULT 0,
    fl_pago BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_pagamento_vencimento CHECK (data_vencimento >= data_emissao),
    CONSTRAINT chk_pagamento_data CHECK (data_pagamento IS NULL OR data_pagamento >= data_emissao)
);

CREATE INDEX IF NOT EXISTS idx_fato_pagamento_cliente ON fato_pagamento (id_cliente);
CREATE INDEX IF NOT EXISTS idx_fato_pagamento_venda ON fato_pagamento (id_venda);
CREATE INDEX IF NOT EXISTS idx_fato_pagamento_vencimento ON fato_pagamento (data_vencimento);

-- -----------------------------------------------------------------------------
-- 3. Fatos Agregados e Snapshots para ML
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fato_cliente_mes (
    id_cliente BIGINT NOT NULL REFERENCES dim_cliente(id_cliente),
    mes_referencia DATE NOT NULL,
    quantidade_pedidos INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_pedidos >= 0),
    faturamento NUMERIC(14,2) NOT NULL DEFAULT 0.00 CHECK (faturamento >= 0),
    ticket_medio NUMERIC(14,2) NOT NULL DEFAULT 0.00 CHECK (ticket_medio >= 0),
    quantidade_itens NUMERIC(14,3) NOT NULL DEFAULT 0.000 CHECK (quantidade_itens >= 0),
    categorias_distintas INTEGER NOT NULL DEFAULT 0 CHECK (categorias_distintas >= 0),
    margem_total NUMERIC(14,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (id_cliente, mes_referencia)
);

CREATE INDEX IF NOT EXISTS idx_fato_cliente_mes_data ON fato_cliente_mes (mes_referencia);

CREATE TABLE IF NOT EXISTS ml_cliente_snapshot (
    id_cliente BIGINT NOT NULL REFERENCES dim_cliente(id_cliente),
    data_referencia DATE NOT NULL,
    recency_days INTEGER NOT NULL CHECK (recency_days >= 0),
    frequency_30d INTEGER NOT NULL CHECK (frequency_30d >= 0),
    frequency_90d INTEGER NOT NULL CHECK (frequency_90d >= 0),
    frequency_180d INTEGER NOT NULL CHECK (frequency_180d >= 0),
    revenue_30d NUMERIC(14,2) NOT NULL CHECK (revenue_30d >= 0),
    revenue_90d NUMERIC(14,2) NOT NULL CHECK (revenue_90d >= 0),
    revenue_180d NUMERIC(14,2) NOT NULL CHECK (revenue_180d >= 0),
    revenue_365d NUMERIC(14,2) NOT NULL CHECK (revenue_365d >= 0),
    avg_ticket_90d NUMERIC(14,2) NOT NULL CHECK (avg_ticket_90d >= 0),
    revenue_variation_90d NUMERIC(10,4) NOT NULL DEFAULT 0.0000,
    frequency_variation_90d NUMERIC(10,4) NOT NULL DEFAULT 0.0000,
    avg_days_between_orders NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (avg_days_between_orders >= 0),
    category_diversity INTEGER NOT NULL CHECK (category_diversity >= 0),
    avg_payment_delay NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    late_payment_rate NUMERIC(8,4) NOT NULL DEFAULT 0.0000 CHECK (late_payment_rate >= 0 AND late_payment_rate <= 1),
    returns_rate NUMERIC(8,4) NOT NULL DEFAULT 0.0000 CHECK (returns_rate >= 0 AND returns_rate <= 1),
    churn_label_90d INTEGER NULL CHECK (churn_label_90d IN (0, 1)),
    future_revenue_90d NUMERIC(14,2) NULL CHECK (future_revenue_90d >= 0),
    feature_version VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, data_referencia)
);

CREATE INDEX IF NOT EXISTS idx_ml_snapshot_data_ref ON ml_cliente_snapshot (data_referencia);
CREATE INDEX IF NOT EXISTS idx_ml_snapshot_churn ON ml_cliente_snapshot (churn_label_90d);

