# CYCLE AI --- Contexto do Projeto

> Documento-base para orientar a criação do CYCLE AI no Antigravity
> (desenvolvimento assistido por IA / low-code). Este arquivo é a fonte
> principal de contexto do produto. Antes de implementar qualquer
> funcionalidade, leia este documento e preserve suas decisões.

## 1. Identidade do produto

**Nome:** CYCLE AI\
**Categoria:** Plataforma B2B SaaS de Customer Intelligence\
**Tagline:** Inteligência preditiva para decisões comerciais.\
**Idioma inicial:** Português do Brasil (pt-BR).\
**Mercado inicial:** Distribuidoras, atacadistas e empresas B2B com
histórico de vendas recorrentes.\
**Empresa demonstrativa:** Distribuidora fictícia de autopeças.

### Proposta de valor

O CYCLE AI transforma dados comerciais e financeiros que as empresas já
possuem em previsões e oportunidades acionáveis. A plataforma identifica
grupos de clientes com comportamentos semelhantes, estima o risco de
abandono (churn) e prevê o potencial de crescimento de cada cliente.

**Mensagem central:** sair de uma gestão comercial reativa para uma
gestão orientada por dados e preditiva.

### Princípios do produto

1.  Mostrar informação útil para decisões, não apenas gráficos.
2.  Toda previsão deve apresentar contexto e explicação compreensível.
3.  Não apresentar resultados fictícios como se fossem resultados reais
    de modelos.
4.  Separar claramente dados demonstrativos, previsões do modelo e
    resultados observados.
5.  Priorizar uma experiência simples para gestores comerciais.
6.  Construir o MVP com arquitetura modular, preparada para integração
    futura com ERPs.
7.  Não executar ações comerciais automaticamente no MVP; apresentar
    recomendações para decisão humana.

------------------------------------------------------------------------

## 2. Objetivos do MVP

O MVP deve entregar três capacidades de Machine Learning:

1.  **Customer Segmentation:** segmentação não supervisionada de
    clientes.
2.  **Churn Prediction:** estimativa da probabilidade de um cliente
    deixar de comprar.
3.  **Growth Prediction:** previsão do faturamento futuro e
    identificação de clientes com potencial de crescimento.

Além dos modelos, o MVP deve incluir:

-   Base de dados sintética realista.
-   Banco PostgreSQL.
-   Pipeline de preparação de dados e criação de features.
-   Treinamento, avaliação e persistência dos modelos.
-   API para consulta dos resultados.
-   Dashboard interativo.
-   Protótipo navegável com identidade visual consistente.
-   Explicabilidade das previsões, especialmente para churn.
-   Documentação de instalação, execução e limitações.

### Fora do escopo do MVP

Não implementar nesta primeira versão:

-   Integrações reais com ERPs.
-   Multi-tenancy completo e cobrança SaaS.
-   Agentes autônomos que enviem mensagens ou executem ações comerciais.
-   Recomendação individual de produtos.
-   Modelos de crédito ou concessão automática de limite.
-   Aplicativo mobile nativo.
-   Infraestrutura distribuída ou Kubernetes.

Esses itens podem ser considerados em fases futuras.

------------------------------------------------------------------------

## 3. Público-alvo e personas

### Persona principal --- Gestor comercial

Precisa entender a saúde da carteira, priorizar clientes e identificar
riscos e oportunidades sem analisar manualmente milhares de registros.

### Persona secundária --- Diretor ou proprietário

Precisa acompanhar indicadores consolidados, evolução da carteira,
riscos de perda de receita e oportunidades de crescimento.

### Persona operacional --- Vendedor

Precisa receber uma lista priorizada de clientes para contato,
acompanhada de uma justificativa simples.

------------------------------------------------------------------------

## 4. Cenário de dados sintéticos

Todos os dados da demonstração devem ser sintéticos. Não utilizar dados
pessoais ou comerciais reais.

### Empresa fictícia

Uma distribuidora de autopeças com as seguintes características
iniciais:

  Elemento                   Volume inicial
  ------------------------ ----------------
  Clientes                           10.000
  Produtos / SKUs                     1.500
  Categorias de produtos                 15
  Filiais                                 5
  Vendedores                             30
  Histórico transacional           36 meses

Os volumes podem ser ajustados para manter bom desempenho no ambiente
local, mas a geração deve ser parametrizável.

### Perfis comportamentais para geração

Criar uma mistura de perfis com diferenças estatísticas, ruído e
sobreposição:

-   Estratégico: alto faturamento, frequência e diversidade de
    categorias.
-   Recorrente: compras regulares e ticket relativamente estável.
-   Em crescimento: aumento progressivo de frequência ou faturamento.
-   Sazonal: demanda concentrada em determinados períodos.
-   Em retração: queda gradual de frequência e faturamento.
-   Baixo engajamento/inativo: intervalos longos entre compras.

**Importante:** os perfis usados pelo gerador não podem ser fornecidos
diretamente como variáveis explicativas aos modelos. Os algoritmos devem
aprender a partir das características observáveis. Evitar dados
excessivamente perfeitos ou separáveis.

### Tabelas relacionais previstas

#### `dim_cliente`

Campos sugeridos:

-   `id_cliente` BIGINT PRIMARY KEY
-   `nome_fantasia` VARCHAR
-   `tipo_cliente` VARCHAR
-   `porte` VARCHAR
-   `uf` CHAR(2)
-   `id_filial` INTEGER
-   `id_vendedor` INTEGER
-   `data_cadastro` DATE
-   `fl_ativo` BOOLEAN

Usar nomes claramente fictícios, como "Cliente Demonstração 00001". Não
gerar CPF, CNPJ, telefone ou endereço realista que possa coincidir com
dados pessoais reais.

#### `dim_produto`

-   `id_produto` BIGINT PRIMARY KEY
-   `descricao` VARCHAR
-   `id_categoria` INTEGER
-   `preco_lista` NUMERIC(14,2)
-   `margem_referencia` NUMERIC(8,4)

#### `dim_categoria`

-   `id_categoria` INTEGER PRIMARY KEY
-   `descricao` VARCHAR

#### `dim_filial`

-   `id_filial` INTEGER PRIMARY KEY
-   `descricao` VARCHAR
-   `uf` CHAR(2)

#### `dim_vendedor`

-   `id_vendedor` INTEGER PRIMARY KEY
-   `descricao` VARCHAR
-   `id_filial` INTEGER

#### `fato_venda`

-   `id_venda` BIGINT PRIMARY KEY
-   `id_cliente` BIGINT
-   `id_produto` BIGINT
-   `id_vendedor` INTEGER
-   `id_filial` INTEGER
-   `data_venda` DATE
-   `quantidade` NUMERIC(14,3)
-   `valor_bruto` NUMERIC(14,2)
-   `valor_desconto` NUMERIC(14,2)
-   `valor_liquido` NUMERIC(14,2)
-   `margem_valor` NUMERIC(14,2)

#### `fato_pagamento`

-   `id_pagamento` BIGINT PRIMARY KEY
-   `id_cliente` BIGINT
-   `id_venda` BIGINT
-   `data_emissao` DATE
-   `data_vencimento` DATE
-   `data_pagamento` DATE NULL
-   `valor_titulo` NUMERIC(14,2)
-   `valor_pago` NUMERIC(14,2)
-   `dias_atraso` INTEGER
-   `fl_pago` BOOLEAN

#### `fato_cliente_mes`

Agregação mensal derivada das transações:

-   `id_cliente` BIGINT
-   `mes_referencia` DATE
-   `quantidade_pedidos` INTEGER
-   `faturamento` NUMERIC(14,2)
-   `ticket_medio` NUMERIC(14,2)
-   `quantidade_itens` NUMERIC(14,3)
-   `categorias_distintas` INTEGER
-   `margem_total` NUMERIC(14,2)

Chave única: (`id_cliente`, `mes_referencia`).

#### `ml_cliente_snapshot`

Fotografia do comportamento de cada cliente em uma data de referência.
Deve conter `id_cliente`, `data_referencia`, features calculadas somente
com dados disponíveis até aquela data, labels futuros e versão do
conjunto de features.

Campos possíveis:

-   `id_cliente`
-   `data_referencia`
-   `recency_days`
-   `frequency_30d`
-   `frequency_90d`
-   `frequency_180d`
-   `revenue_30d`
-   `revenue_90d`
-   `revenue_180d`
-   `revenue_365d`
-   `avg_ticket_90d`
-   `revenue_variation_90d`
-   `frequency_variation_90d`
-   `avg_days_between_orders`
-   `category_diversity`
-   `avg_payment_delay`
-   `late_payment_rate`
-   `returns_rate` (se houver geração de devoluções)
-   `churn_label_90d`
-   `future_revenue_90d`
-   `feature_version`

Os campos de label são alvos de treinamento e nunca podem entrar nas
features.

### Regras de integridade dos dados

-   Todas as chaves estrangeiras devem ser válidas.
-   Datas de pagamento não podem anteceder a emissão.
-   Valores financeiros devem ser coerentes e não negativos, salvo casos
    explicitamente simulados.
-   O faturamento agregado deve reconciliar com a tabela de vendas.
-   O histórico deve cobrir 36 meses completos.
-   Utilizar uma seed fixa configurável para reproduzir a geração.
-   Criar scripts idempotentes ou documentar claramente como limpar e
    regenerar a base.

------------------------------------------------------------------------

## 5. Definições dos problemas de Machine Learning

### 5.1 Customer Segmentation

**Tipo:** aprendizado não supervisionado.\
**Modelo inicial:** K-Means.\
**Objetivo:** descobrir grupos de clientes com comportamento semelhante.

Features candidatas:

-   Recência.
-   Frequência de compras.
-   Valor monetário.
-   Ticket médio.
-   Diversidade de categorias.
-   Margem.
-   Regularidade de compras.

Pipeline:

1.  Selecionar features.
2.  Tratar ausentes e outliers.
3.  Aplicar transformação logarítmica quando a distribuição justificar.
4.  Escalar as variáveis.
5.  Testar diferentes valores de K.
6.  Avaliar Silhouette Score e tamanho dos clusters.
7.  Perfilar os clusters e atribuir rótulos comerciais interpretáveis.

Não fixar antecipadamente o número de clusters. Escolher com base em
métricas e interpretação de negócio. Persistir scaler, modelo,
parâmetros e perfil dos clusters.

### 5.2 Churn Prediction

**Tipo:** aprendizado supervisionado binário.\
**Modelos candidatos:** Regressão Logística (baseline), Random Forest e
XGBoost.

**Definição inicial de churn:** cliente que, após uma data de
referência, permanece 90 dias consecutivos sem comprar, desde que tenha
histórico mínimo suficiente para ser considerado cliente ativo.

A definição deve ser implementada sem olhar para o futuro ao construir
as features.

**Construção temporal:**

-   Data de referência: instante em que a previsão seria feita.
-   Features: somente dados disponíveis até a data de referência.
-   Janela de resultado: 90 dias seguintes.
-   Label: indica se o cliente atende à definição de churn nessa janela.

Criar snapshots em múltiplas datas históricas. Evitar criar linhas de
treinamento sem janela futura completa.

Features candidatas:

-   `recency_days`
-   `frequency_30d`, `frequency_90d`, `frequency_180d`
-   `revenue_90d`, `revenue_180d`
-   `revenue_variation_90d`
-   `frequency_variation_90d`
-   `avg_days_between_orders`
-   `category_diversity`
-   `avg_payment_delay`
-   `late_payment_rate`
-   `avg_ticket_90d`

Métricas:

-   Precision
-   Recall
-   F1-score
-   PR-AUC
-   ROC-AUC
-   Matriz de confusão
-   Calibração das probabilidades

A métrica principal deve considerar o custo comercial dos falsos
negativos e falsos positivos. Não usar acurácia isoladamente.

A probabilidade exibida deve ser identificada como estimativa do modelo.
Definir faixas de risco com base em validação e critérios de negócio,
não por limites arbitrários apresentados como cientificamente
comprovados.

### 5.3 Growth Prediction

**Tipo:** regressão supervisionada.\
**Target:** faturamento do cliente nos 90 dias posteriores à data de
referência.\
**Modelos candidatos:** Regressão Linear (baseline), Random Forest
Regressor e XGBoost Regressor.

Features candidatas:

-   Histórico de faturamento em janelas de 30, 90, 180 e 365 dias.
-   Frequência de compras.
-   Ticket médio.
-   Tendência de faturamento.
-   Diversidade de categorias.
-   Regularidade de compras.
-   Sazonalidade.
-   Margem histórica.

Métricas:

-   MAE
-   RMSE
-   R²
-   WAPE ou outra métrica percentual adequada, tratando corretamente
    valores zero ou próximos de zero.

Calcular potencial de crescimento comparando a previsão com uma
referência histórica definida e documentada. Não confundir previsão de
faturamento com oportunidade incremental comprovada.

------------------------------------------------------------------------

## 6. Estratégia de validação e prevenção de vazamento

Como os dados são temporais, utilizar divisão cronológica.

Exemplo inicial, a ajustar conforme o desenho dos snapshots e a janela
de 90 dias:

-   Treinamento: períodos históricos mais antigos.
-   Validação: período posterior ao treinamento.
-   Teste: período mais recente, nunca utilizado na seleção de modelos.

Requisitos:

1.  Features de uma linha só podem usar informações disponíveis até sua
    data de referência.
2.  Labels usam exclusivamente a janela futura definida.
3.  Garantir que as janelas dos labels não ultrapassem indevidamente os
    limites entre treino, validação e teste.
4.  Usar validação temporal progressiva quando viável.
5.  Ajustar scalers, imputadores e seleção de features apenas no
    conjunto de treino.
6.  Não usar identificadores ou rótulos artificiais do gerador como
    features.
7.  Registrar a data de corte, a definição do target e a versão do
    dataset em cada experimento.

Os resultados devem ser reproduzíveis e calculados sobre dados não
vistos durante o treinamento.

------------------------------------------------------------------------

## 7. Explicabilidade

Utilizar SHAP para explicar previsões individuais e o comportamento
geral dos modelos compatíveis.

Na tela do cliente, apresentar:

-   Probabilidade estimada de churn.
-   Principais fatores que elevaram o risco.
-   Principais fatores que reduziram o risco.
-   Previsão de faturamento futuro.
-   Comparação com histórico.
-   Data de referência da previsão.
-   Versão do modelo.

As explicações devem ser descritas como fatores que influenciaram a
previsão, não como causas comprovadas do comportamento do cliente.

Não apresentar recomendações comerciais como garantias de recuperação,
crescimento ou conversão.

------------------------------------------------------------------------

## 8. Arquitetura técnica

Arquitetura inicial modular:

1.  **Data Layer:** PostgreSQL.
2.  **Data Engineering:** Python, Pandas e SQL.
3.  **ML Layer:** Scikit-learn, XGBoost e SHAP.
4.  **Model Registry / Experiments:** MLflow, se viável no ambiente.
5.  **API:** FastAPI.
6.  **Frontend / Dashboard:** Streamlit para o MVP.
7.  **Orquestração inicial:** scripts Python executados manualmente ou
    por comandos documentados.

Fluxo:

`Dados sintéticos → PostgreSQL → Feature Engineering → Treinamento/Avaliação → Modelos persistidos → FastAPI → Streamlit`

O frontend não deve treinar modelos durante a navegação. O treinamento
será executado em scripts separados. A API deve carregar artefatos
treinados e servir previsões.

### Tecnologias

-   Python 3.12.
-   PostgreSQL 16.
-   Pandas.
-   NumPy.
-   Scikit-learn.
-   XGBoost.
-   SHAP.
-   FastAPI.
-   Streamlit.
-   SQLAlchemy ou psycopg.
-   MLflow (opcional no primeiro ciclo).
-   Pytest.

Usar versões compatíveis e fixadas no arquivo de dependências. Não
assumir que versões futuras são compatíveis sem teste.

------------------------------------------------------------------------

## 9. Estrutura inicial do repositório

``` text
cycle-ai/
├── app/
│   ├── main.py
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── segmentation.py
│   │   ├── churn.py
│   │   ├── growth.py
│   │   └── customers.py
│   └── components/
│       ├── charts.py
│       ├── metrics.py
│       └── customer_card.py
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── customers.py
│   │   ├── predictions.py
│   │   └── models.py
│   └── services/
│       └── prediction_service.py
├── data/
│   ├── generators/
│   │   ├── customers.py
│   │   ├── products.py
│   │   ├── sales.py
│   │   └── payments.py
│   └── processed/
├── ml/
│   ├── features/
│   │   ├── customer_features.py
│   │   └── snapshots.py
│   ├── segmentation/
│   │   └── train.py
│   ├── churn/
│   │   ├── train.py
│   │   └── predict.py
│   ├── growth/
│   │   ├── train.py
│   │   └── predict.py
│   └── evaluation/
│       └── metrics.py
├── database/
│   ├── connection.py
│   └── schema.sql
├── models/
│   ├── segmentation/
│   ├── churn/
│   └── growth/
├── experiments/
├── tests/
├── scripts/
│   ├── generate_data.py
│   ├── load_data.py
│   └── train_all.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── README.md
└── context.md
```

------------------------------------------------------------------------

## 10. API prevista

Criar endpoints REST documentados automaticamente pelo FastAPI.

  Método   Endpoint                      Objetivo
  -------- ----------------------------- -----------------------------------
  GET      `/api/health`                 Saúde da API
  GET      `/api/dashboard`              KPIs executivos
  GET      `/api/customers`              Listagem e filtros
  GET      `/api/customers/{id}`         Detalhes do cliente
  GET      `/api/segmentation`           Distribuição e perfis de clusters
  GET      `/api/churn/ranking`          Ranking de risco
  POST     `/api/churn/predict`          Gerar previsão de churn
  GET      `/api/growth/opportunities`   Ranking de potencial
  POST     `/api/growth/predict`         Previsão de faturamento
  GET      `/api/models/metrics`         Métricas e versões dos modelos

Usar paginação e filtros na listagem de clientes. Validar parâmetros e
retornar erros consistentes. Não expor caminhos internos de arquivos ou
detalhes sensíveis da infraestrutura.

------------------------------------------------------------------------

## 11. Experiência visual e identidade

### Direção de design

-   Nome visível: CYCLE AI.
-   Aparência: SaaS B2B moderno e profissional.
-   Idioma: português brasileiro.
-   Preferência visual: Enterprise, com azul-marinho, grafite e azul
    como cor de destaque.
-   Sidebar para navegação.
-   Cards executivos com números claros.
-   Gráficos limpos e sem excesso de elementos.
-   Tabelas com busca, ordenação e filtros.
-   Layout responsivo para desktop e tablet.
-   Estados de carregamento, vazio e erro.
-   Datas no formato `dd/mm/aaaa`.
-   Valores monetários em Real brasileiro (`R$`).

### Navegação

1.  Visão Executiva.
2.  Segmentação.
3.  Risco de Churn.
4.  Oportunidades de Crescimento.
5.  Clientes (Customer 360).
6.  Modelos e Métricas.

### Visão Executiva

Apresentar:

-   Total de clientes analisados.
-   Distribuição por segmento.
-   Quantidade e percentual de clientes em risco.
-   Quantidade de clientes com potencial de crescimento.
-   Faturamento histórico.
-   Faturamento futuro estimado.
-   Evolução temporal dos principais indicadores.

### Segmentação

Apresentar:

-   Quantidade de clusters.
-   Distribuição dos clientes.
-   Visualização bidimensional dos grupos.
-   Perfil médio de cada cluster.
-   Filtros por filial, região e segmento.

### Churn

Apresentar:

-   Ranking de clientes por probabilidade estimada.
-   Faixas de risco.
-   Principais fatores de influência.
-   Filtros e busca.
-   Detalhes do cliente.

### Growth

Apresentar:

-   Clientes com maior faturamento previsto.
-   Comparação entre histórico e previsão.
-   Variação percentual estimada.
-   Oportunidades por filial e segmento.

### Customer 360

Apresentar:

-   Perfil e cadastro fictício.
-   Histórico de faturamento.
-   Frequência de compras.
-   Segmento identificado.
-   Probabilidade estimada de churn.
-   Faturamento previsto.
-   Explicações dos modelos.
-   Data da última atualização.

### Demonstração guiada

Criar uma experiência de apresentação que permita navegar pelos módulos
e mostrar um cenário de exemplo. O cenário guiado deve ser claramente
identificado como demonstrativo e usar resultados efetivamente gerados
pelos modelos sempre que a integração estiver concluída.

------------------------------------------------------------------------

## 12. Indicadores e resultados

Separar três tipos de informação:

### Indicadores observados

Calculados diretamente das transações sintéticas, como faturamento
histórico e quantidade de clientes.

### Indicadores preditivos

Calculados pelos modelos, como probabilidade de churn e faturamento
futuro estimado.

### Indicadores de avaliação

Calculados durante a validação, como F1, PR-AUC, MAE e Silhouette Score.

Nunca misturar essas categorias. Exibir a origem, o período e a data de
atualização de cada indicador.

------------------------------------------------------------------------

## 13. Segurança e qualidade

Mesmo sendo um projeto demonstrativo:

-   Não armazenar credenciais no código.
-   Utilizar `.env` e disponibilizar `.env.example` sem segredos.
-   Validar entradas da API.
-   Usar consultas parametrizadas.
-   Evitar expor dados de conexão no frontend.
-   Não incluir dados pessoais reais na geração sintética.
-   Criar testes para funções de features, labels, modelos e endpoints.
-   Registrar logs sem informações sensíveis.
-   Documentar como reiniciar e regenerar o ambiente.

------------------------------------------------------------------------

## 14. Roadmap de implementação

### Fase 1 --- Data Foundation

-   Criar estrutura do repositório.
-   Configurar PostgreSQL.
-   Criar DDL.
-   Implementar geradores sintéticos.
-   Popular clientes, produtos, vendas e pagamentos.
-   Validar consistência dos dados.
-   Criar snapshots históricos.

**Critério de conclusão:** banco populado e dados reconciliados, com
geração reproduzível.

### Fase 2 --- Machine Learning

-   Implementar feature engineering.
-   Criar modelo de segmentação.
-   Criar modelo de churn.
-   Criar modelo de growth.
-   Comparar algoritmos baseline e candidatos.
-   Avaliar com divisão temporal.
-   Implementar explicabilidade.
-   Salvar modelos e métricas.

**Critério de conclusão:** três modelos treinados, avaliados e
reproduzíveis.

### Fase 3 --- Backend e interface

-   Implementar FastAPI.
-   Criar endpoints.
-   Conectar PostgreSQL.
-   Criar dashboard Streamlit.
-   Implementar módulos e filtros.
-   Integrar resultados reais dos modelos.

**Critério de conclusão:** interface consulta API e apresenta resultados
do banco e dos modelos.

### Fase 4 --- Qualidade e apresentação

-   Testar o fluxo completo.
-   Validar métricas e previsões.
-   Revisar experiência visual.
-   Criar roteiro de demonstração.
-   Documentar limitações.
-   Preparar pitch.

**Critério de conclusão:** demonstração estável e coerente, sem números
inventados como resultados reais.

------------------------------------------------------------------------

## 15. Instruções de trabalho para o Antigravity

O agente de desenvolvimento deve seguir estas regras:

1.  Ler este `context.md` antes de propor alterações.
2.  Tratar este documento como fonte de verdade do produto.
3.  Implementar em etapas pequenas e verificáveis.
4.  Não tentar criar todo o sistema em uma única geração.
5.  Antes de alterar a arquitetura, explicar a necessidade e o impacto.
6.  Manter separação entre interface, API, banco, preparação de dados e
    modelos.
7.  Não criar dados fictícios diretamente no dashboard para simular
    integração concluída.
8.  Quando ainda não houver modelo treinado, apresentar estado vazio ou
    modo demonstrativo claramente identificado.
9.  Não inventar métricas de desempenho.
10. Criar testes e executar os testes relevantes após cada etapa.
11. Atualizar README e documentação quando houver mudança na execução.
12. Manter nomes de tabelas, campos, rotas e arquivos consistentes.
13. Priorizar legibilidade, simplicidade e reprodutibilidade.
14. Não adicionar LLM ou funcionalidades generativas ao núcleo do MVP: o
    diferencial inicial é Machine Learning preditivo.
15. Ao concluir cada fase, informar arquivos criados, decisões tomadas,
    comandos executados, testes realizados e pendências.

### Primeira tarefa do agente

Começar exclusivamente pela **Fase 1 --- Data Foundation**.

Ordem sugerida:

1.  Inspecionar o ambiente e confirmar Python, PostgreSQL e Docker
    disponíveis.
2.  Criar a estrutura inicial do repositório.
3.  Criar `requirements.txt` e `.env.example`.
4.  Criar `docker-compose.yml` para PostgreSQL, se Docker for o ambiente
    escolhido.
5.  Criar `database/schema.sql`.
6.  Implementar geradores sintéticos parametrizáveis e com seed fixa.
7.  Implementar carga no PostgreSQL.
8.  Criar consultas de validação e reconciliação.
9.  Documentar comandos de execução.
10. Executar e relatar os testes.

Não iniciar os modelos nem o dashboard antes de validar a base de dados.

------------------------------------------------------------------------

## 16. Critérios de aceite do MVP

O MVP será considerado pronto quando:

-   [ ] A base sintética puder ser recriada com seed fixa.
-   [ ] O PostgreSQL estiver populado e consistente.
-   [ ] Os snapshots históricos forem criados sem vazamento temporal.
-   [ ] O modelo de segmentação produzir clusters interpretáveis.
-   [ ] O modelo de churn produzir probabilidades e métricas de teste.
-   [ ] O modelo de growth produzir previsões e métricas de teste.
-   [ ] Os modelos tiverem artefatos persistidos e versão identificável.
-   [ ] A API disponibilizar os resultados.
-   [ ] O dashboard consumir os dados reais da API.
-   [ ] O usuário conseguir navegar pelos cinco principais módulos.
-   [ ] A explicabilidade estiver disponível para previsões de churn.
-   [ ] A interface distinguir dados observados, previsões e métricas de
    avaliação.
-   [ ] O README permitir que outra pessoa execute o projeto.
-   [ ] A demonstração não apresentar resultados inventados como
    resultados reais.

## 17. Narrativa para o pitch acadêmico

**Problema:** empresas possuem grandes volumes de dados comerciais, mas
ainda têm dificuldade para antecipar mudanças no comportamento dos
clientes.

**Solução:** CYCLE AI, uma plataforma de inteligência comercial que
utiliza Machine Learning para segmentar clientes, prever abandono e
identificar potencial de crescimento.

**Tecnologia:** aprendizado não supervisionado, modelos supervisionados
de classificação e regressão, engenharia de atributos e explicabilidade.

**Impacto esperado:** apoiar a priorização comercial, antecipar riscos e
identificar oportunidades de receita.

**Modelo de negócio:** SaaS B2B integrado a ERPs e sistemas comerciais.

**Evolução:** integração com sistemas reais, testes de efetividade das
ações comerciais, recomendação de produtos e modelos de uplift.

### Frase de encerramento

> CYCLE AI: não basta conhecer o histórico dos seus clientes. É preciso
> antecipar o próximo ciclo do relacionamento comercial.
